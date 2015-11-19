import os
import sys
import subprocess
from PySide import QtCore, QtGui

installFolder = os.path.split(os.path.split(os.path.abspath(__file__))[0])[0]

cmdArgs = ['git', 'pull']
p = subprocess.Popen(cmdArgs, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell = True, cwd = installFolder)
p.wait()
(stdout, stderr) = p.communicate()

app = QtGui.QApplication(sys.argv)
QtGui.QMessageBox.information(None, 'Zookeeper', stdout)
