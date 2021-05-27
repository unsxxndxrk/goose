from constants.actions import actions as act
from utils.styledText import styledText
from constants.textStyles import textStyles
from modules.Namespace import Namespace
from constants.environments import environments as envs

ns = Namespace().help

# Ім'я: getHelp
# Опис: Форматування тексту довідки
# Аргументи: void
# Повертаєме значення: string

def getHelp():
  actStyle = textStyles["Bold"] + textStyles["White"]
  noteStyle = textStyles["Yellow"]

  note1 = styledText(noteStyle + ns["note1"])
  note2 = styledText(noteStyle + ns["note2"])
  note3 = styledText(noteStyle + ns["note3"])

  connect = styledText(actStyle + act["Connect"])
  upload = styledText(actStyle + act["Upload"])
  download = styledText(actStyle + act["Download"])
  changeEnv = styledText(actStyle + act["ChangeEnv"])
  delete = styledText(actStyle + act["Delete"])
  mkdir = styledText(actStyle + act["Mkdir"])
  cd = styledText(actStyle + act["Cd"])
  clear = styledText(actStyle + act["Clear"])
  ls = styledText(actStyle + act["Ls"])
  whereami = styledText(actStyle + act["WhereAmI"])
  whereamiShort = styledText(actStyle + act["WhereAmIShort"])
  whoami = styledText(actStyle + act["WhoAmI"])
  helpAct = styledText(actStyle + act["Help"])
  helpActShort = styledText(actStyle + act["HelpShort"])
  exit = styledText(actStyle + act["Exit"])
  exitShort = styledText(actStyle + act["ExitShort"])
  status = styledText(actStyle + act["Status"])

  connectExample = ns["connect_example"]
  connectDesc = ns["connect"]

  uploadExample = ns["upload_example"]
  uploadDesc = ns["upload"]

  downloadExample = ns["download_example"]
  downloadDesc = ns["download"]

  localEnv = envs["Local"]
  remoteEnv = envs["Remote"]
  localEnvDesc = ns["changeLocalEnv"]
  remoteEnvDesc = ns["changeRemoteEnv"]

  statusDesc = ns["status"]

  mkdirExample = ns["mkdir_example"]
  mkdirDesc = ns["mkdir"]

  deleteExample = ns["delete_example"]
  deleteDesc = ns["delete"]

  cdExample = ns["cd_example"]
  cdDesc = ns["cd"]

  lsDesc = ns["ls"]
  whereamiDesc = ns["whereami"]
  whoamiDesc = ns["whoami"]
  clearDesc = ns["clear"]
  helpDesc = ns["help"]
  exitDesc = ns["exit"]

  _or = ns["or"]

  return f"""
    {note1}
    {note2}
    {note3}
    {connect} {connectExample} -- {connectDesc}
    {upload} {uploadExample} -- {uploadDesc} 
    {download} {downloadExample} -- {downloadDesc}
    {changeEnv} {localEnv} -- {localEnvDesc}
    {changeEnv} {remoteEnv} -- {remoteEnvDesc}
    {status} -- {statusDesc}
    {mkdir} {mkdirExample} -- {mkdirDesc}
    {delete} {deleteExample} -- {deleteDesc}
    {cd} {cdExample} -- {cdDesc}
    {ls} -- {lsDesc}
    {whereami} {_or} {whereamiShort} -- {whereamiDesc}
    {whoami} -- {whoamiDesc}
    {clear} -- {clearDesc}
    {helpAct} {_or} {helpActShort} -- {helpDesc}
    {exit} {_or} {exitShort} -- {exitDesc}
    """
    
# ----------------------------------------------------