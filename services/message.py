import datetime
import logging
import uuid
from typing import Generator

import aiohttp as aiohttp
from sqlalchemy import select

from repository.session import create_db_session
from services.dals import BaseDAL, ResponseCode
from settings import settings
from models.db import Message, MessageStates, Customer, Mailing

from utils.async_utils import async_enumerate
from utils.decorators import catch_exceptions
from utils.time_utils import get_current_date


class MessageDAL(BaseDAL):
    # Describes the business logic of the message.
    @catch_exceptions
    async def create_message(
            self,
            sending_date: datetime,
            status: MessageStates,
            mailing_id: uuid.UUID,
            customer_id: uuid.UUID
    ) -> Message:
        """
        Creates a message in the database.
        :param sending_date:
        :param status:
        :param mailing_id:
        :param customer_id:
        :return:
        """
        new_message = Message(
            sending_date=sending_date,
            status=status.value,
            mailing_id=mailing_id,
            customer_id=customer_id
        )
        self.db_session.add(new_message)
        await self.db_session.commit()
        return new_message

    @catch_exceptions
    async def get_messages(self) -> Generator[Message, None, None]:
        """
        Outputs list of message from the database.
        :return:
        """
        messages = await self.db_session.execute(select(Message))
        return (item for item in messages.scalars())

    @staticmethod
    @catch_exceptions
    async def send_message(id: int, message: str, phone: int) -> tuple[int, str]:
        """
        Opens a session with an external API to send a message. Sends a request to send a message to the customer.
        :param id:
        :param message:
        :param phone:
        :return:
        """
        data = {
            "id": id,
            "phone": phone,
            "text": message
        }
        async with aiohttp.ClientSession(headers=settings.MAILING_API_HEADERS, timeout=settings.TIMEOUT) as session:
            async with session.post(url=settings.MAILING_API_URL, data=data) as resp:
                return resp.status, await resp.text()

    @staticmethod
    @catch_exceptions
    async def send_messages(mailing_id: uuid.UUID) -> ResponseCode:
        """
        Retrieves the mailing from the database by id. Gets a list of customers that match the filters from the
        database.
        :param mailing_id:
        :return:
        """
        from services.mailing import MailingDAL
        from services.customer import CustomerDAL

        mailing_dal = MailingDAL(create_db_session())
        customers_dal = CustomerDAL(create_db_session())

        mailing = await mailing_dal.get_mailing_by_id(mailing_id)
        customers = await customers_dal.get_customers_by_filter(filters=mailing.filters)
        await mailing_dal.db_session.close()
        await customers_dal.db_session.close()
        with_errors = await MessageDAL._start_mailing(customers, mailing)

        if with_errors:
            return ResponseCode(code=200, message='Mailing completed successfully, but with errors')
        return ResponseCode(code=200, message='Mailing successfully completed')

    @staticmethod
    async def _start_mailing(customers: Generator[Customer, None, None], mailing: Mailing) -> bool:
        """
        Starts an enumeration of messages in the customers list. After sending the message it creates a message in the
        database. If the date from mailing.expiry_date becomes less than current time while the customers list is being
        searched, the mailing is terminated prematurely.
        :param customers:
        :param mailing:
        :return:
        """
        logging.info(f'The mailing list {mailing.id} has been started.')
        with_errors = False
        async for id, customer in async_enumerate(customers):
            message_dal = MessageDAL(create_db_session())
            current_date = get_current_date()
            if mailing.expiry_date < current_date:
                return ResponseCode(code=408, message='Mailing deadline expired')
            try:
                await MessageDAL.send_message(
                    id=id,
                    phone=customer.phone,
                    message=mailing.message
                )
                await message_dal.create_message(
                    sending_date=get_current_date(),
                    status=MessageStates.DELIVERED,
                    mailing_id=mailing.id,
                    customer_id=customer.id
                )
            except Exception:
                await message_dal.create_message(
                    sending_date=get_current_date(),
                    status=MessageStates.UNDELIVERED,
                    mailing_id=mailing.id,
                    customer_id=customer.id
                )
                with_errors = True
            finally:
                await message_dal.db_session.close()
        logging.info(f'The mailing list {mailing.id} has been completed.')
        return with_errors
