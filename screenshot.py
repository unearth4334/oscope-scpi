#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright (c) 2024, Stephen Goadhouse <sgoadhouse@virginia.edu>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""
Capture a screenshot from an oscilloscope via SCPI commands.

This script takes a device address and output path as command line arguments,
connects to the oscilloscope, captures a screenshot, and saves it with a 
filename format: {MODEL}_screenshot_{YYYYMMDD}_{HHMM}.png
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import sys
import os
import argparse
from datetime import datetime

try:
    from oscope_scpi import Oscilloscope
except ImportError:
    # If running from source directory
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    from oscope_scpi import Oscilloscope


def extract_model_from_idn(idn_string):
    """Extract and clean the model name from IDN string for use in filename."""
    try:
        parts = idn_string.split(',')
        if len(parts) >= 2:
            model = parts[1].strip()
            # Remove any characters that might be problematic in filenames
            model = model.replace(' ', '_').replace('/', '_').replace('\\', '_')
            # Remove any other special characters except letters, numbers, underscore, hyphen
            import re
            model = re.sub(r'[^a-zA-Z0-9_-]', '', model)
            return model
        else:
            return "UNKNOWN"
    except Exception:
        return "UNKNOWN"


def generate_filename(model, output_path):
    """Generate the screenshot filename with timestamp."""
    # Generate timestamp in format YYYYMMDD_HHMM
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    
    # Create filename: {MODEL}_screenshot_{YYYYMMDD}_{HHMM}.png
    filename = f"{model}_screenshot_{timestamp}.png"
    
    # Combine with output path
    if output_path:
        # Check if output_path is definitely a directory
        if os.path.isdir(output_path) or output_path.endswith(('/', '\\')):
            # It's a directory, join with our generated filename
            full_path = os.path.join(output_path, filename)
        elif '.' in os.path.basename(output_path) and not output_path.endswith('.'):
            # It appears to be a file path with extension
            # Use the directory part and our generated filename
            dir_path = os.path.dirname(output_path)
            if dir_path:
                full_path = os.path.join(dir_path, filename)
            else:
                full_path = filename
        else:
            # Treat as directory path
            full_path = os.path.join(output_path, filename)
    else:
        # Use current directory
        full_path = filename
    
    return full_path


def capture_screenshot(device_address, output_path):
    """Capture screenshot from the oscilloscope and save to specified path."""
    
    print(f"Connecting to oscilloscope at: {device_address}")
    
    scope = None
    try:
        # Create oscilloscope object
        scope = Oscilloscope(device_address)
        
        # Open connection and get device info
        scope.open()
        idn = scope.idn()
        print(f"Connected to: {idn}")
        scope.close()
        
        # Get the best class for this device
        scope = scope.getBestClass()
        
        # Re-open with the specific device class
        scope.open()
        
        # Extract model name for filename
        model = extract_model_from_idn(idn)
        print(f"Device model: {model}")
        
        # Generate filename with timestamp
        filename = generate_filename(model, output_path)
        print(f"Saving screenshot to: {filename}")
        
        # Ensure output directory exists
        output_dir = os.path.dirname(filename)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        # Capture screenshot
        scope.hardcopy(filename)
        
        print(f"Screenshot saved successfully: {filename}")
        return filename
        
    except ImportError as e:
        print(f"Error: Missing required dependencies: {str(e)}", file=sys.stderr)
        print("Make sure PyVISA and other dependencies are installed.", file=sys.stderr)
        return None
    except Exception as e:
        error_msg = str(e)
        if "RSRC_NFOUND" in error_msg or "Resource not found" in error_msg:
            print(f"Error: Could not find oscilloscope at address '{device_address}'", file=sys.stderr)
            print("Please check the device address and ensure the device is connected and powered on.", file=sys.stderr)
        elif "Permission denied" in error_msg or "Access denied" in error_msg:
            print(f"Error: Permission denied accessing device '{device_address}'", file=sys.stderr)
            print("Make sure you have the necessary permissions to access the device.", file=sys.stderr)
        elif "timeout" in error_msg.lower():
            print(f"Error: Timeout communicating with device '{device_address}'", file=sys.stderr)
            print("The device may be busy or not responding. Try again later.", file=sys.stderr)
        else:
            print(f"Error capturing screenshot: {error_msg}", file=sys.stderr)
        return None
    finally:
        # Ensure connection is closed
        if scope:
            try:
                scope.close()
            except:
                pass


def main():
    """Main function to parse arguments and capture screenshot."""
    
    parser = argparse.ArgumentParser(
        description="Capture a screenshot from an oscilloscope via SCPI commands",
        epilog="""
Examples:
  %(prog)s USB0::0x0957::0x17BC::MY56310625::INSTR /path/to/screenshots/
  %(prog)s TCPIP0::192.168.1.100::INSTR ./screenshots/
  %(prog)s "USB0::0x0957::0x17BC::MY56310625::INSTR" ~/Downloads/scope_captures/
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        'device_address',
        help='VISA device address (e.g., "USB0::0x0957::0x17BC::MY56310625::INSTR")'
    )
    
    parser.add_argument(
        'output_path',
        nargs='?',
        default='.',
        help='Output directory or file path for the screenshot (default: current directory)'
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version='%(prog)s 1.0'
    )
    
    # Parse arguments
    args = parser.parse_args()
    
    # Validate device address format
    if not args.device_address:
        parser.error("Device address is required")
    
    # Capture screenshot
    result = capture_screenshot(args.device_address, args.output_path)
    
    if result:
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == '__main__':
    main()