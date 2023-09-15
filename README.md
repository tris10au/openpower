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
	print("Currently feeding in:", api.for_device(device["sysSn"]).get_realtime_power_usage()["pgrid"])
```

## Methods

### Constructor: `AlphaESS(app_id: str, app_secret: str, device_serial_number: str = None) -> AlphaESS`
**Parameters:**
- `app_id`: (str) (required) The app ID of your developer account
- `app_secret`: (str) (required) The app secret of your developer account
- `device_serial_number`: (str) (optional) If specified, this will be used as the default serial number for methods related to a specific device, if none is specified in the method.

### `for_device(serial_number: str)`
A convenience wrapper that clones the current instance and sets the serial number so that further calls do not need the serial number passed in. Every device-specified method can have the serial number provided in the method, in the class constructor or using this method.
**Parameters:**
- `serial_number`: The serial number of the device to scope future requests to, available from `list_systems()`

**Returns:**
A new instance of `AlphaESS` with the serial number set

### `list_systems()`
Lists the available systems to monitor/control. Additional systems can be added via the web UI or by calling `get_verification_code()` and `bind_system()`. Systems can also be removed with `unbind_system()`. 
**Returns:**
A list of systems, uncluding serial number (`sysSn`) and model, that are whitelisted for this developer account

### `get_verification_code(check_code: str)`
This is the first step to "binding" (adding) a new system to the developer account to allow it to be monitored and controlled. It will send an enamil to the registered owner of the system with a verification code that can be used on `bind_system()`
**Parameters:**
- `check_code`: (str) (required) The check code shown on the battery/inverter's physical label below the serial number
- `serial_number` (str) (optional) The serial number of the battery/inverter. This can alternatively be passed in via the constructor or by using the `for_device()` helper method

**Returns:**
Nothing.

*Note that this method will email the battery/inverter's owner with a code, so check the the details thoroughly.*

### `bind_system(verification_code: str)`
Binds (adds) a battery/inverter to the developer's account to allow it to be monitored and controlled. This can only be done after calling `get_verification_code()` (or via the web UI).

**Parameters:**
- `verification_code`: (str) (required) The code which was sent via email to the registered owner when calling `get_verification_code()`. This is **not** the check code.
- `serial_number` (str) (optional) The serial number of the battery/inverter. This can alternatively be passed in via the constructor or by using the `for_device()` helper method

**Returns:**
Nothing. The system will now be visible when you call `list_systems()`

### `unbind_system()`
Unbind (remove) a battery/inverter from the developer account.
**Parameters:**
- `serial_number` (str) (optional) The serial number of the battery/inverter. This can alternatively be passed in via the constructor or by using the `for_device()` helper method

### `get_realtime_energy_usage()`
Gets the current power usage, typically in 30 second blocks.
**Parameters:**
- `serial_number` (str) (optional) The serial number of the battery/inverter. This can alternatively be passed in via the constructor or by using the `for_device()` helper method