from utils.styledText import styledText
from constants.textStyles import textStyles
from modules.Namespace import Namespace

ns = Namespace().interact

# Ім'я: Interact
# Опис: Надає можливість користувачеві взаємодіяти з програмою
# Методи: 
#   - confirm (підтвердження)
#   - multiInput (багаторядкове введення даних)

class Interact:

  # Ім'я: confirm
  # Опис: Підтвердження
  # Аргументи: question (string)
  # Повертаєме значення: boolean

  def confirm(self, question):
    q = question + "\n"
    yes = ns["confirm"]["yes"]
    yesShort = ns["confirm"]["short_yes"]
    confTip = ns["confirm"]["tip"]
    conf = input(styledText(textStyles["Yellow"] + q + confTip))
    confLover = conf.lower()
    if confLover == yes or confLover == yesShort:
      return True
    return False

  # ----------------------------------------------------

  # Ім'я: multiInput
  # Опис: Багаторядкове введення даних
  # Аргументи: fields (масив рядків)
  # Повертаєме значення: Словник,
  #         кожен ключ - ключ значення масиву, кожне значення - відповідь користувача 

  def multiInput(self, fields):
    result = {}
    for field in fields:
      userInput = input(field + ": ")
      result[field] = userInput
    return result

  # ----------------------------------------------------