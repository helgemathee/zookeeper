import os
import subprocess
from PySide import QtCore, QtGui

installFolder = os.path.split(os.path.split(os.path.abspath(__file__))[0])[0]
print installFolder

cmdArgs = ['git', 'pull']
p = subprocess.Popen(cmdArgs, cwd = installFolder)
p.wait()
