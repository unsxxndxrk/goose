import subprocess

# Ім'я: execCmd
# Опис: Виконання Linux команд в терміналі
# Аргументи: command (string)
# Повертаєме значення: будь-яке

def execCmd(command):
  try:
    process = subprocess.Popen(command, stdout = subprocess.PIPE, shell = True)
    stdout = process.communicate()[0].strip()
    return stdout.decode("utf-8")
  except:
    return False

# ----------------------------------------------------