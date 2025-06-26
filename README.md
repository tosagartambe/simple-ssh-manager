===========================================
 Simple SSH Manager
===========================================

A simple, cross-platform Python tool to manage SSH host configs and port forwarding using your ~/.ssh/config file.

Works on:
- ✅ Windows
- ✅ Linux
- ✅ macOS

Requirements:
- Python 3.x installed
- OpenSSH installed and accessible in PATH

-------------------------------------------
🎯 Features
-------------------------------------------

1. Add / Update SSH Hosts
2. Save Host aliases, User, Port, IdentityFile
3. Add and search using tags
4. Connect to hosts by number or name
5. Start local port forwarding (`ssh -L`)
6. Auto-detect defaults from `Host *` config
7. No external Python dependencies required

-------------------------------------------
🚀 How to Use
-------------------------------------------

1. Download the script:

   simple-ssh-manager.py

2. Make it executable:

   On Linux/macOS:
     chmod +x simple-ssh-manager.py

   On Windows:
     (No action needed — just double click or run from terminal)

3. Run it:

   python simple-ssh-manager.py

-------------------------------------------
🧩 Add a Host Example
-------------------------------------------

Choose an option (1-7): 1
Enter host alias (e.g., myserver): dev-api
HostName [example.com]: 10.0.0.12
User [ubuntu]:
Port [22]:
IdentityFile [~/.ssh/id_rsa]:
Tags (comma separated) [none]: dev,api

✅ Host 'dev-api' added successfully.

-------------------------------------------
🔁 Port Forwarding Example
-------------------------------------------

Choose an option (1-7): 6
Select host: dev-api
Local port: 8080
Remote host: localhost
Remote port: 8000

🔁 Forwarding localhost:8080 → localhost:8000 via dev-api
⏳ Press Ctrl+C to stop

-------------------------------------------
📂 Recommended File Location
-------------------------------------------

Save it somewhere like:

Linux/macOS:
  ~/.local/bin/sshmgr
  (and add ~/.local/bin to PATH)

Windows:
  C:\Users\YourName\Scripts\sshmgr.py
  (add folder to system PATH, or create a shortcut)

-------------------------------------------
📜 License

MIT License  
(c) 2025 Sagar Tambe

