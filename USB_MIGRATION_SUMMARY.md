# USB Connection Migration Summary

This document summarizes the changes made to migrate oscope-scpi from TCP/IP to USB connectivity.

## Changes Made

### 1. Core Connection Logic (scpi.py)
- Modified `__init__()` to accept `resource=None` for USB auto-detection
- Added `_find_usb_oscilloscope()` method to scan and identify USB oscilloscopes
- Added `connect()` method with auto-detection capability
- Maintained existing `open()` method for backward compatibility

### 2. Oscilloscope Class (oscilloscope.py)
- Updated constructor to support USB auto-detection
- Updated documentation examples to use USB
- Maintained full backward compatibility

### 3. Example Scripts
- Updated `oscope.py` to use USB auto-detection by default
- Created `usb_example.py` to demonstrate new functionality
- Updated README.md with USB usage examples

### 4. Device Detection
The USB detection looks for these oscilloscope identifiers:
- `MY5*` - Keysight instruments (like MY59 from example)
- `DSO*` - Keysight DSO series
- `MSO*` - Keysight MSO series  
- `MXR*` - Keysight MXR series
- `UXR*` - Keysight UXR series
- `EXR*` - Keysight EXR series
- `RIGOL*` - Rigol instruments
- `DHO*` - Rigol DHO series
- `AGILENT*` - Legacy Agilent instruments
- `KEYSIGHT*` - Keysight instruments

## Usage Patterns

### Auto-detect USB (New Default)
```python
from oscope_scpi import Oscilloscope
scope = Oscilloscope()  # No resource = auto-detect USB
scope.connect()
```

### Manual USB Resource
```python
scope = Oscilloscope('USB0::0x0957::0x17A6::MY59270123::INSTR')
scope.connect()
```

### Environment Variable Override
```bash
export OSCOPE_IP='USB0::0x0957::0x17A6::MY59270123::INSTR'
python oscope.py
```

### Backward Compatibility (TCP/IP)
```python
scope = Oscilloscope('TCPIP0::172.16.2.13::INSTR')
scope.open()  # or scope.connect()
```

## Error Handling

The implementation provides clear error messages:
- "No USB oscilloscope found. Please ensure an oscilloscope is connected via USB."
- "No resource specified and auto-detection disabled."

## Backward Compatibility

All existing code continues to work without modification:
- Manual resource strings are still supported
- Environment variable `OSCOPE_IP` is still respected
- All existing methods and APIs remain unchanged
- Legacy `open()` method still works

## Testing

Comprehensive tests verify:
- USB auto-detection functionality
- Error handling when no devices found
- Backward compatibility with existing code
- Environment variable override
- Manual resource specification