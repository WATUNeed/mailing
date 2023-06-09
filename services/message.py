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
from utils.decorators import catch_exceptions, services_request
from utils.time_utils import get_current_date


logger = logging.getLogger("uvicorn")


class MessageDAL(BaseDAL):
    # Describes the business logic of the message.
    @services_request
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

    @services_request
    @catch_exceptions
    async def get_messages(
            self,
            limit: int = 10,
            offset: int = 0,
            pagination: bool = True
    ) -> Generator[Message, None, None]:
        """
        Outputs list of message from the database.
        :return:
        """
        if pagination:
            messages = await self.db_session.execute(select(Message).limit(limit).offset(offset))
        else:
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
        url = f'{settings.MAILING_API_URL}{id}'
        data = {
            "customer_id": id,
            "phone": phone,
            "text": message
        }
        session_timeout = aiohttp.ClientTimeout(total=None, sock_connect=settings.TIMEOUT, sock_read=settings.TIMEOUT)
        async with aiohttp.ClientSession(timeout=session_timeout) as session:
            async with session.post(url=url, data=data) as resp:
                return resp.status, await resp.text()

    @staticmethod
    @catch_exceptions
    async def send_messages(mailing_id: uuid.UUID) -> ResponseCode:
        """
        Retrieves the mailing from the database by customer_id. Gets a list of customers that match the filters from the
        database.
        :param mailing_id:
        :return:
        """
        from services.mailing import MailingDAL
        from services.customer import CustomerDAL

        mailing = await MailingDAL(create_db_session()).get_mailing_by_id(mailing_id)

        if mailing.start_date > get_current_date():
            return ResponseCode(code=410, message='The task is overwritten.')

        customers = await CustomerDAL(create_db_session()).get_customers_by_filter(filters=mailing.filters)
        with_errors = await MessageDAL._start_mailing(customers, mailing)

        if with_errors:
            return ResponseCode(code=200, message='Mailing completed successfully, but with errors.')

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
                    message=mailing.message,
                )
                await message_dal.create_message(
                    sending_date=get_current_date(),
                    status=MessageStates.DELIVERED,
                    mailing_id=mailing.mailing_id,
                    customer_id=customer.customer_id,
                )
            except Exception as e:
                await message_dal.create_message(
                    sending_date=get_current_date(),
                    status=MessageStates.UNDELIVERED,
                    mailing_id=mailing.mailing_id,
                    customer_id=customer.customer_id,
                )
                with_errors = True
                logger.error(e)
            finally:
                logger.debug(f'Customer {customer.customer_id} received message.')
        logger.info(f'Mailing {mailing.mailing_id} is completed.')
        return with_errors
