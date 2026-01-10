"""
Player Vault API Router
Security-critical endpoints for private user data storage.
"""

from typing import Annotated, Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.api.schemas.vault_schemas import (
    VaultDataMergeRequest,
    VaultDataUpdateRequest,
    VaultDetail,
    VaultShareRequest,
)
from backend.core.dependencies import get_db, get_current_user
from backend.core.sanitization import sanitize_dict
from backend.models.models import User
from backend.services.vault_service import (
    PermissionDeniedError,
    VaultNotFoundError,
    VaultService,
    VaultServiceError,
)

router = APIRouter(prefix="/api/v1/vault", tags=["player-vault"])


@router.get(
    "/{user_id}",
    response_model=VaultDetail,
    status_code=status.HTTP_200_OK,
    summary="Get player vault",
    description="Get player vault data. Users can ONLY access their own vault.",
)
async def get_vault(
    user_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> VaultDetail:
    """
    Get player vault data.

    Security: Users can ONLY access their own vault.
    No exceptions, even for admins.
    """
    service = VaultService(db)

    try:
        vault = await service.get_vault(current_user, user_id)
        if not vault:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Vault for user {user_id} not found",
            )

        return VaultDetail(
            id=vault.id,
            user_id=vault.user_id,
            vault_data=vault.vault_data,
            created_at=vault.created_at,
            updated_at=vault.updated_at,
        )

    except PermissionDeniedError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        )
    except VaultServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.put(
    "/{user_id}",
    response_model=VaultDetail,
    status_code=status.HTTP_200_OK,
    summary="Update player vault",
    description="Update player vault data (full replacement). Users can ONLY update their own vault.",
)
async def update_vault(
    user_id: UUID,
    request: VaultDataUpdateRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> VaultDetail:
    """
    Update player vault data (full replacement).

    Security: Users can ONLY update their own vault.
    Data is sanitized before storage.
    """
    service = VaultService(db)

    try:
        # Sanitize input data
        sanitized_data = sanitize_dict(request.data, max_depth=10)

        vault = await service.update_vault_data(
            user=current_user,
            vault_user_id=user_id,
            data=sanitized_data,
        )

        await db.commit()

        return VaultDetail(
            id=vault.id,
            user_id=vault.user_id,
            vault_data=vault.vault_data,
            created_at=vault.created_at,
            updated_at=vault.updated_at,
        )

    except PermissionDeniedError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        )
    except VaultNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except VaultServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.patch(
    "/{user_id}",
    response_model=VaultDetail,
    status_code=status.HTTP_200_OK,
    summary="Merge player vault data",
    description="Merge player vault data (partial update). Users can ONLY update their own vault.",
)
async def merge_vault(
    user_id: UUID,
    request: VaultDataMergeRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> VaultDetail:
    """
    Merge player vault data (partial update).

    Security: Users can ONLY update their own vault.
    Data is sanitized before storage.
    """
    service = VaultService(db)

    try:
        # Sanitize input data
        sanitized_data = sanitize_dict(request.data, max_depth=10)

        vault = await service.merge_vault_data(
            user=current_user,
            vault_user_id=user_id,
            data=sanitized_data,
        )

        await db.commit()

        return VaultDetail(
            id=vault.id,
            user_id=vault.user_id,
            vault_data=vault.vault_data,
            created_at=vault.created_at,
            updated_at=vault.updated_at,
        )

    except PermissionDeniedError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        )
    except VaultNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except VaultServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post(
    "/{user_id}/share",
    status_code=status.HTTP_200_OK,
    summary="Share vault data to chat",
    description="Share vault data to a squad/team/chat. Requires explicit action. Users can ONLY share their own vault.",
)
async def share_vault(
    user_id: UUID,
    request: VaultShareRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> dict[str, Any]:
    """
    Share vault data to a chat/squad/team.

    Security: Users can ONLY share their own vault.
    Requires explicit action - vault is private by default.
    """
    service = VaultService(db)

    try:
        shared_data = await service.share_vault_to_chat(
            user=current_user,
            vault_user_id=user_id,
            target_id=request.target_id,
            target_type=request.target_type,
            data_keys=request.data_keys,
            message=request.message,
        )

        await db.commit()

        return {
            "message": "Vault data shared successfully",
            "target_id": str(request.target_id),
            "target_type": request.target_type,
            "data_keys": request.data_keys or list(shared_data.keys()),
        }

    except PermissionDeniedError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        )
    except VaultNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except VaultServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
