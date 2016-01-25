import os
import sys
import zookeeper
from PySide import QtCore, QtGui
from zkSubmitter_impl import zkSubmitter
from zkFileUtils_impl import zk_uncFromDrivePath

class zkSoftimageLogHook(object):
  __app = None
  def __init__(self, app):
    self.__app = app

  def write(self, data):
    # py engine adds a newline at the end of the data except if
    # the statement was ended by a comma.
    data = "" if data == "\n" else data
    if data != "":
      self.__app.LogMessage(data)
    return None

class zkSoftimageSubmitter(zkSubmitter):

  __c = None
  __app = None
  __stdOutHook = None

  def __init__(self, connection, application, constants):
    super(zkSoftimageSubmitter, self).__init__('Softimage', connection)

    self.__app = application
    self.__c = constants

    if zkSoftimageSubmitter.__stdOutHook is None:
      self.__stdOutHook = zkSoftimageLogHook(self.__app)
      sys.stdout = self.__stdOutHook
      sys.stderr = self.__stdOutHook

  def getDCCName(self):
    return 'Softimage'

  def getDCCVersion(self):
    path = self.__app.GetInstallationPath2(self.__c.siFactoryPath)
    path = path.replace('\\', '/')
    version = path.rpartition('/')[2]
    version = version.partition(' ')[2]
    version = version.partition(' ')[0]
    return version

  def getRendererName(self):
    return str(self.__app.ActiveProject.ActiveScene.ActivePass.Renderer.Name)

  def getRendererVersion(self):
    return str(self.__app.ActiveProject.ActiveScene.ActivePass.Renderer.Version)

  def getInputPath(self):
    return str(self.__app.ActiveProject.ActiveScene.Parameters.GetItem('filename').Value)

  def performPostDialogChecks(self, fields):
    # check all outputs, and if there are some files on disc already exist
    results = {}
    for field in fields:
      results[field['name']] = field['value']

    if results.get('overwrite', False):
      return True

    scene = self.__app.ActiveProject.ActiveScene
    currentPass = scene.ActivePass
    frameBuffers = currentPass.FrameBuffers

    # we need 5 padding...
    self.__app.SetValue("Passes.RenderOptions.FramePadding", 5)

    existingFiles = []
    for i in range(frameBuffers.Count):
      fb = frameBuffers(i)
      if not fb.Parameters.GetItem('Enabled').Value:
        continue

      # for now let's check last and first frame
      times = [results['framestart'], results['frameend']]
      for t in times:
        path = fb.GetResolvedPath(t)
        path = zk_uncFromDrivePath(path)
        if os.path.exists(path):
          existingFiles += [path]
    if len(existingFiles) > 0:
      msgBox = QtGui.QMessageBox()
      msgBox.setText("Are you sure?")
      text = "There are already files on disc which will be\noverwritten if you submit this job!\n\n%s\n\nThis info has been copied to the clipboard." % '\n'.join(existingFiles)
      clipboard = QtGui.QApplication.clipboard()
      clipboard.setText(text)
      msgBox.setInformativeText(text)
      msgBox.setStandardButtons(QtGui.QMessageBox.Ok | QtGui.QMessageBox.Cancel)
      msgBox.setDefaultButton(QtGui.QMessageBox.Ok)
      ret = msgBox.exec_()
      return ret == QtGui.QMessageBox.Ok

    return True

  def getExternalFilePaths(self):
    scene = self.__app.ActiveProject.ActiveScene
    currentPass = scene.ActivePass

    result = []
    extFiles = scene.ExternalFiles
    for i in range(extFiles.Count):
      extFile = extFiles(i)
      resolvedPath = extFile.ResolvedPath

      # invalid rigid body cache
      if resolvedPath.lower().endswith('rigidbodycache.xsi'):
        continue

      for j in range(extFile.NumberOfFilesInSequence):
        result += [{'path': extFile.GetFileInSequence(j), 'exist': True, 'group': extFile.FileType}]

    # also add the outputs for validation
    frameBuffers = currentPass.FrameBuffers
    for i in range(frameBuffers.Count):
      fb = frameBuffers(i)
      if not fb.Parameters.GetItem('Enabled').Value:
        continue
      result += [{'path': fb.GetResolvedPath(1), 'exist': False, 'group': 'render output'}]

    # redshift IES profile files
    objects = self.__app.FindObjects('', '{6495C5C1-FD18-474E-9703-AEA66631F7A7}')
    for i in range(objects.Count):
      o = objects(i)
      if not o.Name.lower() == 'redshift_ies':
        continue
      iesPath = str(o.profileString.Value)
      if not os.path.exists(iesPath):
        iesPath = os.path.join(self.__app.ActiveProject.Path, iesPath)
      result += [{'path': iesPath, 'exist': True, 'group': 'IESProfiles'}]

    # todo: ICE caches etc, ass caches etc..

    return result

  def getProjectDefaultName(self):
    prop = self.__app.ActiveSceneRoot.Properties.GetItem('zookeeper')
    if prop:
      param = prop.Parameters.GetItem('projectid')
      if param:
        proj = zookeeper.zkDB.zkProject.getById(self.connection, id = int(param.Value))
        if proj:
          return proj.name
    return None

  def getJobDefaultName(self):
    sceneName = str(self.__app.ActiveProject.ActiveScene.Name)
    passName = str(self.__app.ActiveProject.ActiveScene.ActivePass.Name)
    return '%s|%s' % (sceneName, passName)

  def getExtraFields(self):
    fields = []

    scene = self.__app.ActiveProject.ActiveScene
    currentPass = scene.ActivePass
    sceneOptions = scene.PassContainer.Properties.GetItem('Scene Render Options')

    frameRangeSource = int(currentPass.Parameters.GetItem('FrameRangeSource').Value)
    framestart = 1
    frameend = 1
    framestep = 1
    
    if frameRangeSource == 3: # scene options
      frameRangeSource = int(sceneOptions.Parameters.GetItem('FrameRangeSource').Value)
      if frameRangeSource == 0:
        framestart = int(sceneOptions.Parameters.GetItem('FrameStart').Value)
        frameend = int(sceneOptions.Parameters.GetItem('FrameEnd').Value)
        framestep = int(sceneOptions.Parameters.GetItem('FrameStep').Value)
      else:
        print "Frame Set / Timeline not supported."
    elif frameRangeSource == 0: # range
      framestart = int(currentPass.Parameters.GetItem('FrameStart').Value)
      frameend = int(currentPass.Parameters.GetItem('FrameEnd').Value)
      framestep = int(currentPass.Parameters.GetItem('FrameStep').Value)
    else:
      print "Frame Set / Timeline not supported."


    # make passes names a list to sort alphabetically (...just for the DialogBox)
    passes = scene.Passes
    passesNameList = list( [ p.Name for p in passes ] )
    passesNameList.sort( key=lambda y: y.lower() ) # to sort Softimage style...

    # get the selection and set value=True in the Dialog if it matches the pass name
    selectList = list( self.__app.Selection )

    for pName in passesNameList:
      enabled = pName in [ s.Name for s in selectList]
      fields += [{'name': 'pass_'+pName, 'label': 'Pass <b>'+pName+"</b>", 'value': enabled, 'type': 'bool'}]


    fields += [{'name': 'framestart', 'label': 'First Frame', 'value': framestart, 'type': 'int', 'tooltip': 'The first frame of the sequence'}]
    fields += [{'name': 'frameend', 'label': 'Last Frame', 'value': frameend, 'type': 'int', 'tooltip': 'The last frame of the sequence'}]
    fields += [{'name': 'framestep', 'label': 'Frame Step', 'value': framestep, 'type': 'int', 'tooltip': 'The stepping across the sequence'}]
    fields += [{'name': 'packagesize', 'label': 'Package Size', 'value': 20, 'type': 'int', 'tooltip': 'The number of frames which are processed as a batch.'}]
    fields += [{'name': 'highprio_firstlast', 'label': 'Bump boundaries', 'value': False, 'type': 'bool', 'tooltip': 'Use higher priority for the first and last frame.'}]
    # fields += [{'name': 'capturejob', 'label': 'capturejob', 'value': False, 'type': 'bool', 'tooltip': 'Enabling this also creates a capture movie.'}]

    prop = self.__app.ActiveSceneRoot.Properties.GetItem('zookeeper')
    if prop:
      for f in fields:
        param = prop.Parameters.GetItem(f['name'])
        if param:
          if isinstance(f['value'], int):
            f['value'] = int(param.Value)
          elif isinstance(f['value'], bool):
            f['value'] = bool(param.Value)
          elif isinstance(f['value'], str):
            f['value'] = str(param.Value)

    return fields

  def validatePath(self, path, shouldExist = True):
    instPath = self.__app.GetInstallationPath2(self.__c.siFactoryPath).lower().replace('\\', '/')
    if path.lower().replace('\\', '/').startswith(instPath):
      return True
    return super(zkSoftimageSubmitter, self).validatePath(path, shouldExist=shouldExist)

  def createJobFramesAndOutput(self, fields, connection, bracket, project, input):

    #persist all standard changes in scene....
    prop = self.__app.ActiveSceneRoot.Properties.GetItem('zookeeper')
    if not prop:
      self.__app.AddProp("Custom_parameter_list", "Scene_Root", "", "zookeeper", "")
      self.__app.SIAddCustomParameter("Scene_Root.zookeeper", "projectid", "siString", "", 0, 1, "", 4, 0, 1, "", "")
      self.__app.SIAddCustomParameter("Scene_Root.zookeeper", "mincores", "siString", "", 0, 1, "", 4, 0, 1, "", "")
      self.__app.SIAddCustomParameter("Scene_Root.zookeeper", "minramgb", "siString", "", 0, 1, "", 4, 0, 1, "", "")
      self.__app.SIAddCustomParameter("Scene_Root.zookeeper", "mingpuramgb", "siString", "", 0, 1, "", 4, 0, 1, "", "")
      self.__app.SIAddCustomParameter("Scene_Root.zookeeper", "packagesize", "siString", "", 0, 1, "", 4, 0, 1, "", "")
      prop = self.__app.ActiveSceneRoot.Properties.GetItem('zookeeper')

    if prop:
      for f in fields:
        param = prop.Parameters.GetItem(f['name'])
        if param:
          param.Value = f['value']

    results = {}
    for field in fields:
      results[field['name']] = field['value']

    scene = self.__app.ActiveProject.ActiveScene
    currentPass = scene.ActivePass
    frameBuffers = currentPass.FrameBuffers

    framestart = results['framestart']
    frameend = results['frameend']
    framestep = results['framestep']
    packagesize = results['packagesize']
    capturejob = results.get('capturejob', False)
    highprio_firstlast = results['highprio_firstlast']

    # submit all external files
    xsiFiles = scene.ExternalFiles
    for i in range(xsiFiles.Count):
      xsiFile = xsiFiles(i)
      resolvedPath = xsiFile.ResolvedPath

      # invalid rigid body cache
      if resolvedPath.lower().endswith('rigidbodycache.xsi'):
        continue

      resolution = -1
      if xsiFile.FileType == 'Models':
        param = xsiFile.Owners(0)
        model = param.Parent
        if param.Name == 'res'+str(model.active_resolution.value):
          resolution = model.active_resolution.value
      f = zookeeper.zkDB.zkExternalFile.getOrCreateByProjectAndPaths(self.connection, project.id, xsiFile.Path, xsiFile.ResolvedPath, type = xsiFile.FileType, resolution = resolution)
      if f.id is None:
        self.__app.LogMessage('Error: Could not create external file for '+xsiFile.Path)

    # redshift IES profile files
    objects = self.__app.FindObjects('', '{6495C5C1-FD18-474E-9703-AEA66631F7A7}')
    for i in range(objects.Count):
      o = objects(i)
      if not o.Name.lower() == 'redshift_ies':
        continue
      iesPath = str(o.profileString.Value)
      resolvedPath = iesPath
      if not os.path.exists(iesPath):
        resolvedPath = os.path.join(self.__app.ActiveProject.Path, resolvedPath)
      f = zookeeper.zkDB.zkExternalFile.getOrCreateByProjectAndPaths(self.connection, project.id, iesPath, resolvedPath, type = 'IESProfiles', resolution = -1)
      if f.id is None:
        self.__app.LogMessage('Error: Could not create external file for '+iesPath)

    if capturejob:

      job = zookeeper.zkDB.zkJob.createNew(self.connection)
      job.project = project
      job.name = results['jobname']+' capture'
      job.input = input
      job.type = 'CAPTURE'
      self.decorateJobWithDefaults(fields, job)
      bracket.push(job)

      # make a single frame for the capture movie
      frame = zookeeper.zkDB.zkFrame.createNew(self.connection)
      frame.job = job
      frame.time = framestart
      frame.timeend = frameend
      frame.priority = 100
      job.pushFrameForSubmit(frame)

      # create a single output for the movie
      mainBuffer = frameBuffers(0)
      capturePath = str(mainBuffer.GetResolvedPath(framestart))
      capturePath = capturePath.rpartition('.')[0]
      capturePath += '.mov'
      output = zookeeper.zkDB.zkOutput.createNew(self.connection)
      output.frame = frame
      output.name = mainBuffer.Name
      output.path = zk_uncFromDrivePath(capturePath)
      frame.pushOutputForSubmit(output)

    passes = scene.Passes
    for i in range(passes.Count):
      passObj = passes(i)
      sceneName = str(scene.Name)
      passName = str(passObj.Name)

      if not results.get('pass_'+str(passObj.Name), False):
        continue

      job = zookeeper.zkDB.zkJob.createNew(self.connection)
      job.project = project
      job.name = '%s|%s' % (sceneName, passName)
      job.input = input
      job.type = 'ALL'
      self.decorateJobWithDefaults(fields, job)
      bracket.push(job)

      packageoffset = 0
      package = 0

      for f in range(framestart, frameend+1, framestep):

        self.__app.LogMessage('Submitting frame '+str(f))

        if packageoffset % packagesize == 0:
          package = package + 1
        packageoffset = packageoffset + 1

        frame = zookeeper.zkDB.zkFrame.createNew(self.connection)
        frame.job = job
        frame.time = f
        frame.priority = 50
        frame.package = package
        if highprio_firstlast:
          if f == framestart or f == frameend:
            frame.priority = 75
            frame.package = 1
        job.pushFrameForSubmit(frame)

