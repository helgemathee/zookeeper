Supported operating systems
===============================
- Windows: 7+, 8.0, 8.1, 10.0


Client Installation
===========================

A) Installer folder
- Install 01_git - right click 'Run as administrator', use all defaults
- Install 02_python-02.7.9, for all users
- Install 03_pywin...
- Install 04_psutil...
- Install 05_mysql...
B) Environment variables
- PATH: C:\Python27;C:\Python27\Scripts
- PYTHONPATH: C:\zookeeper

C) Within a command shell (cmd) type

```
pip install win_unc
pip install pyside
git clone https://github.com/helgemathee/zookeeper.git c:\zookeeper
```

D) Shortcuts ( you can use the icon found in "C:\zookeeper\launchers")
- A shortcut on the desktop to "c:\zookeeper\launchers\ZooKeeperConfig.pyw" named "Config"
- A shortcut on the desktop to "c:\zookeeper\launchers\ZooKeeperManager.pyw" named "Manager"
- A shortcut on the desktop to "c:\zookeeper\launchers\ZooKeeperLauncher.pyw" named "Launcher"

E) Launch the local config tool 
- Double click on "C:\zookeeper\launchers\ZooKeeperConfig.pyw" or use your new shortcut.
- Fill in all defaults correctly
- It's highly recommended to configure a scratch disc!
