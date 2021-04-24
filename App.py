import os
import shutil
from pathlib import Path

from classes.ActionVerifier import ActionVerifier
from classes.Message import Message
from classes.Ftp import Ftp

from constants.textStyles import textStyles
from constants.settings import settings
from constants.textStyles import textStyles
from constants.environments import environments as envs
from constants.actions import Actions as Act
from constants.nsAccessors import nsAccessors

from helpers.getNamespace import getNamespace
from helpers.styledText import styledText
from helpers.execCmd import execCmd
from helpers.getNextPath import getNextPath
from helpers.getUserConfirm import getUserConfirm
from helpers.getUserInput import getUserInput
from helpers.trimSpaces import trimSpaces
from helpers.getSingleActionParam import getSingleActionParam
from helpers.getTimestamp import getTimestamp
from helpers.getInputPrompt import getInputPrompt
from helpers.processAction import processAction

from __locale.printHelp import printHelp

commonNS = getNamespace(nsAccessors["Common"])
rushNS = getNamespace(nsAccessors["Rush"])
jumpNS = getNamespace(nsAccessors["Jump"])
cdNS = getNamespace(nsAccessors["Cd"])
mkdirNS = getNamespace(nsAccessors["Mkdir"])
deleteNS = getNamespace(nsAccessors["Delete"])
dropNS = getNamespace(nsAccessors["Drop"])
takeNS = getNamespace(nsAccessors["Take"])
clearNS = getNamespace(nsAccessors["Clear"])
lsNS = getNamespace(nsAccessors["Ls"])
statusNS = getNamespace(nsAccessors["Status"])

Av = ActionVerifier()
Msg = Message()

class App:
  def __init__(self):
    self.ftp = None
    self.connected = False
    self.loginData = {}
    self.action = ""
    self.env = envs["Local"]
    self.pathLocal = str(Path.home())
    self.pathRemote = ""


  #------------- Utils -------------#


  def pingServer(self, message=True):
    try:
      self.ftp.voidcmd("NOOP")
    except:
      if message:
        Msg.error(commonNS["connection_lost"])
      self.setStatusDisconnected()
    pass

  def setStatusDisconnected(self):
    self.ftp = None
    self.connected = False
    self.env = envs["Local"]
    self.pathRemote = ""
    pass


  def login(self):
    loginData = self.loginData
    try:
      self.ftp = Ftp(
        loginData["host"],
        loginData["user"],
        loginData["passwd"],
        port=loginData["port"],
        timeout=settings["timeout"]
      )
      self.ftp.login(user=loginData["user"], passwd=loginData["passwd"])
      self.connected = True
      self.env = envs["Remote"]
      self.pathRemote = self.ftp.pwd()
      Msg.serverResponse(self.ftp.getwelcome())
      return True
    except Exception as e:
      self.setStatusDisconnected()
      Msg.serverResponse(e)
      return False
    pass


  def changeLocalPath(self, nextPath):
    os.chdir(nextPath)
    self.pathLocal = nextPath
    pass

  
  def changeRemotePath(self, nextPath):
    self.ftp.cwd(nextPath)
    self.pathRemote = nextPath 
    pass
  

  def rmFtpTree(self, path):
    pathList = self.ftp.list(path, extra=True)
    for target in pathList:
      preparedTargetPath = getNextPath(path, target["name"])
      if target["directory"] == "d":
        self.rmFtpTree(preparedTargetPath)
      else:
        self.ftp.delete(preparedTargetPath)
    self.ftp.rmd(path)
    pass

  
  def deleteLocal(self, target):
    _, targetName = os.path.split(target)
    suspendText = deleteNS["deleting"].format(target=targetName)
    successText = deleteNS["success"]
    localTargetPath = getNextPath(self.pathLocal, target)
    Msg.suspend(commonNS["processing"])
    if os.path.isfile(localTargetPath):
      confirmMsg = deleteNS["delete_file"].format(fileName=targetName)
      confirmDelFile = getUserConfirm(confirmMsg)
      if confirmDelFile:
        Msg.suspend(suspendText)
        os.remove(localTargetPath)
        Msg.success(successText)
    elif os.path.isdir(localTargetPath):
      confirmMsg = deleteNS["delete_dir"].format(dirName=targetName)
      confirmDelDir = getUserConfirm(confirmMsg)
      if confirmDelDir:
        Msg.suspend(suspendText)
        shutil.rmtree(localTargetPath)
        Msg.success(successText)
    else:
      raise
    pass


  def deleteRemote(self, target):
    _, targetName = os.path.split(target)
    suspendText = deleteNS["deleting"].format(target=targetName)
    successText = deleteNS["success"]
    remoteTargetPath = getNextPath(self.pathRemote, target)
    if self.ftp.isDir(remoteTargetPath):
      confirmMsg = deleteNS["delete_dir"].format(dirName=targetName)
      confirmDelDir = getUserConfirm(confirmMsg)
      if confirmDelDir:
        Msg.suspend(suspendText)
        self.rmFtpTree(remoteTargetPath)
        Msg.success(successText)
    elif self.ftp.isFile(remoteTargetPath):
      confirmMsg = deleteNS["delete_file"].format(fileName=targetName)
      confirmDelFile = getUserConfirm(confirmMsg)
      if confirmDelFile:
        Msg.suspend(suspendText)
        self.ftp.delete(remoteTargetPath)
        Msg.success(successText)
    else:
      raise
    pass


  def uploadFile(self, targetPath, pathExists, override):
    _, fileName = os.path.split(targetPath)
    fileNameToUpload = fileName
    if not override and pathExists:
      timestamp = getTimestamp()
      fileNameToUpload = "{time}_{file}".format(time=timestamp, file=fileName)
    self.ftp.put(targetPath, fileNameToUpload)
    pass


  def uploadTree(self, targetPath, pathExists, override):
    _, dirName = os.path.split(targetPath)
    dirNameToCreate = dirName
    if not override and pathExists:
      timestamp = getTimestamp()
      dirNameToCreate = "{time}_{dir}".format(time=timestamp, dir=dirName)
    remoteDirPath = getNextPath(self.pathRemote, dirNameToCreate)
    if not pathExists or (pathExists and not override):
      self.ftp.mkd(remoteDirPath)
    self.changeRemotePath(remoteDirPath)
    for el in os.listdir(targetPath):
      elPath = getNextPath(targetPath, el)
      remoteElPath = getNextPath(self.pathRemote, el)
      if os.path.isdir(elPath):
        innerExists = False
        if self.ftp.exists(el, self.pathRemote):
          innerExists = True
        self.uploadTree(elPath, innerExists, True)
      else:
        self.ftp.put(elPath, el)
    backPath = getNextPath(self.pathRemote, "..")
    self.changeRemotePath(backPath)
    pass


  def downloadFile(self, targetPath, pathExists, override):
    _, fileName = os.path.split(targetPath)
    fileNameToCreate = fileName
    if not override and pathExists:
      timestamp = getTimestamp()
      fileNameToCreate = "{time}_{file}".format(time=timestamp, file=fileName)
    localFileName = getNextPath(self.pathLocal, fileNameToCreate)
    self.ftp.get(targetPath, localFileName)
    pass


  def downloadTree(self, targetPath, pathExists, override):
    _, dirName = os.path.split(targetPath)
    dirNameToCreate = dirName
    if not override and pathExists:
      timestamp = getTimestamp()
      dirNameToCreate = "{time}_{dir}".format(time=timestamp, dir=dirName)
    localDirPath = getNextPath(self.pathLocal, dirNameToCreate)
    if not pathExists or (pathExists and not override):
      os.mkdir(localDirPath)
    self.changeLocalPath(localDirPath)
    targetList = self.ftp.list(targetPath, extra=True)
    for el in targetList:
      elPath = getNextPath(targetPath, el["name"])
      localElPath = getNextPath(self.pathLocal, el["name"])
      if el["directory"] == "d":
        innerExists = False
        if os.path.exists(localElPath):
          innerExists = True
        self.downloadTree(elPath, innerExists, True)
      else:
        localFileName = getNextPath(self.pathLocal, el["name"])
        self.ftp.get(elPath, localFileName)  
    backPath = getNextPath(self.pathLocal, "..")
    self.changeLocalPath(backPath)
    pass


  #------------- Actions -------------#


  def cd(self):
    dest = getSingleActionParam(Act["Cd"], self.action)
    if self.env == envs["Local"]:
      nextLocalPath = getNextPath(self.pathLocal, dest)
      if os.path.exists(nextLocalPath):
        self.changeLocalPath(nextLocalPath)  
      else:
        Msg.error(cdNS["error"].format(dest=nextLocalPath))
    else:
      self.pingServer()
      if self.connected:
        try:
          nextRemotePath = getNextPath(self.pathRemote, dest)
          self.changeRemotePath(nextRemotePath)
        except:
          Msg.error(cdNS["error"].format(dest=nextRemotePath))
    pass


  def clear(self):
    clearResult = execCmd("clear")
    if clearResult:
      print(clearResult)
    else:
      Msg.error(clearNS["error"])
    pass


  def delete(self):
    target = getSingleActionParam(Act["Delete"], self.action)
    Msg.suspend(commonNS["processing"])
    try:
      if self.env == envs["Local"]:
        self.deleteLocal(target)
      else:
        self.pingServer()
        if self.connected:
          self.deleteRemote(target)
    except:
      Msg.error(deleteNS["error"].format(target=target))   
    pass


  def drop(self):
    self.pingServer(message=False)
    if self.connected:
      Msg.suspend(commonNS["processing"])
      override = False
      pathExists = False
      target = getSingleActionParam(Act["Drop"], self.action)
      targetPath = getNextPath(self.pathLocal, target)
      _, targetName = os.path.split(target)
      if os.path.exists(targetPath):
        if self.ftp.exists(targetName, self.pathRemote):
          pathExists = True
          existsMsg = dropNS["exists"].format(target=targetName)
          confirmOverride = getUserConfirm(existsMsg)
          if confirmOverride:
            override = True
        try:
          Msg.suspend(dropNS["progress"])
          if os.path.isfile(targetPath):
            self.uploadFile(targetPath, pathExists, override)
          elif os.path.isdir(targetPath):
            currentRemotePath = self.pathRemote
            self.uploadTree(targetPath, pathExists, override)
            self.changeRemotePath(currentRemotePath)
          else:
            raise Exception("Unable to define local path")
          Msg.success(dropNS["success"])
        except:
          Msg.error(dropNS["transfer_error"])
      else:
        Msg.error(dropNS["invalid_path"])
    else:
      Msg.error(dropNS["not_connected"])
    pass


  def exit(self):
    self.pingServer(message=False)
    if self.connected and self.ftp:
      self.ftp.quit()
    pass


  def help(self):
    printHelp()
    pass


  def jump(self):
    jumpTo = getSingleActionParam(Act["Jump"], self.action)
    if jumpTo == envs["Local"]:
      self.env = envs["Local"]
    else:
      self.pingServer(message=False)
      if self.connected:
        self.env = envs["Remote"]
      else:
        Msg.error(jumpNS["not_connected"])
    pass


  def ls(self):
    if self.env == envs["Remote"]:
      self.pingServer()
      if self.connected:
        try:
          self.ftp.retrlines("LIST")
        except:
          Msg.error(lsNS["error"])
    else:
      try:
        if os.path.exists(self.pathLocal):
          os.chdir(self.pathLocal)
          cmd = "ls -l"
          output = execCmd(cmd)
          print(output)
        else:
          raise
      except:
        Msg.error(lsNS["error"])
    pass


  def mkdir(self):
    dirName = getSingleActionParam(Act["Mkdir"], self.action)
    try:
      if self.env == envs["Local"]:
        localDirPath = getNextPath(self.pathLocal, dirName)
        os.mkdir(localDirPath)
      else:
        self.pingServer()
        if self.connected:
          remoteDirPath = getNextPath(self.pathRemote, dirName)
          self.ftp.mkd(remoteDirPath)
    except:
      Msg.error(mkdirNS["error"].format(dirName=dirName))
    pass


  def rush(self):
    hostStr = getSingleActionParam(Act["Rush"], self.action)
    loginStr = rushNS["login"]["user"]
    passwdStr = rushNS["login"]["passwd"]
    portSrt = rushNS["login"]["port"]
    userInput = getUserInput([loginStr, passwdStr, portSrt])
    self.loginData = {
      "host": hostStr,
      "user": userInput[loginStr],
      "passwd": userInput[passwdStr],
      "port": userInput[portSrt] or settings["port"]
    }
    Msg.suspend(rushNS["connecting"].format(host=self.loginData["host"]))
    if self.login():
      Msg.success(rushNS["connected"].format(host=self.loginData["host"]))
    else:
      Msg.error(rushNS["connecting_error"].format(host=self.loginData["host"]))
    pass


  def take(self):
    self.pingServer(message=False)
    if self.connected:
      Msg.suspend(commonNS["processing"])
      override = False
      pathExists = False
      target = getSingleActionParam(Act["Take"], self.action)
      targetPath = getNextPath(self.pathRemote, target)
      _, targetName = os.path.split(targetPath)
      localTargetPath = getNextPath(self.pathLocal, targetName)
      if os.path.exists(localTargetPath):
        pathExists = True
        confirmOverride = getUserConfirm(takeNS["exists"].format(target=targetName))
        if confirmOverride:
          override = True
      try:
        Msg.suspend(takeNS["progress"])
        if self.ftp.isDir(targetPath):
          currentLocalPath = self.pathLocal
          self.downloadTree(targetPath, pathExists, override)
          self.changeLocalPath(currentLocalPath)
        else:
          self.downloadFile(targetPath, pathExists, override)
        Msg.success(takeNS["success"])
      except:
        Msg.error(takeNS["transfer_error"])
    else:
      Msg.error(takeNS["not_connected"])
    pass


  def whereAmI(self):
    if self.env == envs["Local"]:
      print(self.pathLocal)
    else:
      self.pingServer()
      if self.connected:
        print(self.pathRemote)
    pass


  def whoAmI(self):
    if self.env == envs["Local"]:
      print(execCmd("whoami"))
    else:
      self.pingServer()
      if self.connected:
        print(self.loginData["user"])
    pass


  def status(self):
    try:
      self.ftp.voidcmd("NOOP")
      Msg.serverResponse(self.ftp.getwelcome())
      Msg.success(statusNS["connected_title"])
      Msg.default(statusNS["connected_data"].format(
        host=self.loginData["host"],
        user=self.loginData["user"],
        passwd=self.loginData["passwd"],
        port=self.loginData["port"]
      ))
    except:
      Msg.error(statusNS["disconnected_title"])
      self.setStatusDisconnected()
    pass


  #------------- Run -------------#


  def run(self):
    self.clear()
    Msg.welcome()
    while True:
      try:
        inputPrompt = getInputPrompt(self.env)
        action = input(inputPrompt)
        self.action = processAction(action)
        if Av.isExit(self.action):
          self.exit()
          break
        elif Av.isClear(self.action):
          self.clear()
        elif Av.isHelp(self.action):
          self.help()
        elif Av.isRush(self.action):
          self.rush()
        elif Av.isLs(self.action):
          self.ls()
        elif Av.isJump(self.action):
          self.jump()
        elif Av.isWhereAmI(self.action):
          self.whereAmI()
        elif Av.isWhoAmI(self.action):
          self.whoAmI()
        elif Av.isCd(self.action):
          self.cd()
        elif Av.isMkdir(self.action):
          self.mkdir()
        elif Av.isDelete(self.action):
          self.delete()
        elif Av.isDrop(self.action):
          self.drop()
        elif Av.isTake(self.action):
          self.take()
        elif Av.isStatus(self.action):
          self.status()
        else:
          Msg.info(commonNS["command_not_found"])
      except:
        Msg.error(commonNS["unexpected_error"])
        break
    pass