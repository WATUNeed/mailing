import uuid

from fastapi import Depends, APIRouter
from fastapi_cache.decorator import cache
from sqlalchemy.ext.asyncio import AsyncSession

from api.controllers import (
    create_customer_controller,
    get_customers_controller,
    edit_customer_controller,
    delete_customer_controller,
    create_mailing_controller,
    edit_mailing_controller,
    send_mailing_controller,
    get_messages_controller,
    create_message_controller,
    get_mailing_statistics_by_id_controller,
    get_statistics_mailings_controller,
    delete_mailing_controller
)
from api.dependencies import PaginationParameters
from models.schemas.customer import (
    ShowCustomer,
    CustomerCreate,
    ShowCustomers,
    CustomerEdit
)
from models.schemas.mailing import (
    ShowMailing,
    MailingCreate,
    MailingEdit,
    ShowMailingAPIResponse,
    ShowStatisticsByMailing,
    ShowStatisticsMailings,
)
from models.schemas.message import (
    ShowMessages,
    ShowMessage,
    CreateMessage
)
from repository.session import get_session_generator
from settings import settings


customer_router = APIRouter(
    prefix='/customer',
    tags=['customer'],
)

mailing_router = APIRouter(
    prefix='/mailing',
    tags=['mailing'],
)

message_router = APIRouter(
    prefix='/message',
    tags=['message'],
)

statistics_router = APIRouter(
    prefix='/mailing/statistics',
    tags=['statistics'],
)


@customer_router.post('/create', response_model=ShowCustomer)
async def create_customer(
        body: CustomerCreate,
        session: AsyncSession = Depends(get_session_generator)
) -> ShowCustomer:
    return await create_customer_controller(body, session=session)


@customer_router.get('/list', response_model=ShowCustomers)
@cache(expire=settings.EXPIRY_TIME_SEC)
async def get_customers(
        paginator: PaginationParameters = Depends(PaginationParameters),
        session: AsyncSession = Depends(get_session_generator)
) -> ShowCustomers:
    return await get_customers_controller(session=session, paginator=paginator)


@customer_router.put('/edit', response_model=ShowCustomer)
async def edit_customer(
        body: CustomerEdit,
        session: AsyncSession = Depends(get_session_generator)
) -> ShowCustomer:
    return await edit_customer_controller(body, session=session)


@customer_router.delete('/delete', response_model=ShowCustomer)
async def delete_customer(
        customer_id: uuid.UUID,
        session: AsyncSession = Depends(get_session_generator)
) -> ShowCustomer:
    return await delete_customer_controller(customer_id, session=session)


@mailing_router.post('/create', response_model=ShowMailing)
async def create_mailing(
        body: MailingCreate,
        session: AsyncSession = Depends(get_session_generator),
) -> ShowMailing:
    return await create_mailing_controller(body, session=session)


@mailing_router.put('/edit', response_model=ShowMailing)
async def edit_mailing(
        body: MailingEdit,
        session: AsyncSession = Depends(get_session_generator)
) -> ShowMailing:
    return await edit_mailing_controller(body, session=session)


@mailing_router.delete('/delete', response_model=ShowMailing)
@cache(expire=settings.EXPIRY_TIME_SEC)
async def delete_mailing(
        mailing_id: uuid.UUID,
        session: AsyncSession = Depends(get_session_generator)
) -> ShowMailing:
    return await delete_mailing_controller(mailing_id, session=session)


@mailing_router.post('/send', response_model=ShowMailingAPIResponse)
async def send_mailing(
        mailing_id: uuid.UUID,
        session: AsyncSession = Depends(get_session_generator)
) -> ShowMailingAPIResponse:
    return await send_mailing_controller(mailing_id, session=session)


@statistics_router.get('/by_id', response_model=ShowStatisticsByMailing)
@cache(expire=settings.EXPIRY_TIME_SEC)
async def get_statistics_by_id(
        mailing_id: uuid.UUID,
        session: AsyncSession = Depends(get_session_generator)
) -> ShowStatisticsByMailing:
    return await get_mailing_statistics_by_id_controller(mailing_id, session=session)


@statistics_router.get('/all', response_model=ShowStatisticsMailings)
@cache(expire=settings.EXPIRY_TIME_SEC)
async def get_statistics_mailings(
        session: AsyncSession = Depends(get_session_generator)
) -> ShowStatisticsMailings:
    return await get_statistics_mailings_controller(session=session)


@message_router.post('/create', response_model=ShowMessage)
async def create_message(
        body: CreateMessage,
        session: AsyncSession = Depends(get_session_generator)
) -> ShowMessage:
    return await create_message_controller(body, session=session)


@message_router.get('/list', response_model=ShowMessages)
@cache(expire=settings.EXPIRY_TIME_SEC)
async def get_messages(
        paginator: PaginationParameters = Depends(PaginationParameters),
        session: AsyncSession = Depends(get_session_generator)
) -> ShowMessages:
    return await get_messages_controller(session=session, paginator=paginator)
