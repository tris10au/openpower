# openpower
Python library for monitoring and controlling solar panels, inverters, batteries and power retailers.  an AlphaESS battery/inverter using the AlphaCloud opne API

## Supported Systems
### Retailers
- Amber (Australia)

### Batteries
- AlphaESS (using the Open API)

### Inverters
- AlphaESS (using the Open API)
- Goodwe (using the Open API) - *in development*

# AlphaESS
## How to use

### 1. Sign up for an open API account
Register at https://open.alphaess.com/ for a (free) account to get your Developer ID (AppID) and Developer Secret (AppSecret).

Once registered, add your battery/inverter to the developer account via the web UI. (Adding a battery/inverter can also be automated using the `get_verification_code()` and `bind_system()` methods)

### 2. Get started
```
from openpower.alphaess import AlphaESS

APP_ID = "the AppID from step 1"
APP_SECRET = "the AppSecret from step 1"

api = AlphaESS(app_id=APP_ID, app_secret=APP_SECRET)

devices = api.list_systems()
print(devices)

for device in devices:
	print("Currently consuming/feeding in:", api.for_device(device["sysSn"]).get_realtime_power_usage()["pgrid"])
```

## Methods

### Constructor: `AlphaESS(app_id: str, app_secret: str, device_serial_number: str = None)`

**Parameters:**
- `app_id`: (str) (required) The app ID of your developer account
- `app_secret`: (str) (required) The app secret of your developer account
- `device_serial_number`: (str) (optional) If specified, this will be used as the default serial number for methods related to a specific device, if none is specified in the method.

### Devices
#### `for_device(serial_number: str)`
A convenience wrapper that clones the current instance and sets the serial number so that further calls do not need the serial number passed in. Every device-specified method can have the serial number provided in the method, in the class constructor or using this method.

**Parameters:**
- `serial_number`: The serial number of the device to scope future requests to, available from `list_systems()`

**Returns:**
A new instance of `AlphaESS` with the serial number set

#### `list_systems()`
Lists the available systems to monitor/control. Additional systems can be added via the web UI or by calling `get_verification_code()` and `bind_system()`. Systems can also be removed with `unbind_system()`. 

**Returns:**
A list of systems, uncluding serial number (`sysSn`) and model, that are whitelisted for this developer account

#### `get_verification_code(check_code: str)`
This is the first step to "binding" (adding) a new system to the developer account to allow it to be monitored and controlled. It will send an enamil to the registered owner of the system with a verification code that can be used on `bind_system()`

**Parameters:**
- `check_code`: (str) (required) The check code shown on the battery/inverter's physical label below the serial number
- `serial_number` (str) (optional) The serial number of the battery/inverter. This can alternatively be passed in via the constructor or by using the `for_device()` helper method

**Returns:**
Nothing.

*Note that this method will email the battery/inverter's owner with a code, so check the details thoroughly.*

#### `bind_system(verification_code: str)`
Binds (adds) a battery/inverter to the developer's account to allow it to be monitored and controlled. This can only be done after calling `get_verification_code()` (or via the web UI).

**Parameters:**
- `verification_code`: (str) (required) The code which was sent via email to the registered owner when calling `get_verification_code()`. This is **not** the check code.
- `serial_number` (str) (optional) The serial number of the battery/inverter. This can alternatively be passed in via the constructor or by using the `for_device()` helper method

**Returns:**
Nothing. The system will now be visible when you call `list_systems()`

#### `unbind_system()`
Unbind (remove) a battery/inverter from the developer account.

**Parameters:**
- `serial_number` (str) (optional) The serial number of the battery/inverter. This can alternatively be passed in via the constructor or by using the `for_device()` helper method

**Returns**:
Nothing.

### Power Monitoring

#### `get_realtime_energy_usage()`
Gets the current power usage, typically in 30 second blocks.

**Parameters:**
- `serial_number` (str) (optional) The serial number of the battery/inverter. This can alternatively be passed in via the constructor or by using the `for_device()` helper method

**Returns:**
A dictionary of real-time data from the battery:

| Field | Description | In-App Equivalent | Unit |
|---|---|---|---|
| `ppv` | PV Power | Solar Power | W |
| `pload` | Power Load | Load | W |
| `soc` | Battery charge level | State of Charge | % [0...1] |
| `pgrid` | Grid Consumption (if negative, this is the feed-in value) | Grid Consumption / Feed-In | W |
| `pbat` | Power from battery (if negative, battery is charging) | Battery | W |
| `pev` | Total power of charging pile | ? | W |

#### `get_system_summary()`
Gets an overall summary of the system, including total power, CO2 savings, trees planted and profit/payback.

**Parameters:**
- `serial_number` (str) (optional) The serial number of the battery/inverter. This can alternatively be passed in via the constructor or by using the `for_device()` helper method

**Returns:**
A dictionary of fields (todo: document these in detail). All electricity values are in kWh, all % are [0...1], CO2 is in kg and `todayIncome` and `totalIncome` is in the currency specified by `moneyType`.

#### `get_historical_power_usage(date: date)`
Gets the power usage for a specific day

**Parameters:**
- `date` (datetime.date) The date to get data for
- `serial_number` (str) (optional) The serial number of the battery/inverter. This can alternatively be passed in via the constructor or by using the `for_device()` helper method

#### `get_historical_energy_usage(date: date)`
Gets the energy usage for a specific day (todo: document the difference between power and energy - this is evident in the returned fields)

**Parameters:**
- `date` (datetime.date) The date to get data for
- `serial_number` (str) (optional) The serial number of the battery/inverter. This can alternatively be passed in via the constructor or by using the `for_device()` helper method

### System Configuration
#### `get_charging_settings()`
Gets the charging settings

**Parameters:**
- `serial_number` (str) (optional) The serial number of the battery/inverter. This can alternatively be passed in via the constructor or by using the `for_device()` helper method

**Returns:**
| Field | Description |
|---|---|
| `batHighCap` | % to stop charging from grid at [0...1] |
| `gridCharge` | Whether to charge from the grid (0 or 1) |
| `timeChaf1` | Start time of charging period 1 (HH:mm, 24 hour time, must be a 15 min interval) |
| `timeChae1` | End time of charging period 1 (HH:mm, 24 hour time, must be a 15 min interval) |
| `timeChaf2` | Start time of charging period 2 (HH:mm, 24 hour time, must be a 15 min interval) |
| `timeChae2` | End time of charging period 2 (HH:mm, 24 hour time, must be a 15 min interval) |

#### `set_charging_settings(stop_level: float, use_grid: bool, first_period: tuple[datetime.time, datetime.time], second_period: tuple[datetime.time, datetime.time])`

**Parameters:**
- `stop_level` (float) % to stop charging from the grid at [0...1]
- `use_grid` (bool) True to charge from the grid, False not to
- `first_period` (tuple of `datetime.time`) The start and end time of charging period 1 (the minutes for both fields must be one of :00, :15, :30, :45)
- `second_period` (tuple of `datetime.time`) The start and end time of charging period 2 (the minutes for both fields must be one of :00, :15, :30, :45)
- `serial_number` (str) (optional) The serial number of the battery/inverter. This can alternatively be passed in via the constructor or by using the `for_device()` helper method

#### `get_discharging_settings()`
Gets the discharging settings

**Parameters:**
- `serial_number` (str) (optional) The serial number of the battery/inverter. This can alternatively be passed in via the constructor or by using the `for_device()` helper method

**Returns:**
| Field | Description |
|---|---|
| `batUseCap` | % to stop discharging at [0...1] |
| `ctrDis` | Whether to enable time-based discharge control (0 or 1) |
| `timeDisf1` | Start time of discharging period 1 (HH:mm, 24 hour time, must be a 15 min interval) |
| `timeDise1` | End time of charging period 1 (HH:mm, 24 hour time, must be a 15 min interval) |
| `timeDisf2` | Start time of discharging period 2 (HH:mm, 24 hour time, must be a 15 min interval) |
| `timeDise2` | End time of discharging period 2 (HH:mm, 24 hour time, must be a 15 min interval) |

#### `set_discharging_settings(stop_level: float, enable_time_control: bool, first_period: tuple[datetime.time, datetime.time], second_period: tuple[datetime.time, datetime.time])`

**Parameters:**
- `stop_level` (float) % to stop discharging at [0...1]
- `enable_time_control` (bool) True to use time-based discharging control, Flase not to
- `first_period` (tuple of `datetime.time`) The start and end time of discharging period 1 (the minutes for both fields must be one of :00, :15, :30, :45)
- `second_period` (tuple of `datetime.time`) The start and end time of discharging period 2 (the minutes for both fields must be one of :00, :15, :30, :45)
- `serial_number` (str) (optional) The serial number of the battery/inverter. This can alternatively be passed in via the constructor or by using the `for_device()` helper method


### EV Chargers
#### `get_ev_charger_list()`
Get a list of the the EV chargers in the battery system.

**Parameters:**
- `serial_number` (str) (optional) The serial number of the battery/inverter. This can alternatively be passed in via the constructor or by using the `for_device()` helper method

**Returns:**
A list of the EV chargers model and serial number.

#### `get_ev_charger_current_draw_settings()`
Get the total maximum EV current draw allowed.

**Parameters:**
- `serial_number` (str) (optional) The serial number of the battery/inverter. This can alternatively be passed in via the constructor or by using the `for_device()` helper method

**Returns:**
The maximum current, in Amps, as a float

#### `set_ev_charger_current_draw_settings(current_draw: float)`
Set the maximum EV current draw to `current_draw`

**Parameters:**
- `current_draw` (float) The maximum current draw, in Amps, as a float
- `serial_number` (str) (optional) The serial number of the battery/inverter. This can alternatively be passed in via the constructor or by using the `for_device()` helper method

**Returns:**
Nothing if succesful. As with all requests, an exception will be raised if an error occurs.

#### `get_ev_charger_status(charger_serial_number: str)`
Get the status of an EV charger

**Parameters:**
- `charger_serial_number` (str) The serial number to retrieve status for, see `get_ev_charger_list()`
- `serial_number` (str) (optional) The serial number of the battery/inverter. This can alternatively be passed in via the constructor or by using the `for_device()` helper method

#### `control_ev_charger(charger_serial_number: str, charging: bool)`
Enable or disable an EV charger

**Parameters:**
- `charger_serial_number` (str) The serial number to retrieve status for, see `get_ev_charger_list()`
- `charging` (bool) True to enable the charger, False to disable charging
- `serial_number` (str) (optional) The serial number of the battery/inverter. This can alternatively be passed in via the constructor or by using the `for_device()` helper method


# Amber
This is a direct implementation of [Amber's developer API](https://app.amber.com.au/developers/documentation/).

## How to use
### 1. Get a developer token
You must be an Amber customer to get a developer token.
1. Login to the customer portal via the web UI
2. In Settings, enable Developer Mode and refresh the page
3. In For Developers (which appears after step #2), generate an API token

### 2. Get started
```
from openapi.amber import Amber

api = Amber(token="your API token from step 1")

sites = api.list_sites()

for site in sites:
    print("Current prices are:", api.for_site(site["id"]).get_current_prices(previous=0, next=0))
```

## Methods

### Constructor: `Amber(token: str, site: Optional[str] = None)`

**Parameters:**
- `token` (str) The API token to use (from the developer portal)
- `site` (str) (optional) If specified, the default site ID to use if none is specified in the method and the `for_site()` helper method is not utilsied.

### API Helper Methods

#### `for_site(site: str)`
A convenience wrapper that clones the current instance and sets the site ID so that further calls do not need the site ID passed in. Every site-specified method can have the site ID provided in the method, in the class constructor or using this method.

**Parameters:**
- `site`: The site ID to scope future requests to, available from `list_sites()`

**Returns:**
A new instance of `Amber` with the site ID set

#### `get_ratelimits()`
If a previous API call has been made (excluding `get_current_renewables()`), this will provide the latest rate limit information to assist in throttling additional requests. Currently, Amber allows 50 requests per 5 minutes.

**Parameters:**
None.

**Returns:**
If an API request has been made previously, this returns an object with:
- `limit` The maximum allowed requests in the time window
- `remaining` The remaining requests allowed in the time window
- `reset` The number of seconds until the count will be reset
- `policy` The ratelimiting policy in effect
- `refreshed` (datetime.datetime) The time the rate limits were last retrieved (i.e. the tiem of the last API call)

In addition, there are two helper methods:
- `get_estimated_reset()` which returns a `datetime.datetime` of when the rate limit will reset. This could be in the past if `refreshed` is not recent.
- `get_time_window()` which returns the current time window used for rate limiting. This is done by crudely parsing the `policy` and could break if a more complex policy was implemented.

If there is no rate limit information yet, returns `None`

### Current Renewables
#### `get_current_renewables(state: State, previous: Optional[int], next: Optional[int], resolution: Optional[int])`
Gets the current % of renewables in the grid for a specific state. This request is not rate-limited and does not return rate-limit information so does not affect `get_ratelimits()`

**Parameters:**
- `state` (State) The state to get data for - see `list(State)` to get a list of allowed States
- `previous` (int) (optional) The number of prior data points to retrieve
- `next` (int) (optional) The number of future predictions to retrieve 
- `resolution` (int) (optional) The time resolution (in minutes) to retrieve. Currently only supports 30

**Returns:**
Information about the percentage of renewables in the grid

**Example:**
```
from openpower.amber import Amber, State


AMBER_TOKEN = "Your token here"

amber = Amber(AMBER_TOKEN)

print("Available states:", list(State))
print("Current renewables:", amber.get_current_renewables(State.VICTORIA, previous=0, next=0))
```

### Site-Specific Data
#### `list_sites()`
Gets a list of available sites linked to the current API token

**Parameters:**
None

**Returns:**
A list of sites with ID, NMI, status and network. The ID is used as the site ID in other methods. At current, it appears customers can have only one active site, but may have multiple sites if they've moved address, so it is best to filter the results by `status=active`.

#### `get_current_prices(previous: Optional[int], next: Optional[int], resolution: Optional[int], site: Optional[str])`
Get the current price of electricity on all channels. The results are supposed to be ordered by General, Controlled Load then Feed In (solar) however there have been times when this wasn't being done by Amber's API servers, so it is recommended to filter by channel

**Parameters:**
- `previous` (int) (optional) The number of prior data points to retrieve
- `next` (int) (optional) The number of future predictions to retrieve 
- `resolution` (int) (optional) The time resolution (in minutes) to retrieve. Currently only supports 30

**Returns:**
A list of channels and prices

#### `get_prices(start: Optional[date], end: Optional[date], resolution: int)`
Get historical price data for a site

**Parameters:**
- `start` (datetime.date) (optional) The first day to retrieve data for (inclusive), defaults to today
- `end` (datetime.date) (optional) The last day to retrieve data for (inclusive), defaults to today 
- `resolution` (int) (optional) The time resolution (in minutes) to retrieve. Currently only supports 5 or 30 (default)

**Returns:**
A list of pricing data for all channels. Note: This can take a very long time to return if a large amount of data is requested.

#### `get_usage(start: Optional[date], end: Optional[date], resolution: int)`
Get the usage data for a site

**Parameters:**
- `start` (datetime.date) (optional) The first day to retrieve data for (inclusive), defaults to today
- `end` (datetime.date) (optional) The last day to retrieve data for (inclusive), defaults to today 
- `resolution` (int) (optional) The time resolution (in minutes) to retrieve. Currently only supports 30 (default)

**Returns:**
A list of pricing data for all channels. Note: This can take a very long time to return if a large amount of data is requested. The documentation states it should be 30 days or less.

