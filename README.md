# Windows Sandbox Configuration

This is a simple configuration generator for Windows Sandbox with some basic tools ready to go.

For configuration options in the `.wsb` file please read [https://docs.microsoft.com/en-us/windows/security/threat-protection/windows-sandbox/windows-sandbox-configure-using-wsb-file](https://docs.microsoft.com/en-us/windows/security/threat-protection/windows-sandbox/windows-sandbox-configure-using-wsb-file).

## Software installed

the following software are currently available

- 7-zip (always)
- Visual Studio Code
- Sysinternals Suite
- python2
- python3
- JPEGView (for image view - no default jpg/png viewer in sandbox)
- Git
- Oletools
- Eric Zimmerman Tools (digital forensics tools collection)


#### Software to add:

- Chrome
- Ghidra ? 
- Wireshark ?

## Additional config

- powershell script block logging activated
- sysmon with SwiftOnSecurity profile installed (view results in eventvwr)

## Usage

1. run `python main.py`.
2. Choose which tools you need by typing "tool"
3. Toggle each needed tool using its index.
4. Choose which vm config you need
5. Enter done to complete the configuration.
6. Run ./WinSandbox.wsb
