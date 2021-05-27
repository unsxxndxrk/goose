import json
from constants.nsAccessors import nsAccessors

# Ім'я: Namespace
# Опис: Надає інтерфейс для використання просторів імен
# Методи: 
#   - __getNamespace (отримати простір імен)
# Поля:
#   - common (загальний)
#   - interact (простір імен для взаємодії з користувачем)
#   - errors (простір імен для помилок)
#   - help (простір імен для довідки)

class Namespace:
  def __init__(self):
    self.common = self.__getNamespace(nsAccessors["Common"])
    self.interact = self.__getNamespace(nsAccessors["Interact"])
    self.errors = self.__getNamespace(nsAccessors["Errors"])
    self.help = self.__getNamespace(nsAccessors["Help"])

  # Ім'я: __getNamespace
  # Опис: Отримати простір імен
  # Аргументи: accessor (string<Key of actions>)
  # Повертаєме значення: Словник

  def __getNamespace(self, accessor):
    data = []
    with open("namespaces/{}.json".format(accessor)) as json_file: 
      data = json.load(json_file) 
    return data

  # ----------------------------------------------------