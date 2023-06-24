from dataclasses import dataclass, asdict
from datetime import datetime
import uuid
from typing import NamedTuple
import pandas as pd

from fastapi import HTTPException
from sqlalchemy import select, delete
from sqlalchemy.orm import selectinload

from models.schemas.mailing import ShowStatisticsByMailing, ShowStatisticsMailings
from models.schemas.message import ShowMessages, ShowMessage
from repository.session import create_db_session
from models.db import Mailing, MessageStates
from services.dals import BaseDAL, ResponseCode
from settings import settings
from utils.async_utils import async_generator
from utils.decorators import catch_exceptions, services_request
from utils.time_utils import get_current_date
from tasks.tasks import run_mailing


class MailingDAL(BaseDAL):
    class MessagesListsByStates(NamedTuple):
        delivered_messages: ShowMessages
        undelivered_messages: ShowMessages

    @dataclass(kw_only=True, slots=True)
    class MailingStats:
        completed_mailings_count: int
        uncompleted_mailings_count: int
        total_delivered_messages: int
        total_undelivered_messages: int
        mailings: list[ShowStatisticsByMailing]

    @catch_exceptions
    @services_request
    async def create_mailing(self, start_date: datetime, message: str, filters: int, expiry_date: datetime) -> Mailing:
        """
        Creates a mailing list in a database.
        :param start_date:
        :param message:
        :param filters:
        :param expiry_date:
        :return:
        """
        new_mailing = Mailing(start_date=start_date, message=message, filters=filters, expiry_date=expiry_date)
        self.db_session.add(new_mailing)
        await self.db_session.commit()
        run_mailing.apply_async(args=(new_mailing.mailing_id,), eta=start_date)
        return new_mailing

    @services_request
    @catch_exceptions
    async def edit_mailing(
            self,
            mailing_id: uuid.UUID,
            start_date: datetime,
            message: str,
            filters: int,
            expiry_date: datetime
    ) -> Mailing:
        """
        Edit a mailing list in a database.
        :param mailing_id:
        :param start_date:
        :param message:
        :param filters:
        :param expiry_date:
        :return:
        """
        result = await self.db_session.execute(select(Mailing).where(Mailing.mailing_id == mailing_id))
        mailing: Mailing = result.scalars().one()
        mailing.start_date = start_date
        mailing.message = message
        mailing.filters = filters
        mailing.expiry_date = expiry_date
        await self.db_session.commit()
        run_mailing.apply_async(args=(mailing_id,), eta=start_date)
        return mailing

    async def check_mailing_for_existence(self, mailing_id: uuid.UUID) -> bool | Mailing:
        mailing = await self.db_session.execute(select(Mailing).where(Mailing.mailing_id == mailing_id).limit(1))
        mailing = mailing.scalars().one()

        if not mailing:
            return False
        return mailing

    @services_request
    @catch_exceptions
    async def delete_mailing(self, mailing_id: uuid.UUID) -> Mailing:
        """
        Delete a mailing list in a database.
        :param mailing_id:
        :return:
        """
        mailing = await MailingDAL(create_db_session()).check_mailing_for_existence(mailing_id=mailing_id)
        await self.db_session.execute(delete(Mailing).where(Mailing.mailing_id == mailing_id))
        await self.db_session.commit()
        return mailing

    @services_request
    @catch_exceptions
    async def get_mailing_by_id(self, mailing_id: uuid.UUID) -> Mailing:
        """
        Outputs mailing by its customer_id.
        :param mailing_id:
        :return:
        """
        mailing = await self.db_session.execute(select(Mailing).where(Mailing.mailing_id == mailing_id).limit(1))
        mailing = mailing.scalars().one()

        if not mailing:
            raise HTTPException(status_code=404, detail='Mailing is not found')

        return mailing

    @services_request
    @catch_exceptions
    async def send_mailing(self, mailing_id: uuid.UUID) -> ResponseCode:
        """
        Starts mailing by customer_id.
        :param mailing_id:
        :return:
        """
        from services.message import MessageDAL

        mailing = await self.get_mailing_by_id(mailing_id)
        await MailingDAL(create_db_session()).edit_mailing(
            id=mailing.mailing_id,
            start_date=get_current_date(),
            message=mailing.message,
            filters=mailing.filters,
            expiry_date=get_current_date() + pd.DateOffset(minutes=settings.MAILING_OFFSET_MIN)
        )
        return await MessageDAL.send_messages(mailing_id)

    @services_request
    @catch_exceptions
    async def get_statistics_by_mailing(self, mailing_id: uuid.UUID) -> ShowStatisticsByMailing:
        """
        Outputs statistics on the mailing list customer_id.
        :param mailing_id:
        :return:
        """
        current_datetime = get_current_date()

        query = select(Mailing).options(selectinload(Mailing.messages)).where(Mailing.mailing_id == mailing_id)
        result = await self.db_session.execute(query)
        mailing = result.scalar()

        if not mailing:
            raise HTTPException(status_code=404, detail='Mailing is not found')

        if mailing.expiry_date > current_datetime:
            return ShowStatisticsByMailing(
                **mailing.__dict__,
                delivered_count=0,
                undelivered_count=0,
                delivered_messages=ShowMessages(messages=[]),
                undelivered_messages=ShowMessages(messages=[]),
            )

        delivered_messages, undelivered_messages = await MailingDAL._split_messages_by_states(mailing)

        return ShowStatisticsByMailing(
            **mailing.__dict__,
            delivered_count=len(delivered_messages.messages),
            undelivered_count=len(undelivered_messages.messages),
            delivered_messages=delivered_messages,
            undelivered_messages=undelivered_messages,
        )

    @services_request
    @catch_exceptions
    async def get_statistics_mailings(self) -> ShowStatisticsMailings:
        """
        Outputs statistics on all mailings.
        :return:
        """
        query = select(Mailing).options(selectinload(Mailing.messages))
        result = await self.db_session.execute(query)
        mailings = result.scalars().all()
        statistics = await MailingDAL._counting_statistics_by_mailings(mailings)
        return ShowStatisticsMailings(**asdict(statistics))

    @staticmethod
    async def _counting_statistics_by_mailings(mailings: Mailing) -> MailingStats:
        """
        Packs a mailing list and counts statistics.
        :param mailings:
        :return:
        """
        current_datetime = get_current_date()

        result = MailingDAL.MailingStats(
            completed_mailings_count=0,
            uncompleted_mailings_count=0,
            total_delivered_messages=0,
            total_undelivered_messages=0,
            mailings=[]
        )

        async for mailing in async_generator(mailings):
            statistics = await MailingDAL(create_db_session()).get_statistics_by_mailing(mailing.customer_id)

            if mailing.expiry_date < current_datetime:
                result.completed_mailings_count += 1
            else:
                result.uncompleted_mailings_count += 1

            result.total_delivered_messages += statistics.delivered_count
            result.total_undelivered_messages += statistics.undelivered_count
            result.mailings.append(ShowStatisticsByMailing(**statistics.__dict__))
        return result

    @staticmethod
    async def _split_messages_by_states(mailing: Mailing) -> MessagesListsByStates:
        """
        Divides the mailing list by state.
        :param mailing:
        :return:
        """
        messages = MailingDAL.MessagesListsByStates(
            delivered_messages=ShowMessages(messages=[]),
            undelivered_messages=ShowMessages(messages=[])
        )
        async for message in async_generator(mailing.messages):
            if message.status == MessageStates.DELIVERED.value:
                messages.delivered_messages.messages.append(ShowMessage(**message.__dict__))
            else:
                messages.undelivered_messages.messages.append(ShowMessage(**message.__dict__))
        return messages
