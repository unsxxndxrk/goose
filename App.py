import os
import shutil
from pathlib import Path

from modules.ActionVerifier import ActionVerifier
from modules.Message import Message
from modules.Ftp import Ftp
from modules.Interact import Interact
from modules.Namespace import Namespace
from modules.Spinner import Spinner

from constants.settings import settings
from constants.environments import environments as envs
from constants.actions import actions as act

from utils.execCmd import execCmd
from utils.getNextPath import getNextPath
from utils.trimSpaces import trimSpaces
from utils.getSingleActionParam import getSingleActionParam
from utils.getInputPrompt import getInputPrompt

av = ActionVerifier()
msg = Message()
interact = Interact()
ns = Namespace()
spinner = Spinner()

class App:
  def __init__(self):
    self.ftp = None
    self.connected = False
    self.loginData = {}
    self.action = ""
    self.env = envs["Local"]
    self.pathLocal = str(Path.home())
    self.pathRemote = ""


  # # # # # # # # # # # # # # # # # #
  #                                 #
  #        Функції-помічники        #
  #                                 # 
  # # # # # # # # # # # # # # # # # #


  # Ім'я: processAction
  # Опис: Первинна обробка введеної команди
  # Аргументи: action (string)
  # Повертаєме значення: Рядок з одиничним набором пробілів

  def processAction(self, action):
    return trimSpaces(action)

  # ----------------------------------------------------

  # Ім'я: pingServer
  # Опис: Перевірка з'єднання з сервером
  # Аргументи: message (boolean)
  # Повертаєме значення: void

  def pingServer(self, message=True):
    try:
      self.ftp.voidcmd("NOOP")
    except:
      if message:
        msg.error(ns.errors["no_connection"])
      self.setStatusDisconnected()

  # ----------------------------------------------------

  # Ім'я: setStatusDisconnected
  # Опис: Встановлення статусу "без з'єднання"
  # Аргументи: void
  # Повертаєме значення: void

  def setStatusDisconnected(self):
    self.ftp = None
    self.connected = False
    self.env = envs["Local"]
    self.pathRemote = ""

  # ----------------------------------------------------

  # Ім'я: login
  # Опис: Встановлення з'єднання з сервером
  # Аргументи: void
  # Повертаєме значення: boolean

  def login(self):
    loginData = self.loginData
    try:
      self.ftp = Ftp(
        loginData["host"],
        loginData["user"],
        loginData["passwd"],
        port=loginData["port"],
        timeout=settings["ftp"]["timeout"]
      )
      self.ftp.login(user=loginData["user"], passwd=loginData["passwd"])
      self.connected = True
      self.env = envs["Remote"]
      self.pathRemote = self.ftp.pwd()
      return True
    except Exception as e:
      raise e

  # ----------------------------------------------------

  # Ім'я: changeLocalPath
  # Опис: Зміна шляху локальної файлової системи
  # Аргументи: nextPath (string)
  # Повертаєме значення: void

  def changeLocalPath(self, nextPath):
    os.chdir(nextPath)
    self.pathLocal = nextPath

  # ----------------------------------------------------

  # Ім'я: changeRemotePath
  # Опис: Зміна шляху віддаленої файлової системи
  # Аргументи: nextPath (string)
  # Повертаєме значення: void

  def changeRemotePath(self, nextPath):
    self.ftp.cwd(nextPath)
    self.pathRemote = nextPath 

  # ----------------------------------------------------

  
  # # # # # # # # # # # # #
  #                       #
  #        Команди        #
  #                       #
  # # # # # # # # # # # # #


  # Ім'я: connect
  # Опис: З'єднання з FTP-сервером
  # Аргументи: void
  # Повертаєме значення: void

  def connect(self):
    hostStr = getSingleActionParam(act["Connect"], self.action)
    loginStr = ns.common["login"]["user"]
    passwdStr = ns.common["login"]["passwd"]
    portSrt = ns.common["login"]["port"]
    userInput = interact.multiInput([loginStr, passwdStr, portSrt])
    self.loginData = {
      "host": hostStr,
      "user": userInput[loginStr],
      "passwd": userInput[passwdStr],
      "port": userInput[portSrt] or settings["ftp"]["port"]
    }
    connectingMsg = ns.common["connecting"].format(host=self.loginData["host"])
    connectedMsg = ns.common["connected"].format(host=self.loginData["host"])
    errorMsg = ns.errors["connecting_error"].format(host=self.loginData["host"])
    spinner.start(connectingMsg)
    try:
      isConnected = self.login()
      if isConnected:
        spinner.success(connectingMsg)
        msg.default(self.ftp.getwelcome())
        msg.success(connectedMsg)
    except Exception as e:
      spinner.fail(connectingMsg)
      self.setStatusDisconnected()
      msg.default(e)
      msg.error(errorMsg)

  # ----------------------------------------------------

  # Ім'я: upload
  # Опис: Завантаження даних на сервер
  # Аргументи: void
  # Повертаєме значення: void

  def upload(self):
    self.pingServer(message=False)
    if self.connected:
      overwrite = False
      pathExists = False
      target = getSingleActionParam(act["Upload"], self.action)
      targetPath = getNextPath(self.pathLocal, target)
      _, targetName = os.path.split(targetPath)
      if os.path.exists(targetPath):
        if self.ftp.exists(targetName, self.pathRemote):
          pathExists = True
          existsMsg = ns.interact["data_exists"].format(target=targetName)
          confirmOverwrite = interact.confirm(existsMsg)
          if confirmOverwrite:
            overwrite = True
        uploadingMsg = ns.common["uploading"].format(target=targetPath)
        try:
          spinner.start(uploadingMsg)
          if os.path.isdir(targetPath):
            self.ftp.putTree(targetPath, pathExists, overwrite)
          else:
            self.ftp.putFile(targetPath, pathExists, overwrite)
          spinner.success(uploadingMsg)
          msg.success(ns.common["success"])
        except Exception as e:
          spinner.fail(uploadingMsg)
          msg.default(e)
          msg.error(ns.errors["transfer_error"])
      else:
        msg.error(ns.errors["invalid_path"])
    else:
      msg.error(ns.errors["no_connection"])

  # ----------------------------------------------------

  # Ім'я: download
  # Опис: Завантаження даних з серверу
  # Аргументи: void
  # Повертаєме значення: void

  def download(self):
    self.pingServer(message=False)
    if self.connected:
      overwrite = False
      pathExists = False
      target = getSingleActionParam(act["Download"], self.action)
      targetPath = getNextPath(self.pathRemote, target)
      absTargetPath, targetName = os.path.split(targetPath)
      localTargetPath = getNextPath(self.pathLocal, targetName)
      if self.ftp.exists(targetName, absTargetPath):
        if os.path.exists(localTargetPath):
          pathExists = True
          confirmOverwrite = interact.confirm(ns.interact["data_exists"].format(target=targetName))
          if confirmOverwrite:
            overwrite = True
        downloadingMsg = ns.common["downloading"].format(target=targetPath)
        try:
          spinner.start(downloadingMsg)
          if self.ftp.isDir(targetPath):
            self.ftp.getTree(targetPath, pathExists, overwrite)
          else:
            self.ftp.getFile(targetPath, self.pathLocal, pathExists, overwrite)
          spinner.success(downloadingMsg)
          msg.success(ns.common["success"])
        except Exception as e:
          spinner.fail(downloadingMsg)
          msg.default(e)
          msg.error(ns.errors["transfer_error"])
      else:
        msg.error(ns.errors["invalid_path"])
    else:
      msg.error(ns.errors["no_connection"])

  # ----------------------------------------------------

  # Ім'я: delete
  # Опис: Видалення файлів/директорій
  # Аргументи: void
  # Повертаєме значення: void

  def delete(self):
    target = getSingleActionParam(act["Delete"], self.action)
    try:
      if self.env == envs["Local"]:
        localTargetPath = getNextPath(self.pathLocal, target)  
        if os.path.exists(localTargetPath):
          deletingMsg = ns.common["deleting"].format(target=localTargetPath)  
          confirmMsg = ns.interact["confirm_delete"].format(fileName=localTargetPath)
          confirmDel = interact.confirm(confirmMsg)  
          if confirmDel:
            spinner.start(deletingMsg)
            if os.path.isdir(localTargetPath):
              shutil.rmtree(localTargetPath)
            else:
              os.remove(localTargetPath)
            spinner.success(deletingMsg)
            msg.success(ns.common["success"])
        else:
          msg.error(ns.errors["invalid_path"])
      else:
        self.pingServer()
        if self.connected:
          remoteTargetPath = getNextPath(self.pathRemote, target)
          absTargetPath, absTargetName = os.path.split(remoteTargetPath)
          if self.ftp.exists(absTargetName, absTargetPath):
            deletingMsg = ns.common["deleting"].format(target=remoteTargetPath)  
            confirmMsg = ns.interact["confirm_delete"].format(fileName=remoteTargetPath)
            confirmDel = interact.confirm(confirmMsg)  
            if confirmDel:
              spinner.start(deletingMsg)
              if self.ftp.isDir(remoteTargetPath):
                self.ftp.rmTree(remoteTargetPath)
              else:
                self.ftp.delete(remoteTargetPath)
              spinner.success(deletingMsg)
              msg.success(ns.common["success"])
          else:
            msg.error(ns.errors["invalid_path"])
    except Exception as e:
      spinner.fail(deletingMsg)
      msg.default(e)
      msg.error(ns.errors["delete_error"].format(target=target)) 

  # ----------------------------------------------------

  # Ім'я: mkdir
  # Опис: Створення директорій
  # Аргументи: void
  # Повертаєме значення: void

  def mkdir(self):
    dirName = getSingleActionParam(act["Mkdir"], self.action)
    try:
      if self.env == envs["Local"]:
        localDirPath = getNextPath(self.pathLocal, dirName)
        os.mkdir(localDirPath)
      else:
        self.pingServer()
        if self.connected:
          remoteDirPath = getNextPath(self.pathRemote, dirName)
          self.ftp.mkd(remoteDirPath)
    except Exception as e:
      msg.default(e)
      msg.error(ns.errors["mkdir_error"].format(dirName=dirName))

  # ----------------------------------------------------

  # Ім'я: changeEnv
  # Опис: Зміна поточного оточення
  # Аргументи: void
  # Повертаєме значення: void

  def changeEnv(self):
    changeTo = getSingleActionParam(act["ChangeEnv"], self.action)
    if changeTo == envs["Local"]:
      self.env = envs["Local"]
    else:
      self.pingServer()
      if self.connected:
        self.env = envs["Remote"]
      
  # ----------------------------------------------------

  # Ім'я: cd
  # Опис: Зміна поточного шляху файлової системи
  # Аргументи: void
  # Повертаєме значення: void

  def cd(self):
    dest = getSingleActionParam(act["Cd"], self.action)
    if self.env == envs["Local"]:
      nextLocalPath = getNextPath(self.pathLocal, dest)
      if os.path.exists(nextLocalPath):
        self.changeLocalPath(nextLocalPath)  
      else:
        msg.error(ns.errors["cd_error"].format(dest=nextLocalPath))
    else:
      self.pingServer()
      if self.connected:
        try:
          nextRemotePath = getNextPath(self.pathRemote, dest)
          self.changeRemotePath(nextRemotePath)
        except Exception as e:
          msg.default(e)
          msg.error(ns.errors["cd_error"].format(dest=nextRemotePath))

  # ----------------------------------------------------

  # Ім'я: ls
  # Опис: Друк списку файлів в поточному шляху файлової системи
  # Аргументи: void
  # Повертаєме значення: void

  def ls(self):
    if self.env == envs["Remote"]:
      self.pingServer()
      if self.connected:
        try:
          self.ftp.retrlines("LIST")
        except Exception as e:
          msg.default(e)
          msg.error(ns.errors["terminal_command_error"].format(command="ls"))
    else:
      try:
        if os.path.exists(self.pathLocal):
          os.chdir(self.pathLocal)
          cmd = "ls -l"
          output = execCmd(cmd)
          print(output)
        else:
          raise
      except Exception as e:
        msg.default(e)
        msg.error(ns.errors["terminal_command_error"].format(command="ls"))

  # ----------------------------------------------------

  # Ім'я: status
  # Опис: Друк статусу з'єднання
  # Аргументи: void
  # Повертаєме значення: void

  def status(self):
    try:
      self.ftp.voidcmd("NOOP")
      msg.default(self.ftp.getwelcome())
      msg.success(ns.common["status"]["connected"])
      msg.default(ns.common["status"]["connected_data"].format(
        host=self.loginData["host"],
        user=self.loginData["user"],
        passwd=self.loginData["passwd"],
        port=self.loginData["port"]
      ))
    except:
      msg.error(ns.common["status"]["disconnected"])
      self.setStatusDisconnected()

  # ----------------------------------------------------

  # Ім'я: clear
  # Опис: Очистка терміналу
  # Аргументи: void
  # Повертаєме значення: void

  def clear(self):
    clearResult = execCmd("clear")
    if clearResult:
      print(clearResult)
    else:
      msg.error(ns.errors["terminal_command_error"].format(command="clear"))

  # ----------------------------------------------------

  # Ім'я: whereAmI
  # Опис: Друк поточного шляху файлової системи
  # Аргументи: void
  # Повертаєме значення: void

  def whereAmI(self):
    if self.env == envs["Local"]:
      msg.default(self.pathLocal)
    else:
      self.pingServer()
      if self.connected:
        msg.default(self.pathRemote)

  # ----------------------------------------------------

  # Ім'я: whoAmI
  # Опис: Друк поточного імені користувача
  # Аргументи: void
  # Повертаєме значення: void

  def whoAmI(self):
    if self.env == envs["Local"]:
      msg.default(execCmd("whoami"))
    else:
      self.pingServer()
      if self.connected:
        msg.default(self.loginData["user"])

  # ----------------------------------------------------

  # Ім'я: exit
  # Опис: Завершення роботи
  # Аргументи: void
  # Повертаєме значення: void

  def exit(self):
    self.pingServer(message=False)
    if self.connected and self.ftp:
      self.ftp.quit()

  # ----------------------------------------------------

  # Ім'я: help
  # Опис: Друк довідки
  # Аргументи: void
  # Повертаєме значення: void

  def help(self):
    msg.help()

  # ----------------------------------------------------

  # Ім'я: run
  # Опис: Запуск програми
  # Аргументи: void
  # Повертаєме значення: void

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
        elif av.isConnect(self.action):
          self.connect()
        elif av.isLs(self.action):
          self.ls()
        elif av.isChangeEnv(self.action):
          self.changeEnv()
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
        elif av.isUpload(self.action):
          self.upload()
        elif av.isDownload(self.action):
          self.download()
        elif av.isStatus(self.action):
          self.status()
        else:
          msg.info(ns.common["command_not_found"])
      except:
        msg.error(ns.errors["unexpected_error"])
        break
  
  # ----------------------------------------------------
