from utils.trimSpaces import trimSpaces

# Ім'я: getSingleActionParam
# Опис: Отримати параметр із команди з єдиним параметром
# Аргументи: actionName (string<Key of actions>), action (string)
# Повертаєме значення: string

def getSingleActionParam(actionName, userInput):
  actNameLen = len(actionName)
  result = userInput[actNameLen:]
  return trimSpaces(result)

# ----------------------------------------------------