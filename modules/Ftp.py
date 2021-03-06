import os
from ftpretty import ftpretty as FTP
from utils.getNextPath import getNextPath
from utils.getTimestamp import getTimestamp

# Name: Ftp
# Desc: Provide additional features for ftp.
#       Expand capabilities of inherited module
# Inherits: ftpretty
# Methods: 
#   - exists (check if file exists)
#   - isDir (check if file is a directory)
#   - isFile (check if file is a file)
#   - isBrokenSymlink (check if file is a broken symlink)
#   - rmTree (delete file tree)
#   - putFile (upload single file to the server)
#   - getFile (download single file from the server)
#   - putTree (upload file tree to the server)
#   - getTree (download file tree from the server)

class Ftp(FTP):

  # Name: exists
  # Desc: Check if file exists
  # Args: target (string), currentPath (string)
  # Return: boolean

  def exists(self, target, currentPath):
    curDirList = self.list(currentPath, extra=True)
    for el in curDirList:
      if el["name"] == target:
        return True
    return False
    
  # ----------------------------------------------------

  # Name: isDir
  # Desc: Check if file is a directory
  # Args: target (string)
  # Return: boolean

  def isDir(self, target):
    path, targetName = os.path.split(target)
    curDirList = self.list(path, extra=True)
    for el in curDirList:
      if el["name"] == targetName and el["directory"] == "d":
        return True
    return False

  # ----------------------------------------------------

  # Name: isFile
  # Desc: Check if file is a file
  # Args: target (string)
  # Return: boolean

  def isFile(self, target):
    path, targetName = os.path.split(target)
    curDirList = self.list(path, extra=True)
    for el in curDirList:
      if el["name"] == targetName and el["directory"] != "d":
        return True
    return False

  # ----------------------------------------------------

  # Name: isBrokenSymlink
  # Desc: Check if file is a broken symlink
  # Args: path (string)
  # Return: boolean

  def isBrokenSymlink(self, path):
    if os.path.islink(path):
      targetPath = os.readlink(path)
      if not os.path.isabs(targetPath):
        targetPath = os.path.join(os.path.dirname(path), targetPath)             
      if not os.path.exists(targetPath):
        return True
    return False

  # ----------------------------------------------------

  # Name: rmTree
  # Desc: Delete file tree
  # Args: path (string)
  # Return: void

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

  # Name: putFile
  # Desc: Upload single file to the server
  # Args: targetPath (string),
  #       exists (boolean=False),
  #       overwrite (boolean=True)
  # Return: void

  def putFile(self, targetPath, exists=False, overwrite=True):
    _, fileName = os.path.split(targetPath)
    fileNameToUpload = fileName
    if not overwrite and exists:
      timestamp = getTimestamp()
      fileNameToUpload = "{time}_{file}".format(time=timestamp, file=fileName)
    self.put(targetPath, fileNameToUpload)

  # ----------------------------------------------------

  # Name: getFile
  # Desc: Download single file from the server
  # Args: targetPath (string),
  #       exists (boolean=False),
  #       overwrite (boolean=True)
  # Return: void

  def getFile(self, targetPath, saveToPath, exists=False, overwrite=True):
    _, fileName = os.path.split(targetPath)
    fileNameToCreate = fileName
    if not overwrite and exists:
      timestamp = getTimestamp()
      fileNameToCreate = "{time}_{file}".format(time=timestamp, file=fileName)
    localFileName = getNextPath(saveToPath, fileNameToCreate)
    self.get(targetPath, localFileName)

  # ----------------------------------------------------

  # Name: putTree
  # Desc: Upload file tree to the server
  # Args: targetPath (string),
  #       exists (boolean=False),
  #       overwrite (boolean=True)
  # Return: void

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

  # Name: getTree
  # Desc: Download file tree from the server
  # Args: targetPath (string),
  #       exists (boolean=False),
  #       overwrite (boolean=True)
  # Return: void

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