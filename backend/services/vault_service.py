"""
Player Vault Service
Security-critical service for private user data storage.
"""

from typing import Any, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.permissions import can_access_player_vault
from backend.core.redis_client import get_redis
from backend.models.models import PlayerVault, User


class VaultServiceError(Exception):
    """Base exception for vault service errors."""

    pass


class PermissionDeniedError(VaultServiceError):
    """Raised when user lacks required permissions."""

    pass


class VaultNotFoundError(VaultServiceError):
    """Raised when vault is not found."""

    pass


class VaultService:
    """Service for managing player vaults."""

    def __init__(self, db: AsyncSession):
        """
        Initialize vault service.

        Args:
            db: Database session
        """
        self.db = db

    async def get_vault(self, user: User, vault_user_id: UUID) -> Optional[PlayerVault]:
        """
        Get player vault by user ID.

        Security: Users can ONLY access their own vault.

        Args:
            user: Requesting user
            vault_user_id: UUID of user whose vault to access

        Returns:
            PlayerVault object if found and user has access, None otherwise

        Raises:
            PermissionDeniedError: If user cannot access the vault
        """
        # Strict permission check: users can only access their own vault
        can_access = await can_access_player_vault(self.db, user, vault_user_id)
        if not can_access:
            raise PermissionDeniedError(
                f"User {user.id} does not have permission to access vault for user {vault_user_id}"
            )

        # Get or create vault
        stmt = select(PlayerVault).where(PlayerVault.user_id == vault_user_id)
        result = await self.db.execute(stmt)
        vault = result.scalar_one_or_none()

        if not vault:
            # Create vault if it doesn't exist
            vault = PlayerVault(
                user_id=vault_user_id,
                vault_data={},
            )
            self.db.add(vault)
            await self.db.flush()
            await self.db.refresh(vault)

        return vault

    async def update_vault_data(
        self,
        user: User,
        vault_user_id: UUID,
        data: dict[str, Any],
    ) -> PlayerVault:
        """
        Update vault data (full replacement).

        Security: Users can ONLY update their own vault.

        Args:
            user: Requesting user
            vault_user_id: UUID of user whose vault to update
            data: New vault data (replaces existing)

        Returns:
            Updated PlayerVault object

        Raises:
            PermissionDeniedError: If user cannot access the vault
        """
        # Get vault with permission check
        vault = await self.get_vault(user, vault_user_id)
        if not vault:
            raise VaultNotFoundError(f"Vault for user {vault_user_id} not found")

        # Update data
        vault.vault_data = data
        await self.db.flush()
        await self.db.refresh(vault)

        # Publish audit event (no data, just metadata)
        redis = await get_redis()
        audit_data = {
            "event_type": "vault_updated",
            "user_id": str(user.id),
            "vault_user_id": str(vault_user_id),
            "timestamp": vault.updated_at.isoformat(),
        }
        await redis.publish(f"user:{user.id}:vault_audit", audit_data)

        return vault

    async def merge_vault_data(
        self,
        user: User,
        vault_user_id: UUID,
        data: dict[str, Any],
    ) -> PlayerVault:
        """
        Merge vault data (partial update).

        Security: Users can ONLY update their own vault.

        Args:
            user: Requesting user
            vault_user_id: UUID of user whose vault to update
            data: Data to merge (updates existing keys, adds new ones)

        Returns:
            Updated PlayerVault object

        Raises:
            PermissionDeniedError: If user cannot access the vault
        """
        # Get vault with permission check
        vault = await self.get_vault(user, vault_user_id)
        if not vault:
            raise VaultNotFoundError(f"Vault for user {vault_user_id} not found")

        # Merge data (deep merge for nested dicts)
        def deep_merge(base: dict, update: dict) -> dict:
            result = base.copy()
            for key, value in update.items():
                if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                    result[key] = deep_merge(result[key], value)
                else:
                    result[key] = value
            return result

        vault.vault_data = deep_merge(vault.vault_data, data)
        await self.db.flush()
        await self.db.refresh(vault)

        # Publish audit event
        redis = await get_redis()
        audit_data = {
            "event_type": "vault_merged",
            "user_id": str(user.id),
            "vault_user_id": str(vault_user_id),
            "updated_keys": list(data.keys()),
            "timestamp": vault.updated_at.isoformat(),
        }
        await redis.publish(f"user:{user.id}:vault_audit", audit_data)

        return vault

    async def share_vault_to_chat(
        self,
        user: User,
        vault_user_id: UUID,
        target_id: UUID,
        target_type: str,
        data_keys: Optional[list[str]] = None,
        message: Optional[str] = None,
    ) -> dict[str, Any]:
        """
        Share vault data to a chat/squad/team.

        Security: Users can ONLY share their own vault.
        Requires explicit action - vault is private by default.

        Args:
            user: Requesting user
            vault_user_id: UUID of user whose vault to share
            target_id: Target chat/squad/team ID
            target_type: Target type ('squad', 'team', or 'chat')
            data_keys: Specific keys to share (if None, shares all)
            message: Optional message to accompany shared data

        Returns:
            Dictionary with shared data

        Raises:
            PermissionDeniedError: If user cannot access the vault
        """
        # Get vault with permission check
        vault = await self.get_vault(user, vault_user_id)
        if not vault:
            raise VaultNotFoundError(f"Vault for user {vault_user_id} not found")

        # Extract data to share
        if data_keys:
            shared_data = {key: vault.vault_data.get(key) for key in data_keys if key in vault.vault_data}
        else:
            shared_data = vault.vault_data.copy()

        # Publish share event to target channel
        redis = await get_redis()
        share_data = {
            "event_type": "vault_shared",
            "user_id": str(user.id),
            "username": user.username,
            "vault_user_id": str(vault_user_id),
            "target_id": str(target_id),
            "target_type": target_type,
            "data_keys": data_keys or list(shared_data.keys()),
            "message": message,
            "data": shared_data,
        }

        # Publish to appropriate channel
        if target_type == "squad":
            channel = f"squad:{target_id}:chat"
        elif target_type == "team":
            channel = f"team:{target_id}:chat"
        else:  # chat
            channel = f"chat:{target_id}"

        await redis.publish(channel, share_data)

        # Publish audit event
        audit_data = {
            "event_type": "vault_shared",
            "user_id": str(user.id),
            "vault_user_id": str(vault_user_id),
            "target_id": str(target_id),
            "target_type": target_type,
            "data_keys": data_keys,
        }
        await redis.publish(f"user:{user.id}:vault_audit", audit_data)

        return shared_data
