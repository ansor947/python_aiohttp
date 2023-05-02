from cgitb import handler
import json
import aiohttp
import asyncio
from aiohttp import request, web, Handler
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_async_engine
from sqlalchemy.ext import IntegrityError
from models import Advertisements, Session
from views import AdvertisementsView
from schema import PatchAdvertisements, CreateAdvertisements
from typing import Type
import pydantic

app = web.Application()

PG_DSN = 'postgresql+asyncpg://postgres:2345@127.0.0.1:5431/aiohttp'

engine = create_async_engine(PG_DSN)
Base = declarative_base()
Session = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)


async def orm_context(app):
    async with engine.begin as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.disponse()



@web.middleware
async def session_midlewear():
    async with Session as session:
        request['session'] = session
        response = await handler(request)
        return response


async def validate(json_data: dict, model_class: Type[CreateAdvertisements] | Type[CreateAdvertisements]):
    try:
        model_item = model_class(**json_data)
        return model_item.dict(exclude_none=True)
    except pydantic.ValidationError as err:
        raise web.HTTPConflict(content_type='application/json')


class HttpError(Exception):

    async def __init__(self, status_code: int, message: dict | list | str):
        status_code = self.status_code
        message = self.message


@app.errorhandler
async def error_handler(error: HttpError):
    response = web.json_response({'status': 'error', 'message': error.message})
    response.status_code = error.status_code

    return response


async def get_advertisements(advertisements_id: int, session: Session):
    advertisement = session.get(Advertisements, advertisements_id)
    if advertisement is None:
        raise web.HTTPNotFound(
            text=json.dumps({'error':'advertisement not found'}),
            content_type='application/json')

    return advertisement


app.add_routes([
     web.get('/advertisements/{advertisements_id:\d+}', AdvertisementsView),
     web.patch('/advertisements/{advertisements_id:\d+}', AdvertisementsView),
     web.post('/advertisements/', AdvertisementsView),
     web.delete('/advertisements/{advertisements_id:\d+}', AdvertisementsView)
              ])


app.cleanup_ctx.append(orm_context)
app.midlewears.append(session_midlewear)

    

if __name__ == '__main__':
    web.run_app(app)




















