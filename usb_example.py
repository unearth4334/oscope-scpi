#!/usr/bin/env python3

"""
Example: USB Oscilloscope Connection

This example demonstrates how to connect to an oscilloscope over USB
using the new auto-detection functionality.
"""

import sys
import os
sys.path.insert(0, '/home/runner/work/oscope-scpi/oscope-scpi')

from oscope_scpi import Oscilloscope

def main():
    print("USB Oscilloscope Connection Example")
    print("=" * 40)
    
    # Method 1: Auto-detect USB oscilloscope (new default behavior)
    print("\n1. Auto-detecting USB oscilloscope...")
    try:
        scope = Oscilloscope()  # No resource specified = auto-detect USB
        scope.connect()
        
        print(f"✓ Connected to: {scope.idn()}")
        print(f"  Resource: {scope._resource}")
        scope.close()
        
    except ConnectionError as e:
        print(f"ℹ {e}")
        print("  This is expected if no USB oscilloscope is connected.")
    
    # Method 2: Manual USB resource string (for specific devices)
    print("\n2. Manual USB resource specification...")
    try:
        # Example USB resource string for a Keysight oscilloscope
        usb_resource = "USB0::0x0957::0x17BC::MY56310625::INSTR"
        scope = Oscilloscope(usb_resource)
        print(f"✓ Created scope with USB resource: {usb_resource}")
        print("  (Would connect if device was actually present)")
        
    except Exception as e:
        print(f"✗ Error: {e}")
    
    # Method 3: Environment variable override
    print("\n3. Environment variable override...")
    os.environ['OSCOPE_IP'] = 'USB0::0x0957::0x17BC::MY56310625::INSTR'
    try:
        scope = Oscilloscope(os.environ.get('OSCOPE_IP', None))
        print(f"✓ Using resource from OSCOPE_IP: {scope._resource}")
        
    except Exception as e:
        print(f"✗ Error: {e}")
    finally:
        # Clean up
        if 'OSCOPE_IP' in os.environ:
            del os.environ['OSCOPE_IP']
    
    # Method 4: Backward compatibility with TCP/IP
    print("\n4. Backward compatibility (TCP/IP)...")
    try:
        tcpip_resource = "TCPIP0::172.16.2.13::INSTR"
        scope = Oscilloscope(tcpip_resource)
        print(f"✓ Created scope with TCP/IP resource: {tcpip_resource}")
        print("  (Backward compatibility maintained)")
        
    except Exception as e:
        print(f"✗ Error: {e}")
    
    print("\n" + "=" * 40)
    print("Summary of changes:")
    print("• Default behavior now auto-detects USB oscilloscopes")
    print("• Use connect() instead of open() for auto-detection")
    print("• Backward compatibility maintained for manual resources")
    print("• Environment variable OSCOPE_IP still supported")

if __name__ == "__main__":
    main()