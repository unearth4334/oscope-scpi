#   @file KeysightMSOX4154A.py 
#   @brief Establishes a connection to the Keysight MSOX4154A Oscilliscope
#       and provides methods for interfacing with the device.
#   @date 18-May-2023
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

# Imports
import pyvisa
from colorama import init, Fore, Style
try:
    from .loading import *
except:
    from loading import *

# Constants and global variables
_ERROR_STYLE = Fore.RED + Style.BRIGHT + "\rError! "
_SUCCESS_STYLE = Fore.GREEN + Style.BRIGHT  + "\r"
_DELAY = 0.1

"""
Establishes a connection to the Keysight MSOX4154A Oscilliscope and provides methods for interfacing.

Example usage:
    Oscilliscope = KeysightMSOX4154A()
"""
class KeysightMSOX4154A:

    """
    Initializes an instance of the KeysightMSOX4154A class.
    """
    def __init__(self, auto_connect=True):
        
        init(autoreset=True)

        self.rm = pyvisa.ResourceManager()
        self.address = None
        self.instrument = None
        self.loading = loading()

        self.status = "Not Connected"
        
        if auto_connect:
            self.connect()
        
    """
    Establishes a connection to the Keysight MSOX4154A Oscilliscope.

    Raises:
        ConnectionError: If unable to connect to Keysight MSOX4154A Oscilliscope.
    
    Example usage:
        Oscilliscope.connect()
    """
    def connect(self):
        
        resources = self.rm.list_resources()
        for resource in resources:
            if 'MY56' in resource:
                self.address = resource
                break
        
        if self.address is None:
            error_message = "Keysight MSOX4154A Oscilliscope not found."
            raise ConnectionError(_ERROR_STYLE + error_message)
        
        try:
            self.instrument = self.rm.open_resource(self.address)
            self.instrument.read_termination = '\n'
            self.status = "Connected"
            success_message = f"Connected to Keysight MSOX4154A Oscilliscope at {self.address}"
            print(_SUCCESS_STYLE + success_message)

        except:
            error_message = f"Failed to connect to Keysight MSOX4154A Oscilliscope at {self.address}: {e}"
            raise ConnectionError(_ERROR_STYLE + error_message)

    """
    Disconnects from the Keysight MSOX4154A Oscilliscope.
    
    Example usage:
        Oscilliscope.disconnect()
    """
    def disconnect(self):
        
        if self.instrument is not None:
            self.instrument.close()
            print(f"\rDisconnected from Keysight MSOX4154A Oscilliscope at {self.address}")
            self.status = "Not Connected"

    """
    Retrieves the specified value.
    
    Args:
        item (str): The measurement item to retrieve. Valid values are "STAT", "CURR", or "VOLT".
    
    Returns:
        The measurement result corresponding to the specified item and channel.

    Raises:
        ValueError: If an invalid item is requested.
    
    Example usage:
        voltage = Oscilliscope.get("VOLT")
        print(f"Voltage: {voltage} V")
    """
    def get(self, item):
    
        items = {
            "screenshot": self.get_screenshot
        }

        if item in items:
            result = items[item]()
            return result
        else:
            error_message = f"Invalid item: {item} request to Keysight MSOX4154A Oscilliscope"
            raise ValueError(_ERROR_STYLE + error_message)
        
    """
    Captures a screenshot from the oscilloscope and returns it as a PNG file.
    Returns:
        bytes: The PNG image data.
    Example usage:
        screenshot_data = Oscilliscope.get_screenshot()
        with open("screenshot.png", "wb") as f:
            f.write(screenshot_data)
    """
    def get_screenshot(self):
        if self.instrument is None:
            error_message = "Not connected to Keysight MSOX4154A Oscilliscope."
            raise ConnectionError(_ERROR_STYLE + error_message)
        
        try:
            self.instrument.write(":DISP:DATA? PNG, COLOR")
            screenshot_data = self.instrument.read_raw()
            return screenshot_data
        except Exception as e:
            error_message = f"Failed to capture screenshot: {e}"
            raise RuntimeError(_ERROR_STYLE + error_message)

'''
Example test.py file to test the KeysightMSOX4154A class:

from KeysightMSOX4154A import KeysightMSOX4154A

# Take output dir as input argument
import sys
import os
output_dir = sys.argv[1] if len(sys.argv) > 1 else "."
if not os.path.exists(output_dir):
    os.makedirs(output_dir)
os.chdir(output_dir)
print(f"Output directory: {os.getcwd()}")


# Create an instance of the KeysightMSOX4154A class
oscilloscope = KeysightMSOX4154A()
# Get a screenshot from the oscilloscope
screenshot_data = oscilloscope.get_screenshot()
# Save the screenshot to a file
# Create filename like screenshot_YYYYMMDD_HHMMSS.png
import datetime
timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
filename = f"screenshot_{timestamp}.png"
print(f"Saving screenshot to {filename}")

with open(filename, "wb") as f:
    f.write(screenshot_data)

# Disconnect from the oscilloscope
oscilloscope.disconnect()
'''
