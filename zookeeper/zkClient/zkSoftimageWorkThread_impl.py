import os
import sys
import time
import zookeeper
from PySide import QtCore, QtGui

from zkWorkThread_impl import zkWorkThread

class zkSoftimageWorkThread(zkWorkThread):

  def __init__(self, connection, frame, parent = None):
    super(zkSoftimageWorkThread, self).__init__(connection, frame, parent)

  def run(self):
    super(zkSoftimageWorkThread, self).run()
    job = self.frame.job

    cfg = zookeeper.zkConfig()
    folder = os.path.join(cfg.get('softimage_root_folder', ''), 'Softimage %s' % job.dccversion)
    bin = os.path.join(folder, 'Application', 'bin', 'xsibatch.exe')

    env = os.environ.copy()

    env.update({
      'SI_HOME': 'C:\Program Files\Autodesk\Softimage %s' % job.dccversion,
      'MI_ENABLE_PIPE_MODE': '1',
      'XSI_EXT': 'dll',
      'XSI_CPU': 'nt-x86-64',
      'XSI_HIGH_QUALITY_VIEWPORT_MAX_DOF_SAMPLES': '8',
      'XSI_HIGH_QUALITY_VIEWPORT_MAX_AO_SAMPLES': '8',
      'XSI_HIGH_QUALITY_VIEWPORT_MAX_REFLECT_SAMPLES': '1',
      'XSI_HIGH_QUALITY_VIEWPORT_MAX_SHADOW_SAMPLES': '8',
      'SOFTIMAGE_COMMONFILES': 'C:\Program Files\Common Files\Softimage',
      'SI_CER': '1',
      'SOFTIMAGE_LICENSE_METHOD': 'Standalone', # Licensing method: Standalone | MSSA | Network
      'ADSKFLEX_LICENSE_FILE': '', # License servers specified from the setup. Format: [port1]@host1[;[port2]@host2]...
      'XSI_USERROOT': cfg.get('softimage_user_root'),
    })
    env.update({
      'XSI_HOME': env['SI_HOME'],
      'XSI_BINDIR': env['SI_HOME'] + '\\Application\\bin',
    })
    env.update({
      'SI_DBDIR': env['XSI_USERROOT'],
      'XSISDK_ROOT': env['SI_HOME'] + '\\XSISDK',
      'CROSSWALKSDK_ROOT': env['SI_HOME'] + '\\XSISDK',
      'XSI_CPU_OPT': env['XSI_CPU'],
      'XSI_USERHOME': env['XSI_USERROOT'] + '\\Autodesk\\Softimage_%s' % job.dccversion.replace(' ', '_'),
      'MI_ROOT': env['SI_HOME'] + '\\Application\\rsrc',
      'MI_RAY3_SERVICE': 'mi-raysatsi2014_3_11_1_1',
      'MI_RAY_HOSTSFILE': env['XSI_USERROOT'] + '\\.ray3hosts',
      'MI_LIBRARY_PATH': env['XSI_BINDIR'] + '\\' + env['XSI_CPU'],
      # 'PATH': '%XSI_BINDIR%\\%XSI_CPU%%_CPU_REVISION%;%XSI_BINDIR%;%SOFTIMAGE_COMMONFILES%;%Path%''
      'SI_IMAGE_PATH': env['SI_HOME'] + '\\Application\\bin\sil',
      'SILicMethod': env['SOFTIMAGE_LICENSE_METHOD'],
      '_ADSK_LicServers': env['ADSKFLEX_LICENSE_FILE'],
    })

    for key in env:
      env[key] = str(env[key])

    zookeeperPath = os.path.split(os.path.split(zookeeper.__file__)[0])[0]
    args = ['-script']
    args += [os.path.join(zookeeperPath, 'dccs', 'Softimage', 'munch.py')]

    self.launchSubProcess(bin, args = args, env = env)
    self.waitForSubProcess()

