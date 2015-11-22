ZooKeeper
===============================

ZooKeeper is an open source rendering framework. Currently supported are:

- Softimage, Mental Ray and RedShift

Supported operating systems
===============================
- Windows: 7+, 8.0, 8.1, 10.0


Client Installation
===========================

A) Installer package https://www.dropbox.com/s/2r6b5k0rivwgaa5/installers.zip?dl=0

- Install 01_git - right click 'Run as administrator', use all defaults
- Install 02_python-02.7.9, for all users
- Install 03_pywin...
- Install 04_psutil... (psutil might get caught as a trojan - but it's not :-))
- Install 05_mysql...
- Install 06_vcredist...

B) Environment variables

- PATH: C:\Python27;C:\Python27\Scripts
- PYTHONPATH: C:\zookeeper

C) Within a command shell (cmd) type

```
pip install pyside
git clone https://github.com/helgemathee/zookeeper.git c:\zookeeper
```

If you get "git is an unknown command" or such, please use the GIT Cmd instead of the windows default CMD.

D) Shortcuts ( you can use the icon found in "C:\zookeeper\launchers")

- A shortcut on the desktop to "c:\zookeeper\launchers\ZooKeeperConfig.pyw" named "Config"
- A shortcut on the desktop to "c:\zookeeper\launchers\ZooKeeperManager.pyw" named "Manager"
- A shortcut on the desktop to "c:\zookeeper\launchers\ZooKeeperMunch.pyw" named "Munch"

E) Launch the local config tool 

- Double click on "C:\zookeeper\launchers\ZooKeeperConfig.pyw" or use your new shortcut.
- Fill in all defaults correctly
- It's highly recommended to configure a scratch disc!

F) Softimage installation for submissions

- Connect to the workgroup C:\zookeeper\dccs\Softimage\Workgroup
- In the Scripting Preferences set Python as the scripting language and disable the checkbox "Use Python Installed with Softimage"

Usage
=================

All tools for interacting with ZooKeeper can be found in the launchers folder of the installation (c:\zookeeper\launchers)

- UpdateInstallation: Pulls the toolset off Github and updates the current installation.
- ZooKeeperConfig: The configuration utility for the local client
- ZooKeeperManager: The render manager
- ZooKeeperMunch: The render client

