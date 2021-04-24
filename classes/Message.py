from helpers.styledText import styledText
from constants.textStyles import textStyles
from classes.Namespace import Namespace

Ns = Namespace()

class Message:
  def __init__(self):
    pass

  def default(self, text):
    print(text)
    pass

  def welcome(self):
    welcomeMessage = Ns.common["welcome_message"]
    style = textStyles["Bold"] + textStyles["White"]
    print(styledText(style + welcomeMessage))
    pass

  def error(self, text):
    print(styledText(textStyles["Red"] + text))
    pass

  def info(self, text):
    print(styledText(textStyles["Yellow"] + text))
    pass

  def success(self, text):
    print(styledText(textStyles["Green"] + text))
    pass

  def suspend(self, text):
    print(styledText(textStyles["Violet"] + text))
    pass

  def serverResponse(self, text):
    print(Ns.common["server_says"], text)
    pass