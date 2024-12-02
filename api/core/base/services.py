"""
Base Service module
"""

from typing import TypeVar, Generic, Type, List, Optional, Sequence
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, asc, delete as sql_delete, update, func
from sqlalchemy.orm.attributes import InstrumentedAttribute
from sqlalchemy.orm import selectinload

from api.v1.user.model import User

ModelType = TypeVar("ModelType")
# Model could be User, Product, Profile


async def validate_pagination(filterer: dict) -> tuple:
    """
    Validate page and limit from filter.
    """
    page = filterer.pop("page", 1)
    if page < 1:
        page = 1
    limit = filterer.pop("limit", 10)
    if limit < 1 or limit > 10:
        limit = 10

    return page, limit


async def validate_sort(
    model: Type[ModelType], sort: str
) -> Optional[InstrumentedAttribute]:
    """
    Validate if the sort field exists on the model.
    :param filterer: dict containing the field name to order by
    :param model: the SQLAlchemy model class
    :return: the model attribute if valid, else None
    """
    if hasattr(model, sort):
        return getattr(model, sort)
    return getattr(model, "created_at")


async def validate_sort_order(sort_order: str):
    """
    Validates sort order
    """
    if sort_order not in ["desc", "asc"]:
        sort_order == "desc"
    return sort_order


async def validate_params(model: Type[ModelType], filterer: dict) -> dict:
    """
    Validate if the filterer fields exists on the model.
    :param filterer: dict containing the field name to order by
    :param model: the SQLAlchemy model class
    :return: the model attribute if valid, else None
    """
    return {k: v for k, v in filterer.items() if hasattr(model, k)}


class Service(Generic[ModelType]):
    """
    Base service class for all services
    """

    def __init__(self, model: Type[ModelType]) -> None:
        self.model = model

    async def create(self, schema: dict, session: AsyncSession) -> ModelType:
        """
        Create a new record in the database
        :param schema: dictionary containing model data
        :param session: AsyncSession from SQLAlchemy
        """
        if self.model == User:
            password = schema.pop("password", "")
            schema.pop("confirm_password", None)
            obj = self.model(**schema)
            obj.set_password(password)
        else:
            obj = self.model(**schema)

        session.add(obj)

        await session.commit()
        return obj

    async def create_all(
        self, schema_list: List[dict], session: AsyncSession
    ) -> List[ModelType]:
        """
        Create a new record in the database.

        Args:
            schema(List(dict)): List of dictionaries containing fields of data to create
            session: AsyncSession from SQLAlchemy
        Returns:
            objects(List[objects]): List containing the newly created objects.
        """
        validated_schemas: list = []
        # validate attributes
        for schema in schema_list:
            validated_schemas.append(await validate_params(self.model, schema))

        new_objects: list = []
        # iterate through schemas
        for schema in validated_schemas:
            new_objects.append(self.model(**schema))

        session.add_all(new_objects)
        await session.commit()
        return new_objects

    async def update(
        self, where: List[dict], session: AsyncSession
    ) -> Optional[ModelType]:
        """
        Update a record in the database and return the updated object.
            :param where: list containing dicts with filters and data to update
            :param session: AsyncSession from SQLAlchemy
            :return: Updated object
        """
        filterer, schema = where[:2]
        schema = await validate_params(self.model, schema)
        filterer = await validate_params(self.model, filterer)

        stmt = update(self.model)

        for key, value in filterer.items():
            stmt = stmt.where(getattr(self.model, key) == value)
        stmt = stmt.values(**schema).returning(self.model)

        result = await session.execute(stmt)
        await session.commit()

        updated_object = result.unique().scalar()
        await session.refresh(updated_object)
        return updated_object

    async def fetch(self, filterer: dict, session: AsyncSession) -> Optional[ModelType]:
        """
        Fetch a record by using a passed filter(s)
        :param filterer: dictionary containing search data (e.g., {'id': 20})
        :param session: AsyncSession from SQLAlchemy
        """
        if not filterer:
            return
        stmt = select(self.model)
        valid_fields = await validate_params(self.model, filterer)
        if not valid_fields:
            return

        if self.model == User:
            for key, value in valid_fields.items():
                stmt = stmt.options(selectinload(self.model.roles)).where(
                    getattr(self.model, key) == value
                )
        else:
            for key, value in valid_fields.items():
                stmt = stmt.where(getattr(self.model, key) == value)

        result = await session.execute(stmt)

        return result.scalar_one_or_none()

    async def fetch_all(
        self, filterer: dict, session: AsyncSession, where: dict
    ) -> Sequence[ModelType]:
        """
        Fetch all records with optional filters
            filter(dict): dictionary containing filter parameters, e,g., {"sort": "created_at"}
            where(dict): dict containing key and values of whereclause, e.g {"id": "someid}
            session(dict): AsyncSession from SQLAlchemy
        Returns:
            All objects or empty list.
        """
        # validate pagination
        page, limit = await validate_pagination(filterer)

        sort_attr = await validate_sort(self.model, filterer.pop("sort", "created_at"))

        sort_order = await validate_sort_order(filterer.pop("sort_order", "desc"))

        stmt = select(self.model)
        # validate filters
        valid_fields: dict = await validate_params(self.model, where)
        # return empty list if filter is all invalid field

        # apply filters
        if valid_fields:
            for key, value in valid_fields.items():
                stmt = stmt.where(getattr(self.model, key) == value)
        # check for sorting
        if sort_order == "desc":
            result = await session.execute(
                stmt.order_by(desc(sort_attr)).limit(limit).offset((page - 1) * limit)
            )
        else:
            result = await session.execute(
                stmt.order_by(asc(sort_attr)).limit(limit).offset((page - 1) * limit)
            )

        all_objects = result.scalars().all()
        return all_objects

    async def delete(self, filterer: dict, session: AsyncSession) -> bool:
        """
        Delete a record by using the passed filter(s)
        :param filterer: dictionary containing search data (e.g., {'id': 20})
        :param session: AsyncSession from SQLAlchemy
        :return: True if the record was deleted, False otherwise
        """

        stmt = sql_delete(self.model)
        valid_fields = await validate_params(self.model, filterer)
        if not valid_fields and filterer:
            return False

        for key, value in valid_fields.items():
            stmt = stmt.where(getattr(self.model, key) == value)

        result = await session.execute(stmt)
        await session.commit()
        return result.rowcount > 0

    async def delete_all(
        self, session: AsyncSession, where: dict = {}
    ) -> Optional[Sequence[ModelType]]:
        """
        Delete all records.

        Args:
            session(object): AsyncSession from SQLAlchemy.
            where(dict): filters of fields to delete.
        Returns:
            A sequence of deleted rows, if any.
        """
        stmt = sql_delete(self.model)
        if len(where) > 0:
            valid_fields: dict = await validate_params(self.model, where)
            if len(valid_fields) > 0:
                for key, value in valid_fields.items():
                    stmt = stmt.where(getattr(self.model, key) == value)

        result = await session.execute(stmt.returning(self.model))
        return result.scalars().all()

    async def count(self, session: AsyncSession, where: dict = {}) -> int:
        """
        Counts the number of rows.

        Args:
            session(AsyncSession): database async session object.
            where(dict): fields with a specific value(s) to count.
                        e,g ({"location": {"city": "Lagos", "state": "Lagos", "country": "Nigeria"}})

        Returns:
            number of rows.
        """
        stmt = select(func.count()).select_from(self.model)
        if where:
            where = await validate_params(self.model, where)
            for key, value in where.items():
                stmt = stmt.where(getattr(self.model, key) == value)
        result = await session.execute(stmt)

        count = result.scalar_one_or_none()
        return count if count is not None else 0


if __name__ == "__main__":
    pass
