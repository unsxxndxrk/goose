import time
import calendar

# Ім'я: getTimestamp
# Опис: Отрмати поточну мітку часу
# Аргументи: void
# Повертаєме значення: number

def getTimestamp():
  return calendar.timegm(time.gmtime())

# ----------------------------------------------------