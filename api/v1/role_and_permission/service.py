import math
from typing import Optional
from fastapi import HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, asc, Table
from sqlalchemy.orm import joinedload

from api.core.base.services import Service
from api.v1.auth.dependencies import verify_token
from api.v1.role_and_permission.model import (
    Role,
    Permission,
    role_permissions,
    user_roles,
)
from api.v1.role_and_permission.schema import (
    CreateRolesOutputSchema,
    CreateRoleSchema,
    RolePermissionBase,
    UpdateRolesOutputSchema,
    UpdateRoleSchema,
    RolesOutputSchema,
    PermissionBase,
)
from api.utils.task_logger import create_logger


logger = create_logger("Role Service")


class RoleService(Service):
    """
    Role service class.
    """

    def __init__(self, model) -> None:
        """
        Constructor
        """
        super().__init__(model)

    async def create_role_and_permission(
        self,
        schema: CreateRoleSchema,
        session: AsyncSession,
        request: Request,
        access_token: str,
    ) -> Optional[CreateRolesOutputSchema]:
        """
        Creates a new role and permission.

        Args:
            schema(pydantic model): object containing dicts for roles and permissions to create.
            session(AsynSession): database async session object.
            request(Request): request object.
            access_token(str): token to decode
        Returns:
            CreateRolesOutputSchema(pydantic model): Newly created roles and permissions.
        """
        claims = await verify_token(
            token=access_token, request=request, token_type="access"
        )
        claim_role = claims.get("role")
        if claim_role != "superadmin":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="You do not have enough permission to perform this action.",
            )

        if await self.fetch({"name": schema.name}, session):
            raise HTTPException(status_code=409, detail="role already exists.")
        for permission in schema.permissions:
            if await permission_service.fetch({"name": permission.name}, session):
                raise HTTPException(
                    status_code=409, detail="permission already exists."
                )
        role = await self.create(
            {"name": schema.name, "description": schema.description}, session=session
        )
        permissions = [
            await permission_service.create(
                {"name": permission.name, "description": permission.description},
                session,
            )
            for permission in schema.permissions
        ]

        _ = [
            await role_permission_service.insert_if_not_exists(
                session=session, role_id=role.id, permission_id=permission.id
            )
            for permission in permissions
        ]

        all_role_permissions = RolePermissionBase(
            id=role.id,
            name=role.name,
            description=role.description,
            created_at=role.created_at,
            updated_at=role.updated_at,
            permissions=[
                PermissionBase(
                    id=permission.id,
                    name=permission.name,
                    description=permission.description,
                    created_at=permission.created_at,
                    updated_at=permission.updated_at,
                )
                for permission in permissions
            ],
        )
        return CreateRolesOutputSchema(data=all_role_permissions)

    async def update_role(
        self,
        schema: UpdateRoleSchema,
        session: AsyncSession,
        request: Request,
        access_token: str,
        role_id: str,
    ) -> Optional[UpdateRolesOutputSchema]:
        """
        Updates a role.

        Args:
            schema(pydantic model): object containing dicts for roles and permissions to update.
            session(AsynSession): database async session object.
            request(Request): request object.
            access_token(str): token to decode.
            role_id(str): The is of the role to update.
        Returns:
            UpdateRolesOutputSchema(pydantic model): Newly updated roles and permissions.
        """
        claims = await verify_token(
            token=access_token, request=request, token_type="access"
        )
        claim_role = claims.get("role")
        if claim_role != "superadmin":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="You do not have enough permission to perform this action.",
            )
        role_exists = await self.fetch({"id": role_id}, session)
        if not role_exists:
            raise HTTPException(status_code=400, detail="role not found")
        role = await self.update(
            [{"id": role_id}, {"name": schema.name, "description": schema.description}],
            session=session,
        )
        permissions = [
            await permission_service.update(
                [
                    {"id": permission.id},
                    {"name": permission.name, "description": permission.description},
                ],
                session,
            )
            for permission in schema.permissions
        ]

        all_role_permissions = RolePermissionBase(
            id=role.id,
            name=role.name,
            description=role.description,
            created_at=role.created_at,
            updated_at=role.updated_at,
            permissions=[
                PermissionBase(
                    id=permission.id,
                    name=permission.name,
                    description=permission.description,
                    created_at=permission.created_at,
                    updated_at=permission.updated_at,
                )
                for permission in permissions
            ],
        )
        return UpdateRolesOutputSchema(data=all_role_permissions)

    async def retrieve_all_roles(
        self,
        params: dict,
        session: AsyncSession,
        request: Request,
        access_token: str,
    ) -> Optional[RolesOutputSchema]:
        """
        Retrieves all roles.

        Args:
            params(dict): dict containing pagination, sort, sort_order.
            session(AsynSession): database async session object.
            request(Request): request object.
            access_token(str): token to decode
        Returns:
            RolesOutputSchema(pydantic model): retrieved roles and permissions.
        """
        # authorize
        claims = await verify_token(
            token=access_token, request=request, token_type="access"
        )
        claim_role = claims.get("role")
        if claim_role != "superadmin" and claim_role != "admin":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="You do not have enough permission to perform this action.",
            )

        # validate and sort params
        try:
            params["page"] = int(params["page"])
        except (TypeError, ValueError):
            params["page"] = 1

        try:
            params["limit"] = int(params["limit"])
        except (TypeError, ValueError):
            params["limit"] = 10

        if not params["sort"] in ["created_at", "updated_at"]:
            params["sort"] = "created_at"

        if not params["sort_order"] in ["desc", "asc"]:
            params["sort_order"] = "desc"

        stmt = select(Role)
        if params["sort_order"] == "desc":
            stmt.order_by(desc(params["sort"]))

        if params["sort_order"] == "asc":
            stmt.order_by(asc(params["sort"]))

        # fetch roles and permissions
        params_copy = params.copy()
        stmt = (
            stmt.options(joinedload(Role.permissions))
            .limit(params["limit"])
            .offset((params["page"] - 1) * params["limit"])
        )
        result = await session.execute(stmt)

        roles = result.unique().scalars().all()

        all_roles = [
            RolePermissionBase(
                id=role.id,
                name=role.name,
                description=role.description,
                created_at=role.created_at,
                updated_at=role.updated_at,
                permissions=[
                    PermissionBase(
                        id=permission.id,
                        name=permission.name,
                        description=permission.description,
                        created_at=permission.created_at,
                        updated_at=permission.updated_at,
                    )
                    for permission in role.permissions
                    if permission != []
                ],
            )
            for role in roles
        ]

        total_items = await self.count(session)
        total_pages = 0
        if total_items > 0:
            total_pages = math.ceil(total_items / params_copy["limit"])

        return RolesOutputSchema(
            page=params_copy["page"],
            limit=params_copy["limit"],
            total_pages=total_pages,
            total_items=total_items,
            data=all_roles,
        )


class PermissionService(Service):
    """
    Permission service class.
    """

    def __init__(self, model) -> None:
        """
        Constructor
        """
        super().__init__(model)


class UserRolePermission:
    """
    Class service for user_role and role_permission
    """

    def __init__(self, table: Table) -> None:
        """
        Constructor.
        """
        self.table = table

    async def insert_if_not_exists(
        self,
        session: AsyncSession,
        role_id: str,
        user_id: str | None = None,
        permission_id: str | None = None,
    ):
        """
        Adds a role to a User, or adds a permission to a role.

        Args:
            session(AsyncSession): database async session object.
            role_id(str): role to insert.
            user_id(str): Optional, user_to insert if inserrting into user_roles.
            permission_id(str): optional, permission to insert, if inserting into role_permission.
        Returns:
            None.
        Raise:
            ValueError: If Neither user_id nor permission_id is missing.
        """
        if not user_id and not permission_id:
            raise ValueError("must pass either user_id or permission_id")
        stmt = self.table.select()

        if user_id:
            stmt = stmt.where(
                self.table.c.user_id == user_id, self.table.c.role_id == role_id
            )
        else:
            stmt = stmt.where(
                self.table.c.permission_id == permission_id,
                self.table.c.role_id == role_id,
            )
        result = await session.execute(stmt)
        row_exists = result.scalar_one_or_none()

        if not row_exists:
            stmt = self.table.insert()
            if user_id:
                stmt = stmt.values(user_id=user_id, role_id=role_id)
            else:
                stmt = stmt.values(permission_id=permission_id, role_id=role_id)
            await session.execute(stmt)
            await session.commit()

    async def fetch(
        self,
        session: AsyncSession,
        role_id: str,
        user_id: str | None = None,
        permission_id: str | None = None,
    ) -> Optional[Table]:
        """
        Retrieves a user_role row or a role_permission row.

        Args:
            session(AsyncSession): database async session object.
            role_id(str): role to retrieve.
            user_id(str): Optional if retrieving into user_roles.
            permission_id(str): optional, if retrieving role_permission.
        Returns:
            object(user_role or role_permission): the retrieved object.
        Raise:
            ValueError: If Neither user_id nor permission_id is missing.
        """
        if not user_id and not permission_id:
            raise ValueError("must pass either user_id or permission_id")
        stmt = self.table.select()

        if user_id:
            stmt = stmt.where(
                self.table.c.user_id == user_id, self.table.c.role_id == role_id
            )
        else:
            stmt = stmt.where(
                self.table.c.permission_id == permission_id,
                self.table.c.role_id == role_id,
            )
        row_exists = await session.execute(stmt)

        return row_exists.scalar_one_or_none()

    async def delete(
        self,
        session: AsyncSession,
        role_id: str,
        user_id: str | None = None,
        permission_id: str | None = None,
    ) -> None:
        """
        Deletes a user_role row or a role_permission row.

        Args:
            session(AsyncSession): database async session object.
            role_id(str): role to delete.
            user_id(str): Optional if deleting user_roles.
            permission_id(str): optional, if deletig role_permission.
        Returns:
            None.
        Raise:
            ValueError: If Neither user_id nor permission_id is missing."""
        if not user_id and not permission_id:
            raise ValueError("must pass either user_id or permission_id")
        stmt = self.table.delete()

        if user_id:
            stmt = stmt.where(
                self.table.c.user_id == user_id, self.table.c.role_id == role_id
            )
        else:
            stmt = stmt.where(
                self.table.c.permission_id == permission_id,
                self.table.c.role_id == role_id,
            )
        await session.execute(stmt)
        await session.commit()


role_service = RoleService(Role)
permission_service = PermissionService(Permission)
user_roles_service = UserRolePermission(user_roles)
role_permission_service = UserRolePermission(role_permissions)
