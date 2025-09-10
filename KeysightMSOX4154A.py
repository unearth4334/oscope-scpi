#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#   @file KeysightMSOX4154A.py
#   @brief Connect to a Keysight MSOX4154A Oscilloscope and capture screenshots.
#   @date 18-May-2023 (updated)
#   @author Stefan Damkjar
#
#   Licensed to the Apache Software Foundation (ASF) under one
#   or more contributor license agreements.  See the NOTICE file
#   distributed with this work for additional information
#   regarding copyright ownership.  The ASF licenses this file
#   to you under the Apache License, Version 2.0 (the
#   "License"); you may not use this file except in compliance
#   with the License.  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing,
#   software distributed under the License is distributed on an
#   "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
#   KIND, either express or implied.  See the License for the
#   specific language governing permissions and limitations
#   under the License.

from __future__ import annotations

# Imports
import pyvisa
from colorama import init, Fore, Style
from typing import Optional, Any, Dict

try:
    # If used as a package/module
    from .loading import loading
except Exception:
    # If run as a flat script alongside loading.py
    try:
        from loading import loading
    except Exception:
        # Provide a tiny no-op fallback so the class still works without loading.py
        class loading:  # type: ignore
            def __init__(self, *_, **__): ...
            def start(self, *_, **__): ...
            def stop(self, *_, **__): ...

# Constants and global variables
_ERROR_STYLE = Fore.RED + Style.BRIGHT + "\rError! "
_SUCCESS_STYLE = Fore.GREEN + Style.BRIGHT + "\r"
_DELAY = 0.1  # reserved for future use

"""
Establishes a connection to the Keysight MSOX4154A Oscilloscope and provides methods for interfacing.

Example usage:
    osc = KeysightMSOX4154A()
    data = osc.get_screenshot(inksaver=True)
    with open("screen.png", "wb") as f:
        f.write(data)
"""
class KeysightMSOX4154A:
    """
    Keysight MSOX4154A SCPI interface via PyVISA.
    """

    def __init__(
        self,
        auto_connect: bool = True,
        resource_hint: str = "MY56",      # serial prefix for MSOX4154A; adjust if needed
        timeout_ms: int = 20000,          # screenshots can take seconds
        chunk_size: int = 102_400,        # bigger chunks reduce overhead
    ):
        """
        Initialize the oscilloscope interface.

        Args:
            auto_connect: Attempt to connect immediately.
            resource_hint: Substring to match in VISA resource string (e.g., 'USB::...MY56...').
            timeout_ms: VISA I/O timeout in milliseconds.
            chunk_size: VISA chunk size for binary transfers.
        """
        init(autoreset=True)

        self.rm: pyvisa.ResourceManager = pyvisa.ResourceManager()
        self.address: Optional[str] = None
        self.instrument: Optional[pyvisa.resources.MessageBasedResource] = None
        self.loading = loading()

        self.status: str = "Not Connected"
        self._resource_hint = resource_hint
        self._timeout_ms = timeout_ms
        self._chunk_size = chunk_size

        if auto_connect:
            self.connect()

    def _discover_resource(self) -> Optional[str]:
        """Find a VISA resource that contains the hint substring."""
        resources = self.rm.list_resources()
        for res in resources:
            if self._resource_hint in res:
                return res
            # also accept common Keysight USBTMC patterns
            if "USB0::0x0957" in res and "::INSTR" in res:
                return res
        return None

    def connect(self):
        """
        Establish a connection to the Keysight MSOX4154A Oscilloscope.

        Raises:
            ConnectionError: If unable to connect.
        """
        self.address = self._discover_resource()

        if self.address is None:
            raise ConnectionError(_ERROR_STYLE + "Keysight MSOX4154A Oscilloscope not found.")

        try:
            inst = self.rm.open_resource(self.address)

            # Recommended defaults for binary transfers (PNG screenshots):
            inst.timeout = self._timeout_ms           # e.g., 20000 ms
            inst.chunk_size = self._chunk_size        # e.g., 100 KB
            inst.write_termination = '\n'             # SCPI writes are line-terminated
            inst.read_termination = None              # **no** termination for binary block reads

            # Optional: reduce SCPI headers noise (some firmwares ignore this)
            try:
                inst.write(':SYSTem:HEADer OFF')
            except Exception:
                pass

            self.instrument = inst
            self.status = "Connected"
            print(_SUCCESS_STYLE + f"Connected to Keysight MSOX4154A Oscilloscope at {self.address}")

        except Exception as e:
            raise ConnectionError(
                _ERROR_STYLE + f"Failed to connect to Keysight MSOX4154A Oscilloscope at {self.address}: {e}"
            )

    def disconnect(self):
        """
        Disconnect from the oscilloscope.
        """
        if self.instrument is not None:
            try:
                self.instrument.close()
            finally:
                print(f"\rDisconnected from Keysight MSOX4154A Oscilloscope at {self.address}")
                self.instrument = None
                self.status = "Not Connected"

    def get(self, item: str, **kwargs: Any):
        """
        Generic getter that dispatches to specific methods.

        Currently supported:
            - "screenshot" → get_screenshot(**kwargs)

        Example:
            osc.get("screenshot", inksaver=True)

        Raises:
            ValueError: If an invalid item is requested.
        """
        items: Dict[str, Any] = {
            "screenshot": self.get_screenshot,
        }

        if item in items:
            return items[item](**kwargs)
        else:
            raise ValueError(_ERROR_STYLE + f"Invalid item: {item} request to Keysight MSOX4154A Oscilloscope")

    def get_screenshot(self, inksaver: bool = False) -> bytes:
        """
        Capture a screenshot as PNG bytes.

        Args:
            inksaver: If True, capture in inksaver mode ("PNG,INKSaver") which reduces color
                      density for printing. Default False (full color: "PNG,COLor").

        Returns:
            PNG image data as bytes.

        Raises:
            RuntimeError: On transfer/SCPI errors.
            ConnectionError: If not connected.
        """
        if self.instrument is None:
            raise ConnectionError(_ERROR_STYLE + "Not connected to Keysight MSOX4154A Oscilloscope.")

        try:
            # Ensure acquisition isn't blocking (optional—but can help throughput)
            # self.instrument.write(":STOP")

            mode = "INKSaver" if inksaver else "COLor"

            # Use PyVISA helper to parse the definite-length binary block.
            data = self.instrument.query_binary_values(
                f":DISPlay:DATA? PNG,{mode}",
                datatype='B',               # raw bytes
                is_big_endian=True,         # irrelevant for bytes but required by API
                container=bytearray,        # efficient accumulation
                chunk_size=self._chunk_size,
                delay=0
            )
            return bytes(data)

        except pyvisa.errors.VisaIOError as e:
            tips = " (Tips: ensure read_termination=None, increase timeout, and use query_binary_values.)"
            raise RuntimeError(_ERROR_STYLE + f"Failed to capture screenshot: {e}{tips}")
        except Exception as e:
            raise RuntimeError(_ERROR_STYLE + f"Failed to capture screenshot: {e}")


# If run directly, perform a quick self-test screenshot to current directory (optional).
if __name__ == "__main__":
    import datetime
    import os
    import sys

    outdir = sys.argv[1] if len(sys.argv) > 1 else "."
    os.makedirs(outdir, exist_ok=True)
    os.chdir(outdir)
    print(f"Output directory: {os.getcwd()}")

    osc = KeysightMSOX4154A(auto_connect=True)

    try:
        # Full color
        ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        fname = f"screenshot_{ts}.png"
        print(f"Saving screenshot to {fname}")
        with open(fname, "wb") as f:
            f.write(osc.get_screenshot())

        # Inksaver example (disabled by default; uncomment to test)
        # ts2 = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        # fname2 = f"screenshot_inksaver_{ts2}.png"
        # print(f"Saving inksaver screenshot to {fname2}")
        # with open(fname2, "wb") as f2:
        #     f2.write(osc.get_screenshot(inksaver=True))

    finally:
        osc.disconnect()