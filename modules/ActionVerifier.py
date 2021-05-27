from constants.actions import actions as act
from constants.environments import environments as envs

# Ім'я: ActionVerifier
# Опис: Надає можливість перевіряти введену команду на збіг із командами програми
# Методи: 
#   - __splitAction (розбиває рядок за розділювачем "пробіл")
#   - isCd (перевіряє на збіг із командою Cd)
#   - isClear (перевіряє на збіг із командою Clear)
#   - isDelete (перевіряє на збіг із командою Delete)
#   - isUpload (перевіряє на збіг із командою Upload)
#   - isExit (перевіряє на збіг із командою Exit)
#   - isHelp (перевіряє на збіг із командою Help)
#   - isChangeEnv (перевіряє на збіг із командою ChangeEnv)
#   - isLs (перевіряє на збіг із командою Ls)
#   - isMkdir (перевіряє на збіг із командою Mkdir)
#   - isConnect (перевіряє на збіг із командою Connect)
#   - isStatus (перевіряє на збіг із командою Status)
#   - isDownload (перевіряє на збіг із командою Download)
#   - isWhereAmI (перевіряє на збіг із командою WhereAmI)
#   - isWhoAmI (перевіряє на збіг із командою WhoAmI)

class ActionVerifier:

  # Ім'я: __splitAction
  # Опис: Розбиває рядок за розділювачем "пробіл"
  # Аргументи: action (рядок)
  # Повертаєме значення: Масив рядків

  def __splitAction(self, action):
    return action.split(" ")

  # ----------------------------------------------------

  # Ім'я: isCd
  # Опис: Перевіряє на збіг із командою Cd
  # Аргументи: action (рядок)
  # Повертаєме значення: булеве значення
    
  def isCd(self, action):
    splited = self.__splitAction(action)
    if len(splited) >= 2:
      return splited[0] == act["Cd"]
    return False

  # ----------------------------------------------------

  # Ім'я: isClear
  # Опис: Перевіряє на збіг із командою Clear
  # Аргументи: action (рядок)
  # Повертаєме значення: булеве значення

  def isClear(self, action):
    return action == act["Clear"]

  # ----------------------------------------------------

  # Ім'я: isDelete
  # Опис: Перевіряє на збіг із командою Delete
  # Аргументи: action (рядок)
  # Повертаєме значення: булеве значення

  def isDelete(self, action):
    splited = self.__splitAction(action)
    if len(splited) >= 2:
      return splited[0] == act["Delete"]
    return False

  # ----------------------------------------------------

  # Ім'я: isUpload
  # Опис: Перевіряє на збіг із командою Upload
  # Аргументи: action (рядок)
  # Повертаєме значення: булеве значення

  def isUpload(self, action):
    splited = self.__splitAction(action)
    if len(splited) >= 2:
      return splited[0] == act["Upload"]
    return False

  # ----------------------------------------------------

  # Ім'я: isExit
  # Опис: Перевіряє на збіг із командою Exit
  # Аргументи: action (рядок)
  # Повертаєме значення: булеве значення

  def isExit(self, action):
    return action == act["Exit"] or action == act["ExitShort"]

  # ----------------------------------------------------

  # Ім'я: isHelp
  # Опис: Перевіряє на збіг із командою Help
  # Аргументи: action (рядок)
  # Повертаєме значення: булеве значення

  def isHelp(self, action):
    return action == act["Help"] or action == act["HelpShort"]

  # ----------------------------------------------------

  # Ім'я: isChangeEnv
  # Опис: Перевіряє на збіг із командою ChangeEnv
  # Аргументи: action (рядок)
  # Повертаєме значення: булеве значення

  def isChangeEnv(self, action):
    splited = self.__splitAction(action)
    if len(splited) == 2:
      isAct = splited[0] == act["ChangeEnv"]
      local = splited[1] == envs["Local"]
      remote = splited[1] == envs["Remote"]
      return isAct and (local or remote)
    return False

  # ----------------------------------------------------

  # Ім'я: isLs
  # Опис: Перевіряє на збіг із командою Ls
  # Аргументи: action (рядок)
  # Повертаєме значення: булеве значення

  def isLs(self, action):
    return action == act["Ls"]
  
  # ----------------------------------------------------

  # Ім'я: isMkdir
  # Опис: Перевіряє на збіг із командою Mkdir
  # Аргументи: action (рядок)
  # Повертаєме значення: булеве значення

  def isMkdir(self, action):
    splited = self.__splitAction(action)
    if len(splited) >= 2:
      return splited[0] == act["Mkdir"]
    return False

  # ----------------------------------------------------

  # Ім'я: isConnect
  # Опис: Перевіряє на збіг із командою Connect
  # Аргументи: action (рядок)
  # Повертаєме значення: булеве значення

  def isConnect(self, action):
    splited = self.__splitAction(action)
    if len(splited) == 2:
      return splited[0] == act["Connect"]
    return False

  # ----------------------------------------------------

  # Ім'я: isStatus
  # Опис: Перевіряє на збіг із командою Status
  # Аргументи: action (рядок)
  # Повертаєме значення: булеве значення

  def isStatus(self, action):
    return action == act["Status"]

  # ----------------------------------------------------

  # Ім'я: isDownload
  # Опис: Перевіряє на збіг із командою Download
  # Аргументи: action (рядок)
  # Повертаєме значення: булеве значення

  def isDownload(self, action):
    splited = self.__splitAction(action)
    if len(splited) >= 2:
      return splited[0] == act["Download"]
    return False

  # ----------------------------------------------------

  # Ім'я: isWhereAmI
  # Опис: Перевіряє на збіг із командою WhereAmI
  # Аргументи: action (рядок)
  # Повертаєме значення: булеве значення

  def isWhereAmI(self, action):
    isAct = action == act["WhereAmI"]
    isActShort = action == act["WhereAmIShort"]
    return isAct or isActShort

  # ----------------------------------------------------

  # Ім'я: isWhoAmI
  # Опис: Перевіряє на збіг із командою WhoAmI
  # Аргументи: action (рядок)
  # Повертаєме значення: булеве значення

  def isWhoAmI(self, action):
    return action == act["WhoAmI"]

  # ----------------------------------------------------