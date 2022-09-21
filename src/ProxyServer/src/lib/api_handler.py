"""Request functions for Player API."""
import aiohttp
from typing import Optional


class APIHandler:
    def __init__(
        self, authorization: str, player_api_base_url: str, stats_api_base_url: str
    ):
        self.headers = {"authorization": authorization}

        self.player_api_base_url = player_api_base_url
        self.stats_api_base_url = stats_api_base_url

        self.log_url = self.stats_api_base_url + "/log/{}/{}"

    async def fill_in(self, username: str, ip_address: Optional[str] = None) -> bool:
        """Ask a bot to rejoin the server once a user leaves, while attempting to log this event."""

        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(
                    self.log_url.format(username, ip_address), headers=self.headers
                ) as response:
                    ...
            except:
                pass
            async with session.get(
                self.player_api_base_url + "/fill_in", headers=self.headers
            ) as response:
                if response.status >= 200 and response.status <= 299:
                    return True
                return False

    async def sit_out(self, username: str, ip_address: Optional[str] = None) -> bool:
        """Request a bot to leave so a user can join, while attempting to log this event."""

        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(
                    self.log_url.format(username, ip_address), headers=self.headers
                ) as response:
                    ...
            except:
                pass
            async with session.get(
                self.player_api_base_url + "/sit_out", headers=self.headers
            ) as response:
                if response.status >= 200 and response.status <= 299:
                    return True
                return False

    async def join_all(self) -> bool:
        """Request all bots to join the server."""

        async with aiohttp.ClientSession() as session:
            async with session.get(
                self.player_api_base_url + "/join_all", headers=self.headers
            ) as response:
                if response.status >= 200 and response.status <= 299:
                    return True
                return False
