# Author : Noé Backert
# Date   : 2025-06-26
# Description : This script sets up a Windows environment with various tools and configurations.


import os
import requests
import sys
import json

def get_config()->json:
    """Load configuration from config.json."""
    config_path = os.path.join(os.path.dirname(__file__), 'config.json')
    with open(config_path, 'r') as file:
        return json.load(file)

def save_config(config: json):
    """Save the updated configuration back to config.json."""
    config_path = os.path.join(os.path.dirname(__file__), 'config.json')
    with open(config_path, 'w') as file:
        json.dump(config, file, indent=4)
    print("[+] Configuration saved successfully.")

def toggle_tool(config: json, tool_name: str) -> json:
    """Toggle the enable state of a tool in the configuration."""
    if tool_name in config.get('tools', {}):
        current_state = config['tools'][tool_name].get('enable', False)
        config['tools'][tool_name]['enable'] = not current_state
        print(f"[+] Toggled {tool_name} to {'enabled' if not current_state else 'disabled'}.")
        save_config(config)
    else:
        print(f"[-] Tool {tool_name} not found in configuration.")
    return config


def get_missing_setup_files(config: json) -> list:
    """Get a list of setup files that are missing based on the configuration."""
    missing_files = []
    for tool_name, tool_info in config.get('tools', {}).items():
        if tool_info.get('enable', False):
            file_path = os.path.join(os.path.dirname(__file__), 'scripts', 'setups', tool_info['name'])
            if not os.path.exists(file_path):
                missing_files.append(tool_info)
    return missing_files

def download_7zip():
    file_path = os.path.join(os.path.dirname(__file__), 'scripts', 'setups')
    os.makedirs(file_path, exist_ok=True)
    try:
        print("[*] Downloading 7-Zip...")
        response = requests.get("https://www.7-zip.org/a/7z2409-x64.msi", stream=True, allow_redirects=True, timeout=30)
        response.raise_for_status()
        with open(os.path.join(file_path, '7z2409-x64.msi'), 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        print("[+] 7-Zip downloaded successfully.")
    except requests.RequestException as e:
        print(f"[-] Failed to download 7-Zip: {e}")

def download_missing_setup_files(config: json):
    """Download setup files that are missing."""
    file_path = os.path.join(os.path.dirname(__file__), 'scripts', 'setups')
    os.makedirs(file_path, exist_ok=True)
    # If 7zip is not installed, download it
    tools_to_download = get_missing_setup_files(config)

    for tool_info in tools_to_download:
        destination = os.path.join(file_path, tool_info['name'])
        try:
            print(f"[*] Downloading {tool_info['name']}...")
            response = requests.get(tool_info['link'], stream=True, allow_redirects=True, timeout=30)
            response.raise_for_status()
            with open(destination, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            print(f"[+] {tool_info['name']} downloaded successfully.")
        except requests.RequestException as e:
            print(f"[-] Failed to download {tool_info['name']}: {e}")

def generate_wsb_config(config: dict) -> str:
    """Generate a WSB configuration string based on the provided vmConfig section."""
    vm_config = config.get("vmConfig", {})
    tools_config = config.get("tools", {})

    xml_lines = ['<Configuration>']

    # Basic options
    if "vGPU" in vm_config:
        xml_lines.append(f'  <VGpu>{vm_config["vGPU"]}</VGpu>')
    if "Networking" in vm_config:
        xml_lines.append(f'  <Networking>{vm_config["Networking"]}</Networking>')
    if "MemoryInMB" in vm_config:
        mem = vm_config["MemoryInMB"]
        if isinstance(mem, str) and "GB" in mem.upper():
            try:
                gb = int(''.join(filter(str.isdigit, mem)))
                mem_mb = gb * 1024
            except:
                mem_mb = 4096
        else:
            mem_mb = int(mem)
        xml_lines.append(f'  <MemoryInMB>{mem_mb}</MemoryInMB>')
    if "LogonCommand" in vm_config:
        xml_lines.append('  <LogonCommand>')
        xml_lines.append(f'    <Command>{vm_config["LogonCommand"]}</Command>')
        xml_lines.append('  </LogonCommand>')

    # Prepare MappedFolders block
    mapped_folders = []

    # Always add default tools folder
    host_folder = os.path.join(os.path.dirname(__file__), 'scripts')
    mapped_folders.append({
        "HostFolder": host_folder,
        "SandboxFolder": "C:\\Users\\WDAGUtilityAccount\\Desktop\\scripts",
            "ReadOnly": "true"
        })
    print(f"[*] Added default tools folder: {host_folder}")

    # Add user-defined mapped folders
    for folder in vm_config.get("MappedFolder", []):
        host = folder.get("HostFolder", "")
        if host == "Default":
            host = os.path.join(os.path.dirname(__file__), 'scripts', 'setups')
        sandbox = folder.get("SandboxFolder", "/sandbox-auto-setup")
        readonly = str(folder.get("ReadOnly", True)).lower()
        mapped_folders.append({
            "HostFolder": host,
            "SandboxFolder": sandbox,
            "ReadOnly": readonly
        })

    # Write MappedFolders XML
    if mapped_folders:
        xml_lines.append('  <MappedFolders>')
        for folder in mapped_folders:
            xml_lines.append('    <MappedFolder>')
            xml_lines.append(f'      <HostFolder>{folder["HostFolder"]}</HostFolder>')
            xml_lines.append(f'      <SandboxFolder>{folder["SandboxFolder"]}</SandboxFolder>')
            xml_lines.append(f'      <ReadOnly>{folder["ReadOnly"]}</ReadOnly>')
            xml_lines.append('    </MappedFolder>')
        xml_lines.append('  </MappedFolders>')

    # Optional features
    for feature in ["AudioInput", "VideoInput", "PrinterRedirection",
                    "ProtectedClient", "ClipboardRedirection"]:
        if feature in vm_config:
            xml_lines.append(f'  <{feature}>{vm_config[feature]}</{feature}>')

    xml_lines.append('</Configuration>')

    # Write to file
    wsb_path = os.path.join(os.path.dirname(__file__), 'WinSandbox.wsb')
    with open(wsb_path, 'w') as file:
        file.write("\n".join(xml_lines))

    print(f"[+] WSB file written to: {wsb_path}")


def tool_config():
    """Show the configuration, with index numbers to toggle tools using numbers.
    When done, enter 'done' to save and run the setup script."""
    config = get_config()
    while True:
        print("\nAvailable Tools:")
        for index, (tool_name, tool_info) in enumerate(config.get('tools', {}).items(), start=1):
            status = "Enabled" if tool_info.get('enable', False) else "Disabled"
            print(f"{index}. [{'X' if status == 'Enabled' else ' '}] - {tool_name} (Version: {tool_info.get('version', 'N/A')})")

        choice = input("\nEnter the number of the tool to toggle, or 'done' to finish: ").strip()
        if choice.lower() == 'done':
            print("[*] Checking for missing setup files...")
            missing_files = get_missing_setup_files(config)

            if missing_files:
                download_missing_setup_files(config)
            print("[+] All setup files are present. Proceeding with the setup script.")
            generate_wsb_config(config)
            break
        try:
            index = int(choice) - 1
            tool_name = list(config['tools'].keys())[index]
            config = toggle_tool(config, tool_name)
        except (ValueError, IndexError):
            print("[-] Invalid input. Please enter a valid number.")

def sandbox_config():
    """Show the current VM configuration and allow the user to modify it."""
    config = get_config()
    vm_config = config.get('vmConfig', {})
    print("[*] Current VM Configuration:")
    for key, value in vm_config.items():
        print(f"{key}: {value}")

    print("\n[*] Enter new values for the VM configuration (leave blank to keep current value):")

    for key in list(vm_config.keys()):
        if key == "MappedFolder":
            print("[*] Do you want to add or remove a mapped folder? (add/remove/none)")
            action = input().strip().lower()

            if action == 'add':
                host_folder = input("Enter the host folder path: ").strip()
                sandbox_folder = input("Enter the sandbox folder path (default: C:\\Users\\WDAGUtilityAccount\\Desktop\\sandbox-auto-setup): ").strip() or "C:\\Users\\WDAGUtilityAccount\\Desktop\\sandbox-auto-setup"
                read_only_input = input("Read only? (yes/no, default: yes): ").strip().lower() or "yes"
                read_only = read_only_input == "yes"

                vm_config.setdefault("MappedFolder", []).append({
                    "HostFolder": host_folder,
                    "SandboxFolder": sandbox_folder,
                    "ReadOnly": read_only
                })
                print("[+] Mapped folder added.")

            elif action == 'remove':
                mapped = vm_config.get("MappedFolder", [])
                if mapped:
                    print("[*] Current mapped folders:")
                    for i, folder in enumerate(mapped, 1):
                        print(f"{i}. Host: {folder['HostFolder']}, Sandbox: {folder.get('SandboxFolder', '')}, ReadOnly: {folder.get('ReadOnly', True)}")
                    try:
                        index = input("Enter the number to remove (or 'none' to cancel): ").strip().lower()
                        if index != 'none':
                            idx = int(index) - 1
                            if 0 <= idx < len(mapped):
                                del mapped[idx]
                                print("[+] Folder removed.")
                            else:
                                print("[-] Invalid index.")
                    except ValueError:
                        print("[-] Invalid input.")
                else:
                    print("[!] No mapped folders to remove.")
        elif key == "LogonCommand":
            continue
        else:
            new_value = input(f"{key} (current: {vm_config[key]}): ").strip()
            if new_value:
                vm_config[key] = new_value

    # Ensure LogonCommand is correctly set
    tools_cmd_path = r"C:\Users\WDAGUtilityAccount\Desktop\scripts\start.cmd"
    if "LogonCommand" not in vm_config or vm_config["LogonCommand"] != tools_cmd_path:
        print("[*] Setting LogonCommand to launch tools setup script.")
        vm_config["LogonCommand"] = tools_cmd_path

    print("\n[*] Final VM Configuration:")
    for key, value in vm_config.items():
        print(f"{key}: {value}")

    config["vmConfig"] = vm_config
    save_config(config)
    generate_wsb_config(config)
    print("[+] VM configuration updated and WSB file regenerated.")




def configure_sandbox():
    while True:
        config = get_config()
        tools = config.get('tools', {})
        enabled_tools_list = [name for name, info in tools.items() if info.get('enable')]
        vm_config = config.get('vmConfig', {})
        print("[*] Current configuration:")
        print(f"[*] - Available tools: {', '.join(tools.keys())}")
        print(f"[*] - Enabled tools: {', '.join(enabled_tools_list)}")
        print(f"[*] - VM Configuration: \n\n{json.dumps(vm_config, indent=4)}")
        print(f"[*] To change tools configuration enter 'tool' or 'vm' to change VM configuration.")
        print("[*] Type 'done' to finish configuration and generate the WSB file.")
        print("[*] Type 'exit' to quit the configuration.")
        choice = input("Choice: ").strip().lower()
        if choice == 'tool':
            tool_config()
        elif choice == 'vm':
            sandbox_config()
        elif choice == 'done':
            file_path = os.path.join(os.path.dirname(__file__), 'scripts', 'setups')
            # Check if 7-Zip is installed, if not, download it
            if not os.path.exists(os.path.join(file_path, '7z2409-x64.msi')):
                download_7zip()

            print("[*] Generating WSB configuration file...")
            generate_wsb_config(config)
            print("[+] WSB configuration file generated successfully.")
            break
        elif choice == 'exit':
            print("[*] Exiting configuration.")
            sys.exit(0)

def generate_setup_cmd(config: json):
    """Generate a setup.cmd file that installs only the enabled tools."""
    tools = config.get("tools", {})
    setup_path = r"%SETUP_PATH%"
    lines = [
        "@echo off",
        "set SETUP_PATH=C:\\users\\WDAGUtilityAccount\\Desktop\\scripts\\setups",
        "echo [*] Copying setup files...",
        "copy /B /Y /V %SETUP_PATH%\\* %TEMP%\\",
        ""
    ]
    lines.append(f'msiexec /i "%TEMP%\\7z2409-x64.msi" /qn /norestart')

    for name, tool in tools.items():
        if not tool.get("enable", False):
            continue

        filename = tool.get("name", "").lower()
        lines.append(f'echo [*] Installing {name}...')

        # Custom behavior per tool
        try:
            if "jpegview" in filename:
                lines += [
                    'if not exist "C:\\Program Files\\JPEGView64" mkdir "C:\\Program Files\\JPEGView64"',
                    f'"%PROGRAMFILES%\\7-Zip\\7z.exe" x -aoa "%TEMP%\\{filename}" -o"C:\\Program Files" JPEGView64\\*',
                    'assoc .jpg=JPEGView.Image',
                    'assoc .png=JPEGView.Image',
                    'ftype JPEGView.Image="C:\\Program Files\\JPEGView64\\JPEGView64.exe" "%%1"'
                ]

            if "git" in filename:
                lines += [
                    f'"%TEMP%\\{filename}" /VERYSILENT /NORESTART /NOCANCEL /SP-',
                    'set "PATH=%PATH%;C:\\Program Files\\Git\\cmd"'
                ]

            if "python-3" in filename:
                lines += [
                    f'"%TEMP%\\{filename}" /quiet InstallAllUsers=1 PrependPath=1 Include_test=0',
                    'set "PATH=%PATH%;C:\\Program Files\\Python312\\Scripts\\"',
                    'set "PATH=%PATH%;C:\\Program Files\\Python312\\"'
                ]

            if "python-2" in filename:
                lines.append(f'msiexec /i "%TEMP%\\{filename}" /qn /norestart')

            if "oletools" in name.lower():
                lines += [
                    'pip install -U oletools[full]',
                    'echo "[*] oletools installed successfully."'
                ]

            if "vscode" in filename:
                lines.append(f'"%TEMP%\\{filename}" /verysilent /suppressmsgboxes /MERGETASKS="!runcode,addtopath"')

            if "sysinternals" in filename:
                lines.append(f'"%PROGRAMFILES%\\7-Zip\\7z.exe" x -aoa "%TEMP%\\{filename}" -o"%USERPROFILE%\\Desktop\\Tools\\sysinternals"')

        except Exception as e:
            lines.append(f'echo [!] Unknown install method for: {filename}')

        lines.append("")  # add empty line for readability

    # Add hardcoded options like ScriptBlockLogging
    lines += [
        "echo [*] Enabling PowerShell ScriptBlockLogging...",
        "powershell.exe -Command \"New-Item -Path HKLM:\\SOFTWARE\\Wow6432Node\\Policies\\Microsoft\\Windows\\PowerShell\\ScriptBlockLogging -Force\"",
        "powershell.exe -Command \"Set-ItemProperty -Path HKLM:\\SOFTWARE\\Wow6432Node\\Policies\\Microsoft\\Windows\\PowerShell\\ScriptBlockLogging -Name EnableScriptBlockLogging -Value 1 -Force\"",
        "",
        "echo [*] All tasks completed.",
        "pause"
    ]

    # Write to scripts/setup.cmd
    start_cmd_path = os.path.join(os.path.dirname(__file__), "scripts", "setup.cmd")
    with open(start_cmd_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print(f"[+] setup.cmd generated with {sum(tool['enable'] for tool in tools.values())} tools.")


if __name__ == "__main__":
    config = get_config()
    configure_sandbox()
    generate_setup_cmd(config)
