from utils.styledText import styledText
from constants.textStyles import textStyles
from modules.Namespace import Namespace
from utils.getHelp import getHelp

ns = Namespace()

# Ім'я: Message
# Опис: Надає можливість використовувати стилізовані повідомлення
# Методи: 
#   - default (звичайне повідомлення)
#   - welcome (повідомлення привітання)
#   - error (помилка)
#   - info (інформативне повідомлення)
#   - success (повідомлення про успіх)
#   - help (довідка)

class Message:

  # Ім'я: default
  # Опис: Звичайне повідомлення
  # Аргументи: text (string)
  # Повертаєме значення: void

  def default(self, text):
    print(text)

  # ----------------------------------------------------

  # Ім'я: welcome
  # Опис: Повідомлення привітання
  # Аргументи: void
  # Повертаєме значення: void

  def welcome(self):
    welcomeMessage = ns.common["welcome_message"]
    style = textStyles["Bold"] + textStyles["White"]
    print(styledText(style + welcomeMessage))

  # ----------------------------------------------------

  # Ім'я: error
  # Опис: Помилка
  # Аргументи: text (string)
  # Повертаєме значення: void

  def error(self, text):
    print(styledText(textStyles["Red"] + text))

  # ----------------------------------------------------

  # Ім'я: info
  # Опис: Інформативне повідомлення
  # Аргументи: text (string)
  # Повертаєме значення: void

  def info(self, text):
    print(styledText(textStyles["Yellow"] + text))

  # ----------------------------------------------------

  # Ім'я: success
  # Опис: Повідомлення про успіх
  # Аргументи: text (string)
  # Повертаєме значення: void

  def success(self, text):
    print(styledText(textStyles["Green"] + text))

  # ----------------------------------------------------

  # Ім'я: help
  # Опис: Довідка
  # Аргументи: void
  # Повертаєме значення: void

  def help(self):
    print(getHelp())

  # ----------------------------------------------------