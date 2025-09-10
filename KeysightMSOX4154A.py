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

    def get_screenshot(self):
        if self.instrument is None:
            raise ConnectionError(_ERROR_STYLE + "Not connected to Keysight MSOX4154A Oscilloscope.")

        try:
            # Ask the scope to format PNG and send display data as a definite-length binary block
            # Note: "COLOR" spelling must match the scope's SCPI (Keysight uses COLor or COLOR; both typically work)
            # The helper returns an array of uint8; we collect into a bytearray for speed then convert to bytes.
            data = self.instrument.query_binary_values(
                ":DISPlay:DATA? PNG,COLor",
                datatype='B',                # bytes
                is_big_endian=True,          # binary block header uses ASCII length; endianness irrelevant for bytes
                container=bytearray,         # efficient accumulation
                chunk_size=102_400,          # match/read in large chunks
                delay=0                      # no inter-chunk delay
            )
            return bytes(data)

        except pyvisa.errors.VisaIOError as e:
            # Common cause: timeout. Suggest remedies in the error message.
            tips = (
                " (Tips: ensure read_termination=None, increase timeout, and use query_binary_values for the PNG block.)"
            )
            raise RuntimeError(_ERROR_STYLE + f"Failed to capture screenshot: {e}{tips}")
        except Exception as e:
            raise RuntimeError(_ERROR_STYLE + f"Failed to capture screenshot: {e}")