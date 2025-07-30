import datetime
import pytz
from sqlalchemy import ForeignKey, BigInteger, Date, func
from sqlalchemy.orm import relationship, Mapped, mapped_column
from models.databases import Base


class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True)
    full_name: Mapped[str]
    username: Mapped[str] = mapped_column(nullable=True)
    admin: Mapped[bool] = mapped_column(default=False)


class Price(Base):
    __tablename__ = 'prices'

    id: Mapped[int] = mapped_column(primary_key=True)
    chat_tg_id: Mapped[int] = mapped_column(ForeignKey("users.telegram_id"))
    name: Mapped[str]
    price: Mapped[int]
    add_date: Mapped[datetime.date] = mapped_column(
        Date,
        default=lambda: datetime.datetime.now(
            pytz.timezone("Asia/Yekaterinburg")).date()
    )


class Chat(Base):
    __tablename__ = 'chats'

    id: Mapped[int] = mapped_column(primary_key=True)
    chat_tg_id: Mapped[int] = mapped_column(BigInteger, unique=True)
