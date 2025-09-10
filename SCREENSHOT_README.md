# Screenshot Capture Script

This script captures screenshots from oscilloscopes via SCPI commands and saves them with a standardized filename format.

## Features

- Supports all oscilloscope models supported by oscope-scpi
- Automatic device model detection from IDN string
- Timestamped filenames in format: `{MODEL}_screenshot_{YYYYMMDD}_{HHMM}.png`
- Flexible output path handling (directories or file paths)
- Comprehensive error handling with user-friendly messages
- Cross-platform compatibility

## Usage

```bash
python3 screenshot.py <device_address> [output_path]
```

### Arguments

- `device_address`: VISA device address (required)
  - Examples: `"USB0::0x0957::0x17BC::MY56310625::INSTR"`
  - Examples: `"TCPIP0::192.168.1.100::INSTR"`

- `output_path`: Output directory or file path (optional, defaults to current directory)
  - Examples: `/path/to/screenshots/`
  - Examples: `./screenshots/`
  - Examples: `~/Downloads/scope_captures/`

### Examples

```bash
# Save to current directory
python3 screenshot.py "USB0::0x0957::0x17BC::MY56310625::INSTR"

# Save to specific directory
python3 screenshot.py "USB0::0x0957::0x17BC::MY56310625::INSTR" /tmp/screenshots/

# Save to user's Downloads folder
python3 screenshot.py "TCPIP0::192.168.1.100::INSTR" ~/Downloads/

# Help
python3 screenshot.py --help
```

## Output Filename Format

The script automatically generates filenames using the following format:

```
{MODEL}_screenshot_{YYYYMMDD}_{HHMM}.png
```

Where:
- `{MODEL}` is extracted from the oscilloscope's IDN response
- `{YYYYMMDD}` is the current date
- `{HHMM}` is the current time in 24-hour format

### Example Filenames

- `MSOX4254A_screenshot_20240315_1430.png`
- `DSO-X_3034A_screenshot_20240315_0945.png`
- `MXR058A_screenshot_20240315_2215.png`

## Supported Devices

The script supports all oscilloscope models that are supported by the oscope-scpi library, including:

- Keysight/Agilent MSO-X and DSO-X series
- Keysight MXR and EXR series
- Keysight UXR series
- Rigol DHO series
- And other SCPI-compatible oscilloscopes

## Error Handling

The script provides clear error messages for common issues:

- Device not found or not responding
- Permission/access denied
- Timeout errors
- Missing dependencies
- Invalid device addresses

## Dependencies

- Python 3.6+
- oscope-scpi package
- PyVISA
- PyVISA-py
- NumPy
- QuantiPhy

## Testing

Run the included test script to verify functionality:

```bash
python3 test_screenshot.py
```

This runs tests for:
- Model name extraction from IDN strings
- Filename generation with various path formats
- Command line interface functionality