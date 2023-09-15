from typing import Optional, Any
from datetime import datetime, timezone, date, time
from enum import Enum
import hashlib
import requests


class EvChargerStatus(Enum):
	AVAILABLE = 1
	PREPARING = 2
	CHARGING = 3
	SUSPENDED_CHARGER = 4
	SUSPENDED_VEHICLE = 5
	FINISHING = 6
	FAULT = 7


class ApiResponseException(Exception):
	def __init__(self, message, response):
		super().__init__(message)

		self.response = response


class AlphaESS(object):

	_GET = "GET"
	_POST = "POST"

	_API_ENDPOINT = "https://openapi.alphaess.com/api"
	_API_TIMEOUT = 30


	def __init__(self, app_id: str, app_secret: str, serial_number: Optional[str] = None) -> None:
		self._app_id = app_id
		self._app_secret = app_secret
		self._serial_number = serial_number


	def for_device(self, serial_number: str) -> Any:
		return AlphaESS(self._app_id, self._app_secret, serial_number)


	def _get_serial_number(self, serial_number: Optional[str] = None) -> Optional[str]:
		if serial_number is not None:
			return serial_number

		return self._serial_number or None  # for mypy


	def _get_query_params(self, serial_number: Optional[str] = None, data: dict = {}) -> dict:
		return {**data, "sysSn": self._get_serial_number(serial_number)}


	def _datetime_to_timestamp(self, timestamp: datetime) -> int:
		return str(int(timestamp.timestamp()))


	def _sign_request(self, timestamp: datetime) -> str:
		s = self._app_id + self._app_secret + self._datetime_to_timestamp(timestamp)

		return hashlib.sha512(s.encode("utf-8")).hexdigest()


	def _make_request(self, method: str, path: str, query: Optional[dict] = None, body: Optional[dict] = None):
		timestamp = datetime.now(timezone.utc)

		r = requests.request(
			method,
			url=self._API_ENDPOINT + path,
			params=query or None,
			headers={
				"appId": self._app_id,
				"timeStamp": self._datetime_to_timestamp(timestamp),
				"sign": self._sign_request(timestamp)
			},
			json=body
		)

		r.raise_for_status()

		result = r.json()

		if "code" not in result:
			raise ApiResponseException("Unknown API response (missing 'code' field)", result)

		if result["code"] != 200:
			raise ApiResponseException("Invalid API response (" + (result["msg"] or "no error message provided by API") + ")", result)

		return r.json()["data"]


	def _validate_percentage(self, decimal: float) -> None:
		assert decimal >= 0, "Percentage cannot be below 0%"
		assert decimal <= 1, "Percentage must be expressed as a decimal between [0, 1]"


	def _validate_time(self, period: time) -> None:
		assert period.minute % 15 == 0, "Time must be specified in 15-minute intervals"


	# Obtain the SN of the charging pile according to the SN, and set the model
	def get_ev_charger_settings(self, serial_number: Optional[str] = None) -> list[dict]:
		return self._make_request(
			self._GET, "/getEvChargerConfigList",
			query=self._get_query_params(serial_number)
		)


	# Obtain the current setting of charging pile household according to SN
	def get_ev_charger_current_draw_settings(self, serial_number: Optional[str] = None) -> float:
		return self._make_request(
			self._GET, "/getEvChargerCurrentsBySn",
			query=self._get_query_params(serial_number)
		)["currentsetting"]


	# Set charging pile household current setting according to SN
	def set_ev_charger_current_draw_settings(self, current_draw: float, serial_number: Optional[str] = None) -> dict:
		return self._make_request(
			self._GET, "/setEvChargerCurrentsBySn",
			query=self._get_query_params(serial_number, {"currentsetting": current_draw})
		)


	# Obtain charging pile status according to SN+charging pile SN
	def get_ev_charger_status(self, charger_serial_number: str, serial_number: Optional[str] = None) -> list[EvChargerStatus]:
		return [EvChargerStatus(x) for x in self._make_request(
			self._GET, "/getEvChargerStatusBySn",
			query=self._get_query_params(serial_number, {"evchargerSn": charger_serial_number})
		)]


	# According to SN+ charging pile SN remote control charging pile to start charging/stop charging
	def control_ev_charger(self, charger_serial_number: str, charging: bool, serial_number: Optional[str] = None) -> dict:
		return self._make_request(
			self._POST, "remoteControlEvCharger",
			body=self._get_query_params(serial_number, {
				"evchargerSn": charger_serial_number,
				"controlMode": int(charging)
			})
		)


	# According SN to get System Summary data
	def get_system_summary(self, serial_number: Optional[str] = None) -> dict:
		return self._make_request(
			self._GET, "/getSumDataForCustomer",
			query=self._get_query_params(serial_number)
		)


	# According to SN to get system list data
	def list_systems(self) -> list[dict]:
		return self._make_request(self._GET, "/getEssList")


	# According SN to get real-time power data
	def get_realtime_power_usage(self, serial_number: Optional[str] = None) -> dict:
		return self._make_request(
			self._GET, "/getLastPowerData",
			query=self._get_query_params(serial_number)
		)


	# According SN to get system power data
	def get_historical_power_usage(self, date: date, serial_number: Optional[str] = None) -> dict:
		return self._make_request(
			self._GET, "/getOneDayPowerBySn",
			query=self._get_query_params(serial_number, {"queryDate": date.isoformat()})
		)


	# According SN to get System Energy Data
	def get_historical_energy_usage(self, date: date, serial_number: Optional[str] = None) -> dict:
		return self._make_request(
			self._GET, "/getOneDateEnergyBySn",
			query=self._get_query_params(serial_number, {"queryDate": date.isoformat()})
		)


	# According SN to get charging setting information
	def get_charging_settings(self, serial_number: Optional[str]) -> dict:
		return self._make_request(
			self._GET, "/getChargeConfigInfo",
			query=self._get_query_params(serial_number)
		)


	# According SN to Set charging information
	def set_charging_settings(
		self, stop_level: float, use_grid: bool, first_period: tuple[time, time],
		second_period: tuple[time, time], serial_number: Optional[str]) -> dict:

		self._validate_percentage(stop_level)
		self._validate_time(first_period[0])
		self._validate_time(first_period[1])
		self._validate_time(second_period[0])
		self._validate_time(second_period[1])

		body = self._get_query_params(serial_number, {
			"batHighCap": stop_level,
			"gridCharge": int(use_grid),
			"timeChaf1": first_period[0].isoformat("minutes"),
			"timeChae1": first_period[1].isoformat("minutes"),
			"timeChaf2": second_period[0].isoformat("minutes"),
			"timeChae2": second_period[1].isoformat("minutes"),
		})

		return self._make_request(self._POST, "/updateChargeConfigInfo", body=body)


	# According to SN discharge setting information
	def get_discharging_settings(self, serial_number: Optional[str]) -> dict:
		return self._make_request(
			self._GET, "/getDisChargeConfigInfo",
			query=self._get_query_params(serial_number)
		)


	# According SN to Set charging information
	def set_discharging_settings(
		self, stop_level: float, enable_time_control: bool, first_period: tuple[time, time],
		second_period: tuple[time, time], serial_number: Optional[str]) -> dict:

		self._validate_percentage(stop_level)
		self._validate_time(first_period[0])
		self._validate_time(first_period[1])
		self._validate_time(second_period[0])
		self._validate_time(second_period[1])

		body = self._get_query_params(serial_number, {
			"batUseCap": stop_level,
			"ctrDis": int(use_grid),
			"timeDisf1": first_period[0].isoformat("minutes"),
			"timeDise1": first_period[1].isoformat("minutes"),
			"timeDisf2": second_period[0].isoformat("minutes"),
			"timeDise2": second_period[1].isoformat("minutes"),
		})

		return self._make_request(self._POST, "/updateDisChargeConfigInfo", body=body)


	# According to SN get the check code according to SN
	def get_verification_code(self, check_code: str, serial_number: Optional[str] = None) -> dict:
		return self._make_request(
			self._GET, "/getVerificationCode",
			query=self._get_query_params(serial_number, {"checkCode": check_code})
		)


	# According to SN and check code Bind the system bind the system
	def bind_system(self, verification_code: str, serial_number: Optional[str] = None) -> dict:
		return self._make_request(
			self._POST, "/bindSn",
			body=self._get_query_params(serial_number, {"code": verification_code})
		)


	# According to SN and check code Unbind the system
	def unbind_system(self, serial_number: Optional[str] = None) -> dict:
		return self._make_request(
			self._POST, "/unBindSn",
			body=self._get_query_params(serial_number)
		)
