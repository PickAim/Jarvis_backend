from email.policy import default
from xmlrpc.client import Boolean, DateTime
from sqlalchemy import Column, Table, Index, Integer, String, \
    DateTime, Boolean, PrimaryKeyConstraint, ForeignKey
from .db_config import Base
from datetime import datetime


class Users(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    login = Column(String(255), nullable=False)
    password = Column(String(255), nullable=False)
    name = Column(String(255), nullable=False)


class Pays(Base):
    __tablename__ = 'pays'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey(f'{Users.__tablename__}.id'))
    payment_date = Column(DateTime, nullable=False, default=datetime.now)
    is_auto = Column(Boolean, nullable=False)


class Categories(Base):
    __tablename__ = 'categories'
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)


class Niches(Base):
    __tablename__ = 'niches'
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    category_id = Column(Integer(), ForeignKey(
        f'{Categories.__tablename__}.id'))
    update_date = Column(DateTime(), nullable=False, default=datetime.now)


class Products(Base):
    __tablename__ = 'products'
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    niche_id = Column(Integer(), ForeignKey(f'{Niches.__tablename__}.id'))


class ProductCostHistories(Base):
    __tablename__ = 'product_cost_histories'
    id = Column(Integer, primary_key=True)
    cost = Column(Integer())
    date = Column(DateTime(), nullable=False, default=datetime.now)
