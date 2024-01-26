from aiohttp import BasicAuth
import aiohttp
from typing import Any
import asyncio
import os


class TwilioRequestResource:
    def __init__(self, account_sid, auth_token):
        self._account_sid = account_sid
        self._auth_token = auth_token
        self.use_ssl = (
            False  # bool(os.getenv("KRISPCALL_APP_ENV") != "development")
        )

    async def post(self, url, payload=None) -> Any:
        try:
            auth = BasicAuth(
                login=self._account_sid, password=self._auth_token
            )
            async with aiohttp.ClientSession(auth=auth) as session:
                async with session.post(
                    url=url, data=payload, verify_ssl=self.use_ssl
                ) as resp:
                    response = await resp.json()
                    return response
        except Exception as E:
            raise E

    async def get(self, url) -> Any:
        async with aiohttp.ClientSession(
            loop=asyncio.get_event_loop(),
            connector=aiohttp.TCPConnector(ssl=False),
            auth=aiohttp.BasicAuth(
                login=self._account_sid, password=self._auth_token
            ),
        ) as session:
            async with session.get(url) as resp:
                response = await resp.json()
                return response

    async def delete(self, url) -> Any:
        try:
            async with aiohttp.ClientSession(
                loop=asyncio.get_event_loop(),
                auth=aiohttp.BasicAuth(
                    login=self._account_sid, password=self._auth_token
                ),
            ) as session:
                async with session.delete(
                    url, verify_ssl=self.use_ssl
                ) as resp:
                    response = await resp.json()
                    return response
        except Exception as E:
            raise E
