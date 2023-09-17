from typing import Optional, Any
from enum import Enum
import requests
from datetime import date, datetime, timedelta
from dataclasses import dataclass


class State(Enum):
	NEW_SOUTH_WALES = "nsw"
	QUEENSLAND = "qld"
	SOUTH_AUSTRALIA = "sa"
	VICTORIA = "vic"


@dataclass(frozen=True)
class Ratelimits(object):
	limit: int
	remaining: int
	reset: int
	policy: str
	refreshed: datetime

	
	def get_estimated_reset(self):
		return self.refreshed + timedelta(seconds=self.reset)


	def get_time_window(self):
		return int(self.policy.split("w=")[1])


class Amber(object):
	_API_ENDPOINT = "https://api.amber.com.au/v1"
	_API_TIMEOUT = 30

	_GET = "GET"
	_POST = "POST"

	def __init__(self, token: str, site: Optional[str] = None) -> None:
		self._token = token
		self._site = site


	def for_site(self, site: str) -> Any:
		return Amber(self._token, site)


	def _get_site(self, site: Optional[str] = None) -> Optional[str]:
		if site is not None:
			return site

		return self._site or None  # for mypy


	def _make_request(self, method: str, path: str, params: Optional[dict] = None, query: Optional[dict] = None) -> dict:
		if params is not None:
			path = path.format(**params)

		r = requests.request(
			method,
			url=self._API_ENDPOINT + path,
			params=query,
			headers={
				"Authorization": "Bearer " + self._token
			},
			timeout=self._API_TIMEOUT
		)

		if r.headers and "ratelimit-limit" in r.headers:
			self._ratelimit = Ratelimits(
				limit=int(r.headers["ratelimit-limit"]),
				remaining=int(r.headers["ratelimit-remaining"]),
				reset=int(r.headers["ratelimit-reset"]),
				policy=r.headers["ratelimit-policy"],
				refreshed=datetime.now()
			)

		r.raise_for_status()

		result = r.json()

		return result


	def get_ratelimits(self) -> Optional[Ratelimits]:
		return self._ratelimit or None


	# Returns the current percentage of renewables in the grid
	def get_current_renewables(self, state: State, previous: Optional[int] = None, next: Optional[int] = None, resolution: Optional[int] = None) -> list[dict]:
		return self._make_request(
			self._GET, "/state/{state}/renewables/current",
			params={"state": state.value},
			query={"next": next, "previous": previous, "resolution": resolution}
		)


	# Return all sites linked to your account
	def list_sites(self):
		return self._make_request(self._GET, "/sites")


	# Returns all the prices between the start and end dates
	def get_prices(self, start: Optional[date] = None, end: Optional[date] = None, resolution: int = None, site: Optional[str] = None) -> list[dict]:
		return self._make_request(
			self._GET, "/sites/{id}/prices", params={"id": self._get_site(site)},
			query={
				"startDate": start.isoformat() if start else None,
				"endDate": end.isoformat() if end else None,
				"resolution": resolution
			}
		)


	# Returns the current price
	def get_current_prices(self, previous: Optional[int] = None, next: Optional[int] = None, resolution: int = None, site: Optional[str] = None) -> list[dict]:
		return self._make_request(
			self._GET, "/sites/{id}/prices/current", params={"id": self._get_site(site)},
			query={
				"next": next, "previous": previous, "resolution": resolution
			}
		)


	# Returns all usage data between the start and end dates
	def get_usage(self, start: Optional[date] = None, end: Optional[date] = None, resolution: int = None, site: Optional[str] = None) -> list[dict]:
		return self._make_request(
			self._GET, "/sites/{id}/usage", params={"id": self._get_site(site)},
			query={
				"startDate": start.isoformat() if start else None,
				"endDate": end.isoformat() if end else None,
				"resolution": resolution
			}
		)

