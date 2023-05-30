import uuid
import enum

from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import Column, String, ForeignKey, DateTime, Integer, BigInteger
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.sql import func


Base = declarative_base()


class Mailing(Base):
    # An entity describes the distribution of messages to users' phone numbers.
    __tablename__ = 'mailing'

    id = Column(UUID(as_uuid=True), primary_key=True, unique=True, default=uuid.uuid4)
    start_date = Column(DateTime(timezone=True), server_default=func.now())
    message = Column(String, nullable=False)
    filters = Column(Integer, nullable=True)
    expiry_date = Column(DateTime(timezone=True), server_default=func.now())

    messages = relationship("Message", back_populates="mailings")

    def __repr__(self):
        return f'msg: {self.message} in: {self.start_date}'


class Customer(Base):
    # The entity describes phone owners.
    __tablename__ = 'customer'

    id = Column(UUID(as_uuid=True), primary_key=True, unique=True, default=uuid.uuid4)
    phone = Column(BigInteger, nullable=False)
    code = Column(Integer, nullable=True)
    time_zone = Column(String, nullable=True)

    messages = relationship("Message", back_populates="customers")

    def __repr__(self):
        return f'Customer: {self.id} phone: {self.phone_number}'


class MessageStates(enum.Enum):
    # Lists the message states.
    DELIVERED = 'DELIVERED'
    UNDELIVERED = 'UNDELIVERED'

    @classmethod
    def list(cls):
        return list(map(lambda c: c.value, cls))


class Message(Base):
    # The entity describes the message that was sent to the customer from the mailing list.
    __tablename__ = 'message'

    id = Column(UUID(as_uuid=True), primary_key=True, unique=True, default=uuid.uuid4)
    sending_date = Column(DateTime(timezone=True), server_default=func.now())
    status = Column(String, default=MessageStates.UNDELIVERED.value)

    mailing_id = Column(UUID(as_uuid=True), ForeignKey('mailing.id'))
    customer_id = Column(UUID(as_uuid=True), ForeignKey('customer.id'))

    mailings = relationship('Mailing', back_populates="messages")
    customers = relationship('Customer', back_populates="messages")

    def __repr__(self):
        return f'id: {self.id} ' \
               f'sending data: {self.sending_date} ' \
               f'customer: {self.customer_id} ' \
               f'mailing: {self.mailing_id}'
