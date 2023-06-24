import uuid
from typing import Generator

from fastapi import HTTPException
from sqlalchemy import select, delete

from models.db import Customer
from repository.session import create_db_session
from services.dals import BaseDAL
from utils.decorators import catch_exceptions, services_request


class CustomerDAL(BaseDAL):
    # Contains the customer's business logic.
    @services_request
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

    @services_request
    @catch_exceptions
    async def get_customers(
            self,
            limit: int = 10,
            offset: int = 0,
            pagination: bool = True
    ) -> Generator[Customer, None, None]:
        """
        Get list of customer from database.
        :return: List of customers
        """
        if pagination:
            customers = await self.db_session.execute(select(Customer).limit(limit).offset(offset))
        else:
            customers = await self.db_session.execute(select(Customer))
        return (item for item in customers.scalars())

    @services_request
    @catch_exceptions
    async def edit_customer(self, customer_id: uuid.UUID, phone: int, code: int, time_zone: str) -> Customer:
        """
        Edit customer in database.
        :param customer_id:
        :param phone:
        :param code:
        :param time_zone:
        :return:
        """
        result = await self.db_session.execute(select(Customer).where(Customer.customer_id == customer_id))
        customer: Customer = result.scalars().one()
        customer.phone_number = phone
        customer.mobile_code = code
        customer.time_zone = time_zone
        await self.db_session.commit()
        return customer

    @services_request
    @catch_exceptions
    async def get_customer(self, customer_id: uuid.UUID) -> Customer:
        """
        Output the customer by customer_id.
        :param customer_id:
        :return:
        """
        result = await self.db_session.execute(select(Customer).where(Customer.customer_id == customer_id).limit(1))
        customer = result.scalars().one()
        return customer

    @services_request
    @catch_exceptions
    async def delete_customer(self, customer_id: uuid.UUID) -> Customer:
        """
        Delete customer from database.
        :param customer_id:
        :return:
        """

        customer = await CustomerDAL(create_db_session()).get_customer(customer_id)

        if not customer:
            return HTTPException(status_code=404, detail='Customer is not found')

        await self.db_session.execute(delete(Customer).where(Customer.customer_id == customer_id))
        await self.db_session.commit()
        return customer

    @services_request
    @catch_exceptions
    async def get_customers_by_filter(self, filters: int) -> Generator[Customer, None, None]:
        """
        Outputs generator of customers by filter.
        :param filters:
        :return: Customers generator
        """
        customers = await self.db_session.execute(select(Customer).where(Customer.code == filters))
        return (item for item in customers.scalars())
