"""
SquadSync Permission System
Strict hierarchical permission checks with downward-only access flow.

Permission Rules:
- Organization Admin: Full access to all teams, squads, and players under their org
- Team Manager: Access to their assigned teams and all squads under those teams
- Squad Leader: Access only to their assigned squads
- Player: Access only to own profile, squads they belong to, and their vault
"""

from uuid import UUID

from sqlalchemy import and_, select, union_all
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from backend.models.models import (
    Organization,
    OrganizationAdmin,
    PlayerVault,
    Squad,
    SquadLeader,
    Team,
    TeamManager,
    User,
    squad_membership_table,
)


async def can_access_organization(
    db: AsyncSession,
    user: User,
    organization_id: UUID,
) -> bool:
    """
    Check if user can access an organization.

    Rules:
    - Organization Admin can access if they are admin of this organization
    - Others cannot access organizations directly

    Args:
        db: Database session
        user: User object to check permissions for
        organization_id: UUID of organization to check access to

    Returns:
        True if user has access, False otherwise
    """
    if not user or not user.is_active:
        return False

    # Check if user is an organization admin for this specific organization
    stmt = (
        select(OrganizationAdmin)
        .where(
            and_(
                OrganizationAdmin.organization_id == organization_id,
                OrganizationAdmin.user_id == user.id,
            )
        )
        .limit(1)
    )
    result = await db.execute(stmt)
    org_admin = result.scalar_one_or_none()

    return org_admin is not None


async def can_access_team(
    db: AsyncSession,
    user: User,
    team_id: UUID,
    load_relationships: bool = False,
) -> bool:
    """
    Check if user can access a team.

    Rules:
    - Organization Admin can access if team belongs to any org they administer
    - Team Manager can access if they are manager of this specific team
    - Others cannot access teams directly

    Args:
        db: Database session
        user: User object to check permissions for
        team_id: UUID of team to check access to
        load_relationships: If True, eagerly load relationships for efficiency

    Returns:
        True if user has access, False otherwise
    """
    if not user or not user.is_active:
        return False

    # Check if user is organization admin for the organization that owns this team
    org_admin_stmt = (
        select(OrganizationAdmin.organization_id)
        .join(Team, OrganizationAdmin.organization_id == Team.organization_id)
        .where(
            and_(
                Team.id == team_id,
                OrganizationAdmin.user_id == user.id,
            )
        )
        .limit(1)
    )
    result = await db.execute(org_admin_stmt)
    if result.scalar_one_or_none() is not None:
        return True

    # Check if user is team manager for this specific team
    team_manager_stmt = (
        select(TeamManager)
        .where(
            and_(
                TeamManager.team_id == team_id,
                TeamManager.user_id == user.id,
            )
        )
        .limit(1)
    )
    result = await db.execute(team_manager_stmt)
    team_manager = result.scalar_one_or_none()

    return team_manager is not None


async def can_access_squad(
    db: AsyncSession,
    user: User,
    squad_id: UUID,
    load_relationships: bool = False,
) -> bool:
    """
    Check if user can access a squad.

    Rules:
    - Organization Admin can access if squad belongs to any org they administer
    - Team Manager can access if squad belongs to any team they manage
    - Squad Leader can access if they are leader of this specific squad
    - Player can access if they are a member of this squad

    Args:
        db: Database session
        user: User object to check permissions for
        squad_id: UUID of squad to check access to
        load_relationships: If True, eagerly load relationships for efficiency

    Returns:
        True if user has access, False otherwise
    """
    if not user or not user.is_active:
        return False

    # Build base query to get squad with its team and organization relationships
    if load_relationships:
        squad_stmt = (
            select(Squad)
            .options(
                selectinload(Squad.team).selectinload(Team.organization),
                selectinload(Squad.squad_leaders),
                selectinload(Squad.members),
            )
            .where(Squad.id == squad_id)
        )
    else:
        squad_stmt = select(Squad).where(Squad.id == squad_id)

    result = await db.execute(squad_stmt)
    squad = result.scalar_one_or_none()

    if not squad:
        return False

    # Check Organization Admin: Can access any squad under their orgs
    org_admin_stmt = (
        select(OrganizationAdmin)
        .join(Team, OrganizationAdmin.organization_id == Team.organization_id)
        .join(Squad, Team.id == Squad.team_id)
        .where(
            and_(
                Squad.id == squad_id,
                OrganizationAdmin.user_id == user.id,
            )
        )
        .limit(1)
    )
    result = await db.execute(org_admin_stmt)
    if result.scalar_one_or_none() is not None:
        return True

    # Check Team Manager: Can access squads under their teams
    team_manager_stmt = (
        select(TeamManager)
        .join(Squad, TeamManager.team_id == Squad.team_id)
        .where(
            and_(
                Squad.id == squad_id,
                TeamManager.user_id == user.id,
            )
        )
        .limit(1)
    )
    result = await db.execute(team_manager_stmt)
    if result.scalar_one_or_none() is not None:
        return True

    # Check Squad Leader: Can access their assigned squads
    squad_leader_stmt = (
        select(SquadLeader)
        .where(
            and_(
                SquadLeader.squad_id == squad_id,
                SquadLeader.user_id == user.id,
            )
        )
        .limit(1)
    )
    result = await db.execute(squad_leader_stmt)
    if result.scalar_one_or_none() is not None:
        return True

    # Check Player: Can access squads they are members of
    # Use direct query to squad_membership_table
    member_stmt = (
        select(squad_membership_table)
        .where(
            and_(
                squad_membership_table.c.squad_id == squad_id,
                squad_membership_table.c.user_id == user.id,
                squad_membership_table.c.is_active == True,
            )
        )
        .limit(1)
    )
    result = await db.execute(member_stmt)
    if result.first() is not None:
        return True

    return False


async def can_access_user_profile(
    db: AsyncSession,
    requesting_user: User,
    target_user_id: UUID,
) -> bool:
    """
    Check if requesting user can access target user's profile.

    Rules:
    - Users can always access their own profile
    - Organization Admin can access profiles of users in their orgs
    - Team Manager can access profiles of users in their teams
    - Squad Leader can access profiles of users in their squads
    - Players can only access their own profile

    Args:
        db: Database session
        requesting_user: User requesting access
        target_user_id: UUID of user profile being accessed

    Returns:
        True if user has access, False otherwise
    """
    if not requesting_user or not requesting_user.is_active:
        return False

    # Users can always access their own profile
    if requesting_user.id == target_user_id:
        return True

    # Check if requesting user is organization admin for any org that contains the target user
    # A user is "in an org" if they are admin, manager, leader, or member of squads in that org
    org_admin_stmt = (
        select(OrganizationAdmin)
        .join(Team, OrganizationAdmin.organization_id == Team.organization_id)
        .join(Squad, Team.id == Squad.team_id)
        .join(
            squad_membership_table,
            Squad.id == squad_membership_table.c.squad_id,
        )
        .where(
            and_(
                squad_membership_table.c.user_id == target_user_id,
                squad_membership_table.c.is_active == True,
                OrganizationAdmin.user_id == requesting_user.id,
            )
        )
        .limit(1)
    )
    result = await db.execute(org_admin_stmt)
    if result.scalar_one_or_none() is not None:
        return True

    # Also check if target user is admin/manager/leader in the same org
    org_admin_same_org_stmt = (
        select(OrganizationAdmin)
        .where(
            and_(
                OrganizationAdmin.user_id == target_user_id,
                OrganizationAdmin.organization_id.in_(
                    select(OrganizationAdmin.organization_id).where(
                        OrganizationAdmin.user_id == requesting_user.id
                    )
                ),
            )
        )
        .limit(1)
    )
    result = await db.execute(org_admin_same_org_stmt)
    if result.scalar_one_or_none() is not None:
        return True

    # Check if requesting user is team manager for teams that contain the target user
    team_manager_stmt = (
        select(TeamManager)
        .join(Squad, TeamManager.team_id == Squad.team_id)
        .join(
            squad_membership_table,
            Squad.id == squad_membership_table.c.squad_id,
        )
        .where(
            and_(
                squad_membership_table.c.user_id == target_user_id,
                squad_membership_table.c.is_active == True,
                TeamManager.user_id == requesting_user.id,
            )
        )
        .limit(1)
    )
    result = await db.execute(team_manager_stmt)
    if result.scalar_one_or_none() is not None:
        return True

    # Check if requesting user is squad leader for squads that contain the target user
    squad_leader_stmt = (
        select(SquadLeader)
        .join(
            squad_membership_table,
            SquadLeader.squad_id == squad_membership_table.c.squad_id,
        )
        .where(
            and_(
                squad_membership_table.c.user_id == target_user_id,
                squad_membership_table.c.is_active == True,
                SquadLeader.user_id == requesting_user.id,
            )
        )
        .limit(1)
    )
    result = await db.execute(squad_leader_stmt)
    if result.scalar_one_or_none() is not None:
        return True

    # Players can only access their own profile
    return False


async def can_access_player_vault(
    db: AsyncSession,
    requesting_user: User,
    vault_user_id: UUID,
) -> bool:
    """
    Check if requesting user can access a player vault.

    Rules:
    - Users can ONLY access their own vault
    - No exceptions, even for admins

    Args:
        db: Database session
        requesting_user: User requesting access
        vault_user_id: UUID of user whose vault is being accessed

    Returns:
        True if user has access (only if it's their own vault), False otherwise
    """
    if not requesting_user or not requesting_user.is_active:
        return False

    # Strict rule: Users can ONLY access their own vault
    return requesting_user.id == vault_user_id


async def can_manage_squad(
    db: AsyncSession,
    user: User,
    squad_id: UUID,
) -> bool:
    """
    Check if user can manage (create, update, delete) a squad.

    Rules:
    - Organization Admin can manage squads in their orgs
    - Team Manager can manage squads in their teams
    - Squad Leader can manage their assigned squads
    - Players cannot manage squads

    Args:
        db: Database session
        user: User object to check permissions for
        squad_id: UUID of squad to check management rights for

    Returns:
        True if user can manage the squad, False otherwise
    """
    if not user or not user.is_active:
        return False

    # Organization Admin can manage squads in their orgs
    org_admin_stmt = (
        select(OrganizationAdmin)
        .join(Team, OrganizationAdmin.organization_id == Team.organization_id)
        .join(Squad, Team.id == Squad.team_id)
        .where(
            and_(
                Squad.id == squad_id,
                OrganizationAdmin.user_id == user.id,
            )
        )
        .limit(1)
    )
    result = await db.execute(org_admin_stmt)
    if result.scalar_one_or_none() is not None:
        return True

    # Team Manager can manage squads in their teams
    team_manager_stmt = (
        select(TeamManager)
        .join(Squad, TeamManager.team_id == Squad.team_id)
        .where(
            and_(
                Squad.id == squad_id,
                TeamManager.user_id == user.id,
            )
        )
        .limit(1)
    )
    result = await db.execute(team_manager_stmt)
    if result.scalar_one_or_none() is not None:
        return True

    # Squad Leader can manage their assigned squads
    squad_leader_stmt = (
        select(SquadLeader)
        .where(
            and_(
                SquadLeader.squad_id == squad_id,
                SquadLeader.user_id == user.id,
            )
        )
        .limit(1)
    )
    result = await db.execute(squad_leader_stmt)
    if result.scalar_one_or_none() is not None:
        return True

    return False


async def can_create_summon(
    db: AsyncSession,
    user: User,
    squad_id: UUID,
) -> bool:
    """
    Check if user can create a summon in a squad.

    Rules:
    - Organization Admin can create summons in squads under their orgs
    - Team Manager can create summons in squads under their teams
    - Squad Leader can create summons in their squads
    - Players cannot create summons

    Args:
        db: Database session
        user: User object to check permissions for
        squad_id: UUID of squad where summon would be created

    Returns:
        True if user can create a summon, False otherwise
    """
    # Creating a summon requires management permissions
    return await can_manage_squad(db, user, squad_id)


async def get_user_accessible_organizations(
    db: AsyncSession,
    user: User,
) -> list[UUID]:
    """
    Get list of organization IDs that the user can access.

    Args:
        db: Database session
        user: User object

    Returns:
        List of organization UUIDs the user can access
    """
    if not user or not user.is_active:
        return []

    stmt = select(OrganizationAdmin.organization_id).where(
        OrganizationAdmin.user_id == user.id
    )
    result = await db.execute(stmt)
    return [row[0] for row in result.all()]


async def get_user_accessible_teams(
    db: AsyncSession,
    user: User,
) -> list[UUID]:
    """
    Get list of team IDs that the user can access.

    Args:
        db: Database session
        user: User object

    Returns:
        List of team UUIDs the user can access (via org admin or team manager roles)
    """
    if not user or not user.is_active:
        return []

    # Get teams where user is organization admin
    org_admin_teams_stmt = (
        select(Team.id)
        .join(OrganizationAdmin, Team.organization_id == OrganizationAdmin.organization_id)
        .where(OrganizationAdmin.user_id == user.id)
    )

    # Get teams where user is team manager
    team_manager_teams_stmt = select(TeamManager.team_id).where(
        TeamManager.user_id == user.id
    )

    # Union the results
    combined_stmt = union_all(org_admin_teams_stmt, team_manager_teams_stmt)
    result = await db.execute(combined_stmt)

    # Convert to set to remove duplicates, then back to list
    team_ids = set(row[0] for row in result.all())
    return list(team_ids)


async def get_user_accessible_squads(
    db: AsyncSession,
    user: User,
) -> list[UUID]:
    """
    Get list of squad IDs that the user can access.

    Args:
        db: Database session
        user: User object

    Returns:
        List of squad UUIDs the user can access (via any role or membership)
    """
    if not user or not user.is_active:
        return []

    # Get squads where user is organization admin (via org → team → squad)
    org_admin_squads_stmt = (
        select(Squad.id)
        .join(Team, Squad.team_id == Team.id)
        .join(OrganizationAdmin, Team.organization_id == OrganizationAdmin.organization_id)
        .where(OrganizationAdmin.user_id == user.id)
    )

    # Get squads where user is team manager
    team_manager_squads_stmt = (
        select(Squad.id)
        .join(TeamManager, Squad.team_id == TeamManager.team_id)
        .where(TeamManager.user_id == user.id)
    )

    # Get squads where user is squad leader
    squad_leader_squads_stmt = (
        select(SquadLeader.squad_id).where(SquadLeader.user_id == user.id)
    )

    # Get squads where user is a member
    member_squads_stmt = (
        select(squad_membership_table.c.squad_id)
        .where(
            and_(
                squad_membership_table.c.user_id == user.id,
                squad_membership_table.c.is_active == True,
            )
        )
    )

    # Union all results
    combined_stmt = union_all(
        org_admin_squads_stmt,
        team_manager_squads_stmt,
        squad_leader_squads_stmt,
        member_squads_stmt,
    )
    result = await db.execute(combined_stmt)

    # Convert to set to remove duplicates, then back to list
    squad_ids = set(row[0] for row in result.all())
    return list(squad_ids)
