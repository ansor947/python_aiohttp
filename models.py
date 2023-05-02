import aiohttp
import asyncio
from aiohttp import web
from sqlalchemy import Column, String, Integer, DateTime, Text, func
from server import engine, Base, app


class Advertisements(Base):

    __tablename__ = 'advertisements'

    id = Column(Integer, primary_key=True, autoincrement=True)
    owner = Column(String, nullable=True, index=True, unique=True)
    header = Column(String, nullable=True, index=True)
    description = Column(Text, nullable=True, index=True)
    creation_time = Column(DateTime, server_default=func.now())


