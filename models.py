from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import String, DateTime, Integer, JSON, Text, ForeignKey, Boolean
from datetime import datetime
from conf import now_utc

class Base(DeclarativeBase):
    pass

class Product(Base):
    __tablename__ = "products"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    image_url: Mapped[str] = mapped_column(String(500)) # Фото товара
    # tag: Mapped[str] = mapped_column(String(100)) # Тег товара
    name: Mapped[str] = mapped_column(String(500), nullable=False)  # Название товара
    code: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)  # Код товара
    price: Mapped[int] = mapped_column(Integer, nullable=False) # Цена
    count: Mapped[int] = mapped_column(Integer, nullable=False, default=0) # Количество
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc, nullable=False)
    
    info: Mapped["Info"] = relationship(back_populates='product', uselist=False, cascade='all, delete-orphan', passive_deletes=True)  # Информация о товаре


class Info(Base):
    __tablename__ = "info"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), nullable=False)
    description: Mapped[str] = mapped_column(Text)  # Описание
    characteristic: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)  # Характеристика
    suitabel_car: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)  # Подходит к авто
    
    
    product: Mapped["Product"] = relationship(back_populates="info")