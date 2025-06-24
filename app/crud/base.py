from http import HTTPStatus
from typing import Any, Generic, Sequence, Type, TypeVar

from fastapi import HTTPException
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from sqlalchemy import ColumnElement, delete, select
from sqlalchemy.exc import InvalidRequestError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import Base

PydanticSchema = TypeVar('PydanticSchema', bound=BaseModel)
SQLAlchemyModel = TypeVar('SQLAlchemyModel', bound=Base)


class CRUDBase(Generic[SQLAlchemyModel]):
    """При наследовании от базового класса нужно указывать в квадратных скобках модель
    с которой будет работать новый класс, и которая будет хранится в `self.model`.

    Example:
    ```
    # Наследование будет не таким
    class CRUDUser(CRUDBase):
    # а таким:
    class CRUDUser(CRUDBase[User]):
    ```
    """

    def __init__(self, model: Type[SQLAlchemyModel]) -> None:
        self.model = model

    async def get(
        self,
        async_session: AsyncSession,
        obj_id: int,
    ) -> SQLAlchemyModel | None:
        """Получает один элемент по его id.

        Args:
            async_session (AsyncSession): Асинхронная сессия
            obj_id (int): ИД объекта

        Returns:
            SQLAlchemyModel | None: Найденный объект или None, если объект не найден
        """
        db_obj = await async_session.execute(
            select(self.model).where(self.model.id == obj_id)
        )
        return db_obj.scalars().first()

    async def get_or_404(
        self,
        async_session: AsyncSession,
        obj_id: int,
        detail: str | None = None,
    ) -> SQLAlchemyModel:
        """Получает один элемент по его id или возвращает 404 ошибку.

        Args:
            async_session (AsyncSession): Асинхронная сессия
            obj_id (int): ИД объекта
            detail (str | None): Кастомное сообщение об ошибке

        Returns:
            SQLAlchemyModel: Найденный объект

        Raises:
            HTTPException: 404 если объект не найден
        """
        db_obj = await self.get(async_session, obj_id)
        if not db_obj:
            error_detail = detail or f"{self.model.__name__} with id {obj_id} not found"
            raise HTTPException(
                status_code=HTTPStatus.NOT_FOUND,
                detail=error_detail,
            )
        return db_obj

    async def get_multi(
        self,
        async_session: AsyncSession,
        order_by: tuple[ColumnElement[Any], ...] | None = None,
        **filter_by: Any,
    ) -> Sequence[SQLAlchemyModel]:
        """Получает список элементов.

        Args:
            async_session (AsyncSession): Асинхронная сессия
            order_by (tuple[ColumnElement, ...] | None, optional): Кортеж столбцов для
                сортировки. Используйте .asc() для сортировки по возрастанию и .desc()
                для убывания. По умолчанию None.
            **filter_by (Any): Именованные аргументы для фильтрации в формате
                поле=значение

        Returns:
            Sequence[SQLAlchemyModel]: Список найденных объектов или [], если объекты не
                найдены

        Example:
        ```
            # Сортировка по одному полю по возрастанию
            await crud.get_multi(
                session,
                order_by=(User.created_at.asc(),)
            )

            # Сортировка по нескольким полям
            await crud.get_multi(
                session,
                order_by=(User.role.asc(), User.created_at.desc())
            )

            # Сортировка с фильтрацией
            await crud.get_multi(
                session,
                order_by=(User.created_at.desc(),),
                is_active=True,
                role='admin'
            )
        ```
        """
        query = select(self.model).filter_by(**filter_by)
        if order_by:
            query = query.order_by(*order_by)
        db_objs = await async_session.execute(query)
        return db_objs.scalars().unique().all()

    async def create(
        self,
        async_session: AsyncSession,
        obj_in: PydanticSchema,
        user_id: int | None = None,
    ) -> SQLAlchemyModel:
        """Создает новый объект.

        Args:
            async_session (AsyncSession): Асинхронная сессия
            obj_in (PydanticSchema): Pydantic объект, который будет создан.
            user_id (int | None, optional): ИД пользователя, к которому будет привязан
                объект. По умолчанию None.

        Returns:
            SQLAlchemyModel: Созданный объект
        """
        obj_in_data = obj_in.model_dump()
        if user_id is not None:
            obj_in_data['user_id'] = user_id
        db_obj = self.model(**obj_in_data)
        async_session.add(db_obj)
        await async_session.commit()
        await async_session.refresh(db_obj)
        return db_obj

    async def bulk_create(
        self,
        async_session: AsyncSession,
        objects_in: list[PydanticSchema],
        user_id: int | None = None,
    ) -> list[SQLAlchemyModel]:
        """Создает несколько объектов за один раз.

        Args:
            async_session (AsyncSession): Асинхронная сессия
            objects_in (list[PydanticSchema]): Список Pydantic объектов для создания
            user_id (int | None): ИД пользователя для привязки объектов

        Returns:
            list[SQLAlchemyModel]: Список созданных объектов
        """
        db_objects = []
        for obj_in in objects_in:
            obj_in_data = obj_in.model_dump()
            if user_id is not None:
                obj_in_data['user_id'] = user_id
            db_obj = self.model(**obj_in_data)
            db_objects.append(db_obj)

        async_session.add_all(db_objects)
        await async_session.commit()

        for db_obj in db_objects:
            await async_session.refresh(db_obj)

        return db_objects

    async def update(
        self,
        async_session: AsyncSession,
        db_obj: SQLAlchemyModel,
        obj_in: PydanticSchema,
    ) -> SQLAlchemyModel:
        """Обновляет объект.

        Args:
            async_session (AsyncSession): Асинхронная сессия
            db_obj (SQLAlchemyModel): Объект из БД, который будет обновлен.
            obj_in (PydanticSchema): Pydantic объект, что будем обновлять.

        Returns:
            SQLAlchemyModel: Обновленный объект
        """
        obj_data = jsonable_encoder(db_obj)
        update_data = obj_in.model_dump(exclude_unset=True)

        for field in update_data:
            if field in obj_data:
                setattr(db_obj, field, update_data[field])
        async_session.add(db_obj)
        await async_session.commit()
        await async_session.refresh(db_obj)
        return db_obj

    async def delete(
        self,
        async_session: AsyncSession,
        db_obj: SQLAlchemyModel,
    ) -> None:
        """Удаляет объект. Если нет объекта, будет выброшено исключение.

        Args:
            async_session (AsyncSession): Асинхронная сессия
            db_obj (SQLAlchemyModel): Объект из БД, который будет удален.
        """
        await async_session.delete(db_obj)
        await async_session.commit()

    async def delete_by_id_or_404(
        self,
        async_session: AsyncSession,
        obj_id: int,
        detail: str | None = None,
    ) -> None:
        """Удаляет объект по ID.

        Args:
            async_session (AsyncSession): Асинхронная сессия
            obj_id (int): ИД объекта для удаления
            detail (str | None): Кастомное сообщение об ошибке если объект не найден

        Raises:
            HTTPException: 404 если объект не найден
        """
        db_obj = await self.get_or_404(async_session, obj_id, detail)
        await self.delete(async_session, db_obj)

    async def bulk_delete(
        self,
        async_session: AsyncSession,
        obj_ids: list[int],
    ) -> int:
        """Удаляет несколько объектов по списку ID.

        Args:
            async_session (AsyncSession): Асинхронная сессия
            obj_ids (list[int]): Список ID объектов для удаления

        Returns:
            int: Количество удаленных объектов
        """
        if not obj_ids:
            return 0

        stmt = delete(self.model).where(self.model.id.in_(obj_ids))
        result = await async_session.execute(stmt)
        await async_session.commit()
        return result.rowcount

    async def get_by_attribute(
        self,
        async_session: AsyncSession,
        attr_name: str,
        attr_value: Any,
    ) -> SQLAlchemyModel | None:
        """Получает объект по атрибуту

        Args:
            async_session (AsyncSession): Асинхронная сессия
            attr_name (str): Имя аттрибута, по которому будет происходить поиск
            attr_value (Any): Значение атрибута, по которому будет происходить поиск

        Raises:
            AttributeError: Если атрибута нет в модели
            ValueError: Если невозможно выполнить запрос

        Returns:
            SQLAlchemyModel | None: Найденный объект или None, если объект не найден
        """
        if not hasattr(self.model, attr_name):
            raise AttributeError(
                f"Атрибут '{attr_name}' не существует в модели {self.model.__name__}"
            )

        try:
            attr = getattr(self.model, attr_name)
            db_obj = await async_session.execute(
                select(self.model).where(attr == attr_value)
            )
            return db_obj.scalars().first()
        except InvalidRequestError as e:
            raise ValueError(
                f"Невозможно выполнить запрос с атрибутом '{attr_name}': {str(e)}"
            )

    async def get_by_attribute_or_404(
        self,
        async_session: AsyncSession,
        attr_name: str,
        attr_value: Any,
        detail: str | None = None,
    ) -> SQLAlchemyModel:
        """Получает объект по атрибуту или возвращает 404 ошибку.

        Args:
            async_session (AsyncSession): Асинхронная сессия
            attr_name (str): Имя аттрибута, по которому будет происходить поиск
            attr_value (Any): Значение атрибута, по которому будет происходить поиск
            detail (str | None): Кастомное сообщение об ошибке

        Returns:
            SQLAlchemyModel: Найденный объект

        Raises:
            HTTPException: 404 если объект не найден
        """
        db_obj = await self.get_by_attribute(async_session, attr_name, attr_value)
        if not db_obj:
            error_detail = (
                detail
                or f"{self.model.__name__} with {attr_name}={attr_value} not found"
            )
            raise HTTPException(
                status_code=HTTPStatus.NOT_FOUND,
                detail=error_detail,
            )
        return db_obj
