import uuid
from typing import Generator

from fastapi import HTTPException
from sqlalchemy import select, delete

from models.db import Customer
from repository.session import create_db_session
from services.dals import BaseDAL
from utils.decorators import catch_exceptions


class CustomerDAL(BaseDAL):
    # Contains the customer's business logic.
    @catch_exceptions
    async def create_customer(self, phone: int, code: int, time_zone: str) -> Customer:
        """
        Creates a customer record in database.
        :param phone:
        :param code:
        :param time_zone:
        :return: Customer in database
        """
        new_customer = Customer(phone=phone, code=code, time_zone=time_zone)
        self.db_session.add(new_customer)
        await self.db_session.flush()
        return new_customer

    @catch_exceptions
    async def get_customers(self) -> Generator[Customer, None, None]:
        """
        Get list of customer from database.
        :return: List of customers
        """
        customers = await self.db_session.execute(select(Customer))
        return (item for item in customers.scalars())

    @catch_exceptions
    async def edit_customer(self, id: uuid.UUID, phone: int, code: int, time_zone: str) -> Customer:
        """
        Edit customer in database.
        :param id:
        :param phone:
        :param code:
        :param time_zone:
        :return:
        """
        result = await self.db_session.execute(select(Customer).where(Customer.id == id))
        customer: Customer = result.scalars().one()
        customer.phone_number = phone
        customer.mobile_code = code
        customer.time_zone = time_zone
        await self.db_session.commit()
        return customer

    @catch_exceptions
    async def delete_customer(self, id: uuid.UUID) -> Customer:
        """
        Delete customer from database.
        :param id:
        :return:
        """
        customer = await self.db_session.execute(select(Customer).where(Customer.id == id).limit(1))
        customer = customer.scalars().one()
        await self.db_session.close()

        if not customer:
            return HTTPException(status_code=404, detail='Customer is not found')

        self.db_session = create_db_session()
        await self.db_session.execute(delete(Customer).where(Customer.id == id))
        await self.db_session.commit()
        await self.db_session.close()
        return customer

    @catch_exceptions
    async def get_customers_by_filter(self, filters: int) -> Generator[Customer, None, None]:
        """
        Outputs generator of customers by filter.
        :param filters:
        :return: Customers generator
        """
        customers = await self.db_session.execute(select(Customer).where(Customer.code == filters))
        return (item for item in customers.scalars())