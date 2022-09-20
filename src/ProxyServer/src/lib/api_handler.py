"""Request functions for Player API."""

import requests


class APIHandler:
    def __init__(
        self, authorization: str, player_api_base_url: str, stats_api_base_url: str
    ):
        self.headers = {"authorization": authorization}
        self.player_api_base_url = player_api_base_url
        self.stats_api_base_url = stats_api_base_url

    def fill_in(self, username: str, ip_address: str) -> bool:
        """Ask a bot to rejoin the server once a user leaves, while attempting to log this event."""

        try:
            requests.get(
                self.stats_api_base_url + "/log/{}/{}".format(username, ip_address),
                headers=self.headers,
            )
        except:
            pass

        return requests.get(
            self.player_api_base_url + "/fill_in", headers=self.headers
        ).ok

    def sit_out(self, username: str, ip_address: str) -> bool:
        """Request a bot to leave so a user can join, while attempting to log this event."""

        try:
            requests.get(
                self.stats_api_base_url + "/log/{}/{}".format(username, ip_address),
                headers=self.headers,
            )
        except:
            pass

        return requests.get(
            self.player_api_base_url + "/sit_out", headers=self.headers
        ).ok
