import os
from ftpretty import ftpretty as FTP
from utils.getNextPath import getNextPath
from utils.getTimestamp import getTimestamp

# Ім'я: Ftp
# Опис: Надає додаткові функції для FTP.
#       Розширює функціонал успадкованого модулю
# Успадковує: ftpretty
# Методи: 
#   - exists (перевірка чи файл існує)
#   - isDir (перевірка на директорію)
#   - isFile (перевірка на файл)
#   - isBrokenSymlink (перевірка на невалідне символьне посилання)
#   - rmTree (видаляє деверо файлів)
#   - putFile (завантажує один файл на сервер)
#   - getFile (завантажує один файл з серверу)
#   - putTree (завантажує дерево файлів на серве)
#   - getTree (завантажує дерево файлів з серверу)

class Ftp(FTP):

  # Ім'я: exists
  # Опис: Перевірка чи файл існує
  # Аргументи: target (string), currentPath (string)
  # Повертаєме значення: boolean

  def exists(self, target, currentPath):
    curDirList = self.list(currentPath, extra=True)
    for el in curDirList:
      if el["name"] == target:
        return True
    return False
    
  # ----------------------------------------------------

  # Ім'я: isDir
  # Опис: Перевірка на директорію
  # Аргументи: target (string)
  # Повертаєме значення: boolean

  def isDir(self, target):
    path, targetName = os.path.split(target)
    curDirList = self.list(path, extra=True)
    for el in curDirList:
      if el["name"] == targetName and el["directory"] == "d":
        return True
    return False

  # ----------------------------------------------------

  # Ім'я: isFile
  # Опис: Перевірка на файл
  # Аргументи: target (string)
  # Повертаєме значення: boolean

  def isFile(self, target):
    path, targetName = os.path.split(target)
    curDirList = self.list(path, extra=True)
    for el in curDirList:
      if el["name"] == targetName and el["directory"] != "d":
        return True
    return False

  # ----------------------------------------------------

  # Ім'я: isBrokenSymlink
  # Опис: Перевірка на невалідне символьне посилання
  # Аргументи: path (string)
  # Повертаєме значення: boolean

  def isBrokenSymlink(self, path):
    if os.path.islink(path):
      targetPath = os.readlink(path)
      if not os.path.isabs(targetPath):
        targetPath = os.path.join(os.path.dirname(path), targetPath)             
      if not os.path.exists(targetPath):
        return True
    return False

  # ----------------------------------------------------

  # Ім'я: rmTree
  # Опис: Видалити дерево файлів
  # Аргументи: path (string)
  # Повертаєме значення: void

  def rmTree(self, path):
    pathList = self.list(path, extra=True)
    for target in pathList:
      preparedTargetPath = getNextPath(path, target["name"])
      if target["directory"] == "d":
        self.rmTree(preparedTargetPath)
      else:
        self.delete(preparedTargetPath)
    self.rmd(path)

  # ----------------------------------------------------

  # Ім'я: putFile
  # Опис: Завантажити один файл на сервер
  # Аргументи: targetPath (string),
  #       exists (boolean=False),
  #       overwrite (boolean=True)
  # Повертаєме значення: void

  def putFile(self, targetPath, exists=False, overwrite=True):
    _, fileName = os.path.split(targetPath)
    fileNameToUpload = fileName
    if not overwrite and exists:
      timestamp = getTimestamp()
      fileNameToUpload = "{time}_{file}".format(time=timestamp, file=fileName)
    self.put(targetPath, fileNameToUpload)

  # ----------------------------------------------------

  # Ім'я: getFile
  # Опис: Завантажити один файл з серверу
  # Аргументи: targetPath (string),
  #       exists (boolean=False),
  #       overwrite (boolean=True)
  # Повертаєме значення: void

  def getFile(self, targetPath, saveToPath, exists=False, overwrite=True):
    _, fileName = os.path.split(targetPath)
    fileNameToCreate = fileName
    if not overwrite and exists:
      timestamp = getTimestamp()
      fileNameToCreate = "{time}_{file}".format(time=timestamp, file=fileName)
    localFileName = getNextPath(saveToPath, fileNameToCreate)
    self.get(targetPath, localFileName)

  # ----------------------------------------------------

  # Ім'я: putTree
  # Опис: Завантаження на сервер
  # Аргументи: targetPath (string),
  #       exists (boolean=False),
  #       overwrite (boolean=True)
  # Повертаєме значення: void

  def putTree(self, targetPath, exists=False, overwrite=True):
    _, dirName = os.path.split(targetPath)
    dirNameToCreate = dirName
    if not overwrite and exists:
      timestamp = getTimestamp()
      dirNameToCreate = "{time}_{dir}".format(time=timestamp, dir=dirName)
    remoteDirPath = getNextPath(self.pwd(), dirNameToCreate)
    if not exists or (exists and not overwrite):
      self.mkd(remoteDirPath)
    self.cwd(remoteDirPath)
    for el in os.listdir(targetPath):
      elPath = getNextPath(targetPath, el)
      remoteElPath = getNextPath(self.pwd(), el)
      if os.path.isdir(elPath):
        if not self.isBrokenSymlink(elPath):
          innerExists = False
          if self.exists(el, self.pwd()):
            innerExists = True
          self.putTree(elPath, innerExists)
      if self.isBrokenSymlink(elPath):
        continue
      if os.path.isfile(elPath):
        self.put(elPath, el)
    backPath = getNextPath(self.pwd(), "..")
    self.cwd(backPath)

  # ----------------------------------------------------

  # Ім'я: getTree
  # Опис: Завантаження з серверу
  # Аргументи: targetPath (string),
  #       exists (boolean=False),
  #       overwrite (boolean=True)
  # Повертаєме значення: void

  def getTree(self, targetPath, exists=False, overwrite=True):
    _, dirName = os.path.split(targetPath)
    dirNameToCreate = dirName
    if not overwrite and exists:
      timestamp = getTimestamp()
      dirNameToCreate = "{time}_{dir}".format(time=timestamp, dir=dirName)
    localDirPath = getNextPath(os.getcwd(), dirNameToCreate)
    if not exists or (exists and not overwrite):
      os.mkdir(localDirPath)
    os.chdir(localDirPath)
    targetList = self.list(targetPath, extra=True)
    for el in targetList:
      elPath = getNextPath(targetPath, el["name"])
      localElPath = getNextPath(os.getcwd(), el["name"])
      if el["directory"] == "d":
        innerExists = False
        if os.path.exists(localElPath):
          innerExists = True
        self.getTree(elPath, innerExists)
      else:
        localFileName = getNextPath(os.getcwd(), el["name"])
        self.get(elPath, localFileName)  
    backPath = getNextPath(os.getcwd(), "..")
    os.chdir(backPath)

  # ----------------------------------------------------