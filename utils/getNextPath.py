import os

# Ім'я: getNextPath
# Опис: Створення абсолютного шляху файлової системи
# Аргументи: curPath (string), dest (string), trailingSlash (boolean)
# Повертаєме значення: string

def getNextPath(curPath, dest, trailingSlash=False):
  slash = "/" if trailingSlash else ""
  path = os.path
  return path.abspath(path.join(curPath, dest)) + slash

# ----------------------------------------------------