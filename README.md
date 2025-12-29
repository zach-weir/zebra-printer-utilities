## Zebra Printer Utilities
Collection of scripts to manage Zebra label printers remotely. 

## Pre-requisites
- Python v3.14+
- Mac or Linux computer
    - *Windows support is TBD (currently only works on Mac/Linux computers)*
- Printer name or IP address

## Supported devices
- ZD621
- ZQ620
- ZQ620 Plus
- ZQ630
- ZT410
- ZT411

## Utility
### get_info.py
Query printer to gather information such as friendly name, MAC address, printer firmware version, etc.

### set_configs.py
Send golden CONFIG.SGD file to printers to apply standard settings if any have been changed.

### update_firmware.py
Send firmware files (in chunks) to update firmware version on printers.