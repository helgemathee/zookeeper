import os
import sys
import glob
import time
import zookeeper
from PySide import QtCore, QtGui

from zkWorkThread_impl import zkWorkThread

def getSoftimageEnv(cfg, dccVersion):
  env = os.environ.copy()

  if not env.has_key('ADSKFLEX_LICENSE_FILE'):
    env['ADSKFLEX_LICENSE_FILE'] = ''
    env['SOFTIMAGE_LICENSE_METHOD'] = 'Standalone'
  else:
    env['SOFTIMAGE_LICENSE_METHOD'] = 'Network'

  env.update({
    'SI_HOME': 'C:\Program Files\Autodesk\Softimage %s' % dccVersion,
    'MI_ENABLE_PIPE_MODE': '1',
    'XSI_EXT': 'dll',
    'XSI_CPU': 'nt-x86-64',
    'XSI_HIGH_QUALITY_VIEWPORT_MAX_DOF_SAMPLES': '8',
    'XSI_HIGH_QUALITY_VIEWPORT_MAX_AO_SAMPLES': '8',
    'XSI_HIGH_QUALITY_VIEWPORT_MAX_REFLECT_SAMPLES': '1',
    'XSI_HIGH_QUALITY_VIEWPORT_MAX_SHADOW_SAMPLES': '8',
    'SOFTIMAGE_COMMONFILES': 'C:\Program Files\Common Files\Softimage',
    'SI_CER': '1',
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
    'XSI_USERHOME': env['XSI_USERROOT'] + '\\%s' % dccVersion.replace(' ', '_'),
    'MI_ROOT': env['SI_HOME'] + '\\Application\\rsrc',
    'MI_RAY3_SERVICE': 'mi-raysatsi2014_3_11_1_1',
    'MI_RAY_HOSTSFILE': env['XSI_USERROOT'] + '\\.ray3hosts',
    'MI_LIBRARY_PATH': env['XSI_BINDIR'] + '\\' + env['XSI_CPU'],
    # 'PATH': '%XSI_BINDIR%\\%XSI_CPU%%_CPU_REVISION%;%XSI_BINDIR%;%SOFTIMAGE_COMMONFILES%;%Path%''
    'SI_IMAGE_PATH': env['SI_HOME'] + '\\Application\\bin\sil',
    'SILicMethod': env['SOFTIMAGE_LICENSE_METHOD'],
    '_ADSK_LicServers': env['ADSKFLEX_LICENSE_FILE'],
  })
  return env

class zkSoftimageWorkThread(zkWorkThread):

  def __init__(self, connection, frame, parent = None):
    super(zkSoftimageWorkThread, self).__init__(connection, frame, parent)

  def run(self):
    super(zkSoftimageWorkThread, self).run()
    job = self.frame.job

    cfg = zookeeper.zkConfig()
    dccversion = job.dccversion
    folder = None
    for suffix in ['SP2', 'SP1', '']:
      folder = os.path.join(cfg.get('softimage_root_folder', ''), 'Softimage %s %s' % (dccversion, suffix))
      if os.path.exists(folder):
        if len(suffix) > 0:
          dccversion = dccversion + ' ' + suffix
        break

    if not os.path.exists(folder):
      return

    bin = os.path.join(folder, 'Application', 'bin', 'xsibatch.exe')

    env = getSoftimageEnv(cfg, dccversion)

    zookeeperPath = os.path.split(os.path.split(zookeeper.__file__)[0])[0]
    dccPath = os.path.join(zookeeperPath, 'dccs', 'Softimage')

    # create a settings template
    prefsFolder = os.path.join(env['XSI_USERHOME'], 'Data', 'Preferences')
    if not os.path.exists(prefsFolder):
      os.makedirs(prefsFolder)
    template = open(os.path.join(dccPath, 'default.xsipref'), 'rb').read()
    template = template.replace('%VERSION%', dccversion)

    # localize workgroups
    localPath = cfg.get('softimage_workgroup_root')
    remotePath = zookeeper.zkDB.zkSetting.getByName(self.connection, 'softimage_workgroup_root').value

    self.log('Synchronizing workgroups...')
    zookeeper.zkClient.zk_synchronizeFolder(remotePath, localPath, logFunc = self.logCallback)

    workgroups = []

    workGroupRoot = cfg.get('softimage_workgroup_root', '')
    workGroupGeneral = os.path.join(workGroupRoot, 'general')
    if not os.path.exists(workGroupGeneral):
      os.makedirs(workGroupGeneral)
    for f in glob.glob(os.path.join(workGroupGeneral, '*')):
      if f.startswith('.'):
        continue
      workgroups += [os.path.normpath(f)]
    workGroupRender = os.path.join(workGroupRoot, 'renderer', job.renderer, job.rendererversion, 'Softimage%s' % dccversion.replace(' ', ''))
    if os.path.exists(workGroupRender):
      workgroups += [os.path.normpath(workGroupRender)]

    template = template.replace('%WORKGROUPS%', ';'.join(workgroups))
    open(os.path.join(prefsFolder, 'default.xsipref'), 'wb').write(template)

    args = ['-processing', '-script']
    args += [os.path.join(dccPath, 'munch.py')]

    self.launchSubProcess(bin, args = args, env = env)
    self.waitForSubProcess()

