import json
import aiohttp
import asyncio
from aiohttp import request, web
from server import engine, Base, app
from models import Advertisements
from models import Advertisements, Session
import requests
from schema import CreateAdvertisements, PatchAdvertisements
from server import HttpError, get_advertisements, validate
from sqlalchemy.exc import IntegrityError


class AdvertisementsView(web.View):

    @property
    def session(self):
        return self.request['session']
    
    @property
    def advertisements_id(self): 
        return int(self.request.match_info['advertisements_id'])

    async def get(self):

        advertisement = await get_advertisements(self.advertisements_id, self.session)
        return web.json_response({
            'id': advertisement.id,
            'header': advertisement.header,
            'description': advertisement.description,
            'creation_time': advertisement.creation_time.isoformat(),
            'owner': advertisement.owner
        })


    async def post(self):

        json_data = validate(await self.request.json(), CreateAdvertisements)
        with Session as session:
            new_advertisement = Advertisements(**json_data)
            try:
                self.request['session'].add(new_advertisement)
                await self.request['session'].commit()
            except IntegrityError as err:
                raise web.HTTPConflict(
                    text=json.dumps({'advertisement':'advertisement already exist'}),
                    content_type='application/json')
                return web.json_response({
                    'id': new_advertisement.id
                                        })


    async def patch(self):

        json_data = validate(await request.json, PatchAdvertisements)
        advertisement = get_advertisements(self.advertisements_id, self.session)
        for field, value in json_data.items():
            setattr(advertisement, field, value)
        await self.session.commit()

        return web.json_response({
            'header': advertisement.header,
            'description': advertisement.description,
            'creation_time': advertisement.creation_time.isoformat(),
            'owner': advertisement.owner
        })

    async def delete(self):
 
        advertisement = get_advertisements(self.advertisements_id, self.session)
        await self.session.delete(advertisement)
        await self.session.commit()

        return web.json_response({
            'status': 'success'
        })
