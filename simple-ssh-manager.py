import os
import sys
import re
import shutil
import math
import re


CONFIG_FILE = os.path.expanduser("~/.ssh/config")


def ensure_config_file():
    os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)
    if not os.path.exists(CONFIG_FILE):
        open(CONFIG_FILE, 'a').close()


def parse_config():
    config = {}
    current_host = None
    current_lines = []
    current_tags = []

    with open(CONFIG_FILE, 'r') as f:
        for line in f:
            stripped = line.strip()

            if stripped.startswith("Host "):
                if current_host:
                    config[current_host] = {
                        'lines': current_lines,
                        'tags': current_tags
                    }
                current_host = stripped.split(maxsplit=1)[1]
                current_lines = [line]
                current_tags = []
            elif current_host:
                current_lines.append(line)
                if stripped.lower().startswith("# tags:"):
                    tag_line = stripped.split(":", 1)[1]
                    tags = [t.strip().lower() for t in tag_line.split(",")]
                    current_tags.extend(tags)

        if current_host:
            config[current_host] = {
                'lines': current_lines,
                'tags': current_tags
            }

    return config

def filter_by_tag():
    config = parse_config()
    tag_input = input(color("🔍 Enter tag to filter (e.g., dev): ", "1;36")).strip().lower()

    if not tag_input:
        print(color("⚠ Empty tag. Try again.", "93"))
        return

    matches = [
        host for host, data in config.items()
        if "*" not in host and tag_input in data.get("tags", [])
    ]

    if not matches:
        print(color("❌ No hosts found with that tag.", "91"))
        return

    print(color(f"\n📄 Hosts tagged '{tag_input}':", "1;34"))
    for i, host in enumerate(sorted(matches), 1):
        print(f"{color(f'{i:2d})', '1;33')} {color(host, '92')}")


def get_field(lines, field):
    for line in lines:
        parts = line.strip().split(None, 1)
        if len(parts) == 2 and parts[0].lower() == field.lower():
            return parts[1]
    return ""



def input_with_default(prompt, default):
    val = input(f"{prompt} [{default}]: ").strip()
    return val or default


def write_config(config):
    with open(CONFIG_FILE, 'w') as f:
        for host, lines in config.items():
            for line in lines:
                f.write(line if line.endswith('\n') else line + '\n')
            f.write('\n')


def add_or_update_host():
    config = parse_config()

    host = input("Enter host alias (e.g., myserver): ").strip()
    is_update = host in config
    existing_data = config.get(host, {})
    old_lines = existing_data.get("lines", [])
    old_tags = existing_data.get("tags", [])

    # Get global IdentityFile from Host * (if exists)
    global_config = config.get("*", {})
    global_key = get_field(global_config.get("lines", []), "IdentityFile")
    default_key = os.path.expanduser(global_key or "~/.ssh/id_rsa")

    old_key = get_field(old_lines, "IdentityFile") or default_key
    old_hostname = get_field(old_lines, "HostName") or "example.com"
    old_user = get_field(old_lines, "User") or "ubuntu"
    old_port = get_field(old_lines, "Port") or "22"

    print("Leave blank to keep existing values.")

    hostname = input_with_default("HostName", old_hostname)
    user = input_with_default("User", old_user)
    port = input_with_default("Port", old_port)

    # Validate identity file path
    while True:
        identity_file_input = input(f"IdentityFile [{old_key}]: ").strip()
        if not identity_file_input:
            identity_file = old_key
            break

        identity_file_path = os.path.expanduser(identity_file_input)
        if os.path.exists(identity_file_path):
            identity_file = identity_file_input
            break
        else:
            print(f"❌ IdentityFile '{identity_file_input}' does not exist. Please try again.")

    # Prompt for tags
    tag_input = input(f"Tags (comma separated) [{', '.join(old_tags) if old_tags else 'none'}]: ").strip()
    tags = [t.strip().lower() for t in tag_input.split(",") if t.strip()] if tag_input else old_tags

    # Build host config lines
    new_lines = [
        f"Host {host}",
        f"    HostName {hostname}",
        f"    User {user}",
        f"    Port {port}",
        f"    IdentityFile {identity_file}",
    ]

    if tags:
        new_lines.append(f"    # tags: {', '.join(tags)}")

    config[host] = {
        "lines": new_lines,
        "tags": tags
    }

    # Write back only the lines
    write_config({h: d["lines"] for h, d in config.items()})
    print(f"✅ Host '{host}' {'updated' if is_update else 'added'} successfully.")





def list_hosts():
    config = parse_config()
    hosts = sorted([host for host in config if "*" not in host])

    if not hosts:
        print("⚠️ No saved hosts found.")
        return

    print("\n" + color("📄 Saved Hosts:", "1;34"))

    # Get terminal width for auto-column formatting
    terminal_width = shutil.get_terminal_size((80, 20)).columns
    max_length = max(len(h) for h in hosts) + 4
    cols = max(1, terminal_width // max_length)
    rows = math.ceil(len(hosts) / cols)

    # Pad and print in columns
    for row in range(rows):
        line = ""
        for col in range(cols):
            i = row + col * rows
            if i < len(hosts):
                host = hosts[i]
                line += color(host.ljust(max_length), "92")  # Green color
        print(line)



def connect_to_host():
    config = parse_config()
    hosts = sorted([host for host in config if "*" not in host])

    if not hosts:
        print(color("⚠ No saved hosts to connect.", "91"))
        return

    print(color("\n📡 Available Hosts:", "1;34"))
    for idx, host in enumerate(hosts, 1):
        print(f"{color(f'{idx:2d})', '1;33')} {color(host, '92')}")

    user_input = input(color("\nEnter number or host name to connect: ", "1;36")).strip()

    # Try number input
    if user_input.isdigit():
        choice = int(user_input)
        if 1 <= choice <= len(hosts):
            host_to_connect = hosts[choice - 1]
        else:
            print(color("❌ Invalid number selected.", "91"))
            return
    else:
        # Try name match
        matches = [h for h in hosts if h.lower() == user_input.lower()]
        if not matches:
            print(color(f"❌ Host '{user_input}' not found.", "91"))
            return
        host_to_connect = matches[0]

    print(color(f"\n🔐 Connecting to {host_to_connect} ...", "1;32"))
    os.system(f'ssh {host_to_connect}')

def start_port_forwarding():
    config = parse_config()
    hosts = sorted([host for host in config if "*" not in host])

    if not hosts:
        print(color("⚠ No saved hosts found.", "91"))
        return

    print(color("\n🔌 Select Host for Port Forwarding:", "1;34"))
    for idx, host in enumerate(hosts, 1):
        print(f"{color(f'{idx:2d})', '1;33')} {color(host, '92')}")

    selection = input(color("\nEnter host number or name: ", "1;36")).strip()
    if selection.isdigit():
        idx = int(selection)
        if 1 <= idx <= len(hosts):
            selected_host = hosts[idx - 1]
        else:
            print(color("❌ Invalid host number.", "91"))
            return
    else:
        matches = [h for h in hosts if h.lower() == selection.lower()]
        if not matches:
            print(color("❌ Host not found.", "91"))
            return
        selected_host = matches[0]

    def prompt_port(prompt, default):
        while True:
            val = input(color(f"{prompt} [{default}]: ", "1;36")).strip()
            if not val:
                return default
            if val.isdigit():
                return val
            print(color("❌ Invalid port. Must be a number.", "91"))

    def prompt_text(prompt, default):
        val = input(color(f"{prompt} [{default}]: ", "1;36")).strip()
        return val if val else default

    local_port = prompt_port("🔸 Enter local port", "8080")
    remote_host = prompt_text("🔹 Enter remote host", "localhost")
    remote_port = prompt_port("📡 Enter remote port", "80")

    print(color(f"\n🔁 Forwarding localhost:{local_port} → {remote_host}:{remote_port} via {selected_host}", "92"))
    print(color("⏳ Tunnel is active. Press Ctrl+C to stop.", "90"))
    try:
        os.system(f"ssh -N -L {local_port}:{remote_host}:{remote_port} {selected_host}")
    except KeyboardInterrupt:
        print(color("\n🛑 Port forwarding stopped by user.", "91"))





def search_hosts():
    config = parse_config()
    hosts = sorted([host for host in config if "*" not in host])

    if not hosts:
        print(color("⚠ No saved hosts to search.", "91"))
        return

    keyword = input(color("🔍 Enter regex pattern to search: ", "1;36")).strip()
    if not keyword:
        print(color("⚠ Empty search. Try again.", "93"))
        return

    try:
        pattern = re.compile(keyword, re.IGNORECASE)
        matches = [host for host in hosts if pattern.search(host)]
    except re.error as e:
        print(color(f"❌ Invalid regex pattern: {e}", "91"))
        return

    if not matches:
        print(color("❌ No matches found.", "91"))
        return

    print(color("\n📄 Matching Hosts:", "1;34"))
    for i, host in enumerate(matches, 1):
        print(f"{color(f'{i:2d})', '1;33')} {color(host, '92')}")


def color(text, code):
    return f"\033[{code}m{text}\033[0m"

def main():
    ensure_config_file()

    while True:
        print()
        print(color("╔════════════════════════════╗", "1;36"))
        print(color("║        SSH MANAGER         ║", "1;36"))
        print(color("╚════════════════════════════╝", "1;36"))
        print(color("1)", "93"), "Add / Update Host")
        print(color("2)", "93"), "List All Hosts")
        print(color("3)", "93"), "Search Hosts")
        print(color("4)", "93"), "Connect to Host")
        print(color("5)", "93"), "Filter Hosts by Tag")
        print(color("6)", "93"), "Start Port Forwarding")
        print(color("7)", "91"), "Exit")


        choice = input(color("\nChoose an option (1-7): ", "1;33")).strip()

        if choice == '1':
            add_or_update_host()
        elif choice == '2':
            list_hosts()
        elif choice == '3':
            search_hosts()
        elif choice == '4':
            connect_to_host()
        elif choice == '5':
            filter_by_tag()
        elif choice == '6':
            start_port_forwarding()
        elif choice == '7':
            print(color("👋 Exiting SSH Manager. Goodbye!", "92"))
            sys.exit(0)
        else:
            print(color("❌ Invalid choice. Please enter a number from 1 to 7.", "91"))




if __name__ == "__main__":
    main()
