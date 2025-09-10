# KeysightMSOX4154A.py

import pyvisa
from colorama import init, Fore, Style
try:
    from .loading import *
except Exception:
    from loading import *

_ERROR_STYLE = Fore.RED + Style.BRIGHT + "\rError! "
_SUCCESS_STYLE = Fore.GREEN + Style.BRIGHT  + "\r"
_DELAY = 0.1

class KeysightMSOX4154A:
    def __init__(self, auto_connect=True):
        init(autoreset=True)

        self.rm = pyvisa.ResourceManager()
        self.address = None
        self.instrument = None
        self.loading = loading()
        self.status = "Not Connected"

        if auto_connect:
            self.connect()

    def connect(self):
        resources = self.rm.list_resources()
        for resource in resources:
            if 'MY56' in resource:  # adjust if needed
                self.address = resource
                break

        if self.address is None:
            raise ConnectionError(_ERROR_STYLE + "Keysight MSOX4154A Oscilloscope not found.")

        try:
            inst = self.rm.open_resource(self.address)

            # Important defaults for this scope & binary transfers
            inst.timeout = 20000                # 20 s; screenshots can be slow
            inst.chunk_size = 102_400           # allow larger USB chunks
            inst.write_termination = '\n'       # SCPI writes are line-terminated
            inst.read_termination = None        # **NO** termination for binary data
            # If your VISA backend balks at None, use '' (empty string)

            # Optional: reduce SCPI headers noise
            try:
                inst.write(':SYSTem:HEADer OFF')
            except Exception:
                pass  # some firmwares ignore this

            self.instrument = inst
            self.status = "Connected"
            print(_SUCCESS_STYLE + f"Connected to Keysight MSOX4154A Oscilloscope at {self.address}")

        except Exception as e:
            error_message = f"Failed to connect to Keysight MSOX4154A Oscilloscope at {self.address}: {e}"
            raise ConnectionError(_ERROR_STYLE + error_message)

    def disconnect(self):
        if self.instrument is not None:
            self.instrument.close()
            print(f"\rDisconnected from Keysight MSOX4154A Oscilloscope at {self.address}")
            self.status = "Not Connected"

    def get(self, item):
        items = {
            "screenshot": self.get_screenshot
        }
        if item in items:
            return items[item]()
        else:
            raise ValueError(_ERROR_STYLE + f"Invalid item: {item} request to Keysight MSOX4154A Oscilloscope")

        def get_screenshot(self, inksaver: bool = False):
        """
        Captures a screenshot from the oscilloscope and returns it as PNG image data.

        Args:
            inksaver (bool, optional): If True, capture in inksaver mode 
                                       (less ink/toner when printed). Defaults to False.

        Returns:
            bytes: The PNG image data.
        """
        if self.instrument is None:
            raise ConnectionError(_ERROR_STYLE + "Not connected to Keysight MSOX4154A Oscilloscope.")

        try:
            # Choose SCPI command based on inksaver flag
            mode = "INKSaver" if inksaver else "COLor"

            data = self.instrument.query_binary_values(
                f":DISPlay:DATA? PNG,{mode}",
                datatype='B',
                is_big_endian=True,
                container=bytearray,
                chunk_size=102_400,
                delay=0
            )
            return bytes(data)

        except pyvisa.errors.VisaIOError as e:
            tips = " (Tips: increase timeout, ensure read_termination=None, use query_binary_values.)"
            raise RuntimeError(_ERROR_STYLE + f"Failed to capture screenshot: {e}{tips}")
        except Exception as e:
            raise RuntimeError(_ERROR_STYLE + f"Failed to capture screenshot: {e}")