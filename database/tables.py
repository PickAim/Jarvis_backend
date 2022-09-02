from sqlalchemy import Column, Table, Index, Integer, String, \
    DateTime, Boolean, PrimaryKeyConstraint, ForeignKey
from .db_config import Base
from datetime import datetime


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    login = Column(String(255), nullable=False)
    password = Column(String(255), nullable=False)
    name = Column(String(255), nullable=False)
    wildberries_key = Column(String(255), nullable=False)


class Pay(Base):
    __tablename__ = 'pays'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey(f'{User.__tablename__}.id'))
    payment_date = Column(DateTime, nullable=False, default=datetime.now)
    is_auto = Column(Boolean, nullable=False)


class Category(Base):
    __tablename__ = 'categories'
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False, unique=True)


class Niche(Base):
    __tablename__ = 'niches'
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    category_id = Column(Integer(), ForeignKey(
        f'{Category.__tablename__}.id'))
    update_date = Column(DateTime(), nullable=False, default=datetime.now)


class Product(Base):
    __tablename__ = 'products'
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    niche_id = Column(Integer(), ForeignKey(f'{Niche.__tablename__}.id'))


class ProductCostHistory(Base):
    __tablename__ = 'product_cost_histories'
    id = Column(Integer, primary_key=True)
    cost = Column(Integer(), nullable=False)
    date = Column(DateTime(), nullable=False, default=datetime.now)
    product_id = Column(Integer, ForeignKey(f'{Product.__tablename__}.id'))
