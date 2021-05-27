from halo import Halo

# Ім'я: Spinner
# Опис: Надає інтерфейс для використання графічного спінеру
# Методи: 
#   - start (запуск спінеру)
#   - success (зупинка з успішним повідомленням)
#   - fail (зупинка з повідомленням про помилку)
#   - stop (зупинка спінеру)

class Spinner:
  def __init__(self):
    self.spinner = Halo(spinner="dots")

  # Ім'я: start
  # Опис: Запуск спінеру
  # Аргументи: text (string)
  # Повертаєме значення: void

  def start(self, text):
    self.spinner.start(text)

  # ----------------------------------------------------

  # Ім'я: success
  # Опис: Зупинка з успішним повідомленням
  # Аргументи: text (string)
  # Повертаєме значення: void

  def success(self, text):
    self.spinner.succeed(text)

  # ----------------------------------------------------

  # Ім'я: fail
  # Опис: Зупинка з повідомленням про помилку
  # Аргументи: text (string)
  # Повертаєме значення: void

  def fail(self, text):
    self.spinner.fail(text)

  # ----------------------------------------------------

  # Ім'я: stop
  # Опис: Зупинка спінеру
  # Аргументи: void
  # Повертаєме значення: void

  def stop(self):
    self.spinner.stop()

  # ----------------------------------------------------
