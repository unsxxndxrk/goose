import os
import shutil
from pathlib import Path

from modules.ActionVerifier import ActionVerifier
from modules.Message import Message
from modules.Ftp import Ftp
from modules.Interact import Interact
from modules.Namespace import Namespace

from constants.settings import settings
from constants.environments import environments as envs
from constants.actions import Actions as Act

from utils.execCmd import execCmd
from utils.getNextPath import getNextPath
from utils.trimSpaces import trimSpaces
from utils.getSingleActionParam import getSingleActionParam
from utils.getTimestamp import getTimestamp
from utils.getInputPrompt import getInputPrompt

av = ActionVerifier()
msg = Message()
interact = Interact()
ns = Namespace()

class App:
  def __init__(self):
    self.ftp = None
    self.connected = False
    self.loginData = {}
    self.action = ""
    self.env = envs["Local"]
    self.pathLocal = str(Path.home())
    self.pathRemote = ""


  def processAction(self, action):
    return trimSpaces(action)


  def pingServer(self, message=True):
    try:
      self.ftp.voidcmd("NOOP")
    except:
      if message:
        msg.error(ns.common["connection_lost"])
      self.setStatusDisconnected()


  def setStatusDisconnected(self):
    self.ftp = None
    self.connected = False
    self.env = envs["Local"]
    self.pathRemote = ""


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
      msg.serverResponse(self.ftp.getwelcome())
      return True
    except Exception as e:
      self.setStatusDisconnected()
      msg.serverResponse(e)
      return False


  def changeLocalPath(self, nextPath):
    os.chdir(nextPath)
    self.pathLocal = nextPath

  
  def changeRemotePath(self, nextPath):
    self.ftp.cwd(nextPath)
    self.pathRemote = nextPath 
  

  def rmFtpTree(self, path):
    pathList = self.ftp.list(path, extra=True)
    for target in pathList:
      preparedTargetPath = getNextPath(path, target["name"])
      if target["directory"] == "d":
        self.rmFtpTree(preparedTargetPath)
      else:
        self.ftp.delete(preparedTargetPath)
    self.ftp.rmd(path)

  
  def deleteLocal(self, target):
    _, targetName = os.path.split(target)
    suspendText = ns.delete["deleting"].format(target=targetName)
    successText = ns.delete["success"]
    localTargetPath = getNextPath(self.pathLocal, target)
    msg.suspend(ns.common["processing"])
    if os.path.isfile(localTargetPath):
      confirmMsg = ns.delete["delete_file"].format(fileName=targetName)
      confirmDelFile = interact.confirm(confirmMsg)
      if confirmDelFile:
        msg.suspend(suspendText)
        os.remove(localTargetPath)
        msg.success(successText)
    elif os.path.isdir(localTargetPath):
      confirmMsg = ns.delete["delete_dir"].format(dirName=targetName)
      confirmDelDir = interact.confirm(confirmMsg)
      if confirmDelDir:
        msg.suspend(suspendText)
        shutil.rmtree(localTargetPath)
        msg.success(successText)
    else:
      raise


  def deleteRemote(self, target):
    _, targetName = os.path.split(target)
    suspendText = ns.delete["deleting"].format(target=targetName)
    successText = ns.delete["success"]
    remoteTargetPath = getNextPath(self.pathRemote, target)
    if self.ftp.isDir(remoteTargetPath):
      confirmMsg = ns.delete["delete_dir"].format(dirName=targetName)
      confirmDelDir = interact.confirm(confirmMsg)
      if confirmDelDir:
        msg.suspend(suspendText)
        self.rmFtpTree(remoteTargetPath)
        msg.success(successText)
    elif self.ftp.isFile(remoteTargetPath):
      confirmMsg = ns.delete["delete_file"].format(fileName=targetName)
      confirmDelFile = interact.confirm(confirmMsg)
      if confirmDelFile:
        msg.suspend(suspendText)
        self.ftp.delete(remoteTargetPath)
        msg.success(successText)
    else:
      raise


  def uploadFile(self, targetPath, pathExists, override):
    _, fileName = os.path.split(targetPath)
    fileNameToUpload = fileName
    if not override and pathExists:
      timestamp = getTimestamp()
      fileNameToUpload = "{time}_{file}".format(time=timestamp, file=fileName)
    self.ftp.put(targetPath, fileNameToUpload)


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


  def downloadFile(self, targetPath, pathExists, override):
    _, fileName = os.path.split(targetPath)
    fileNameToCreate = fileName
    if not override and pathExists:
      timestamp = getTimestamp()
      fileNameToCreate = "{time}_{file}".format(time=timestamp, file=fileName)
    localFileName = getNextPath(self.pathLocal, fileNameToCreate)
    self.ftp.get(targetPath, localFileName)


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


  def cd(self):
    dest = getSingleActionParam(Act["Cd"], self.action)
    if self.env == envs["Local"]:
      nextLocalPath = getNextPath(self.pathLocal, dest)
      if os.path.exists(nextLocalPath):
        self.changeLocalPath(nextLocalPath)  
      else:
        msg.error(ns.cd["error"].format(dest=nextLocalPath))
    else:
      self.pingServer()
      if self.connected:
        try:
          nextRemotePath = getNextPath(self.pathRemote, dest)
          self.changeRemotePath(nextRemotePath)
        except:
          msg.error(ns.cd["error"].format(dest=nextRemotePath))


  def clear(self):
    clearResult = execCmd("clear")
    if clearResult:
      print(clearResult)
    else:
      msg.error(ns.clear["error"])


  def delete(self):
    target = getSingleActionParam(Act["Delete"], self.action)
    msg.suspend(ns.common["processing"])
    try:
      if self.env == envs["Local"]:
        self.deleteLocal(target)
      else:
        self.pingServer()
        if self.connected:
          self.deleteRemote(target)
    except:
      msg.error(ns.delete["error"].format(target=target))   


  def put(self):
    self.pingServer(message=False)
    if self.connected:
      msg.suspend(ns.common["processing"])
      override = False
      pathExists = False
      target = getSingleActionParam(Act["Put"], self.action)
      targetPath = getNextPath(self.pathLocal, target)
      _, targetName = os.path.split(target)
      if os.path.exists(targetPath):
        if self.ftp.exists(targetName, self.pathRemote):
          pathExists = True
          existsMsg = ns.put["exists"].format(target=targetName)
          confirmOverride = interact.confirm(existsMsg)
          if confirmOverride:
            override = True
        try:
          msg.suspend(ns.put["progress"])
          if os.path.isfile(targetPath):
            self.uploadFile(targetPath, pathExists, override)
          elif os.path.isdir(targetPath):
            currentRemotePath = self.pathRemote
            self.uploadTree(targetPath, pathExists, override)
            self.changeRemotePath(currentRemotePath)
          else:
            raise Exception("Unable to define local path")
          msg.success(ns.put["success"])
        except:
          msg.error(ns.put["transfer_error"])
      else:
        msg.error(ns.put["invalid_path"])
    else:
      msg.error(ns.put["not_connected"])


  def exit(self):
    self.pingServer(message=False)
    if self.connected and self.ftp:
      self.ftp.quit()


  def help(self):
    msg.help()


  def jump(self):
    jumpTo = getSingleActionParam(Act["Jump"], self.action)
    if jumpTo == envs["Local"]:
      self.env = envs["Local"]
    else:
      self.pingServer(message=False)
      if self.connected:
        self.env = envs["Remote"]
      else:
        msg.error(ns.jump["not_connected"])


  def ls(self):
    if self.env == envs["Remote"]:
      self.pingServer()
      if self.connected:
        try:
          self.ftp.retrlines("LIST")
        except:
          msg.error(ns.ls["error"])
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
        msg.error(ns.ls["error"])


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
      msg.error(ns.mkdir["error"].format(dirName=dirName))


  def rush(self):
    hostStr = getSingleActionParam(Act["Rush"], self.action)
    loginStr = ns.rush["login"]["user"]
    passwdStr = ns.rush["login"]["passwd"]
    portSrt = ns.rush["login"]["port"]
    userInput = interact.multiInput([loginStr, passwdStr, portSrt])
    self.loginData = {
      "host": hostStr,
      "user": userInput[loginStr],
      "passwd": userInput[passwdStr],
      "port": userInput[portSrt] or settings["port"]
    }
    msg.suspend(ns.rush["connecting"].format(host=self.loginData["host"]))
    if self.login():
      msg.success(ns.rush["connected"].format(host=self.loginData["host"]))
    else:
      msg.error(ns.rush["connecting_error"].format(host=self.loginData["host"]))


  def take(self):
    self.pingServer(message=False)
    if self.connected:
      msg.suspend(ns.common["processing"])
      override = False
      pathExists = False
      target = getSingleActionParam(Act["Take"], self.action)
      targetPath = getNextPath(self.pathRemote, target)
      _, targetName = os.path.split(targetPath)
      localTargetPath = getNextPath(self.pathLocal, targetName)
      if os.path.exists(localTargetPath):
        pathExists = True
        confirmOverride = interact.confirm(ns.take["exists"].format(target=targetName))
        if confirmOverride:
          override = True
      try:
        msg.suspend(ns.take["progress"])
        if self.ftp.isDir(targetPath):
          currentLocalPath = self.pathLocal
          self.downloadTree(targetPath, pathExists, override)
          self.changeLocalPath(currentLocalPath)
        else:
          self.downloadFile(targetPath, pathExists, override)
        msg.success(ns.take["success"])
      except:
        msg.error(ns.take["transfer_error"])
    else:
      msg.error(ns.take["not_connected"])


  def whereAmI(self):
    if self.env == envs["Local"]:
      print(self.pathLocal)
    else:
      self.pingServer()
      if self.connected:
        print(self.pathRemote)


  def whoAmI(self):
    if self.env == envs["Local"]:
      print(execCmd("whoami"))
    else:
      self.pingServer()
      if self.connected:
        print(self.loginData["user"])


  def status(self):
    try:
      self.ftp.voidcmd("NOOP")
      msg.serverResponse(self.ftp.getwelcome())
      msg.success(ns.status["connected_title"])
      msg.default(ns.status["connected_data"].format(
        host=self.loginData["host"],
        user=self.loginData["user"],
        passwd=self.loginData["passwd"],
        port=self.loginData["port"]
      ))
    except:
      msg.error(ns.status["disconnected_title"])
      self.setStatusDisconnected()


  def run(self):
    self.clear()
    msg.welcome()
    while True:
      try:
        inputPrompt = getInputPrompt(self.env)
        action = input(inputPrompt)
        self.action = self.processAction(action)
        if av.isExit(self.action):
          self.exit()
          break
        elif av.isClear(self.action):
          self.clear()
        elif av.isHelp(self.action):
          self.help()
        elif av.isRush(self.action):
          self.rush()
        elif av.isLs(self.action):
          self.ls()
        elif av.isJump(self.action):
          self.jump()
        elif av.isWhereAmI(self.action):
          self.whereAmI()
        elif av.isWhoAmI(self.action):
          self.whoAmI()
        elif av.isCd(self.action):
          self.cd()
        elif av.isMkdir(self.action):
          self.mkdir()
        elif av.isDelete(self.action):
          self.delete()
        elif av.isPut(self.action):
          self.put()
        elif av.isTake(self.action):
          self.take()
        elif av.isStatus(self.action):
          self.status()
        else:
          msg.info(ns.common["command_not_found"])
      except:
        msg.error(ns.common["unexpected_error"])
        break
