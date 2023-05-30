import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from models.db import MessageStates
from models.schemas.customer import CustomerCreate, ShowCustomer, ShowCustomers, CustomerEdit
from models.schemas.mailing import (
    MailingCreate,
    ShowMailing,
    MailingEdit,
    ShowMailingAPIResponse, ShowStatisticsByMailing, ShowStatisticsMailings
)
from models.schemas.message import ShowMessages, ShowMessage, CreateMessage
from services.customer import CustomerDAL
from services.mailing import MailingDAL
from services.message import MessageDAL
from utils.decorators import request
from utils.time_utils import get_current_date


@request
async def create_customer_controller(body: CustomerCreate, session: AsyncSession) -> ShowCustomer:
    """
    Creates a buyer in the database.
    :param body:
    :param session:
    :return:
    """
    customer_dal = CustomerDAL(session)
    customer = await customer_dal.create_customer(**body.dict())
    return ShowCustomer(**customer.__dict__)


@request
async def get_customers_controller(session: AsyncSession) -> ShowCustomers:
    """
    Outputs a list of customers from the database.
    :param session:
    :return:
    """
    customer_dal = CustomerDAL(session)
    customers = await customer_dal.get_customers()
    return ShowCustomers(customers=[ShowCustomer(**customer.__dict__) for customer in customers])


@request
async def edit_customer_controller(body: CustomerEdit, session: AsyncSession) -> ShowCustomer:
    """
    Changes the value of the buyer in the database.
    :param body:
    :param session:
    :return:
    """
    customer_dal = CustomerDAL(session)
    customer = await customer_dal.edit_customer(**body.dict())
    return ShowCustomer(**customer.__dict__)


@request
async def delete_customer_controller(id: uuid.UUID, session: AsyncSession) -> ShowCustomer:
    """
    Deletes the customer from the database.
    :param id:
    :param session:
    :return:
    """
    customer_dal = CustomerDAL(session)
    customer = await customer_dal.delete_customer(id=id)
    return ShowCustomer(**customer.__dict__)


@request
async def create_mailing_controller(body: MailingCreate, session: AsyncSession) -> ShowMailing:
    """
    Creates a mailing list in a database.
    :param body:
    :param session:
    :return:
    """
    mailing_dal = MailingDAL(session)
    mailing = await mailing_dal.create_mailing(**body.dict())
    return ShowMailing(**mailing.__dict__)


@request
async def edit_mailing_controller(body: MailingEdit, session: AsyncSession) -> ShowMailing:
    """
    Changes the mailing list in the database.
    :param body:
    :param session:
    :return:
    """
    mailing_dal = MailingDAL(session)
    mailing = await mailing_dal.edit_mailing(**body.dict())
    return ShowMailing(**mailing.__dict__)


@request
async def delete_mailing_controller(mailing_id: uuid.UUID, session: AsyncSession) -> ShowMailing:
    """
    Deletes the mailing list in the database.
    :param mailing_id:
    :param session:
    :return:
    """
    mailing_dal = MailingDAL(session)
    mailing = await mailing_dal.delete_mailing(mailing_id)
    return ShowMailing(**mailing.__dict__)


@request
async def send_mailing_controller(mailing_id: uuid.UUID, session: AsyncSession) -> ShowMailingAPIResponse:
    """
    Changes the start_date and expiry_date of the mailing in the database and starts the mailing list.
    :param mailing_id:
    :param session:
    :return:
    """
    mailing_dal = MailingDAL(session)
    response = await mailing_dal.send_mailing(mailing_id)
    return ShowMailingAPIResponse(**response._asdict())


@request
async def get_mailing_statistics_by_id_controller(
        mailing_id: uuid.UUID,
        session: AsyncSession
) -> ShowStatisticsByMailing:
    """
    Outputs mailing statistics from the database.
    :param mailing_id:
    :param session:
    :return:
    """
    mailing_dal = MailingDAL(session)
    return await mailing_dal.get_statistics_by_mailing(mailing_id)


@request
async def get_statistics_mailings_controller(session: AsyncSession) -> ShowStatisticsMailings:
    """
    Outputs statistics on all mailings from the database.
    :param session:
    :return:
    """
    mailing_dal = MailingDAL(session)
    return await mailing_dal.get_statistics_mailings()


@request
async def get_messages_controller(session: AsyncSession) -> ShowMessages:
    """
    Outputs a list of all messages from the database.
    :param session:
    :return:
    """
    message_dal = MessageDAL(session)
    messages = await message_dal.get_messages()
    return ShowMessages(messages=[ShowMessage(**message.__dict__) for message in messages])


@request
async def create_message_controller(body: CreateMessage, session: AsyncSession) -> ShowMessage:
    """
    Creates a message in the database.
    :param body:
    :param session:
    :return:
    """
    message_dal = MessageDAL(session)
    message = await message_dal.create_message(
        sending_date=get_current_date(),
        status=MessageStates.DELIVERED,
        mailing_id=body.mailing_id,
        customer_id=body.customer_id
    )
    return ShowMessage(**message.__dict__)
