'''
Remote control to trigger all custom programs
of Quanvas as they are needed by the user
'''
from packages import *

points = ["argentinafx","ATM","micro","macro","todo_maintenance",\
          "perform_maintenance","update","owly","bienvenido","welcome","resume"]

endpoints = {k: v for k, v in enumerate(points)}

def commands(points):
    os.system("clear")
    [print(f"{i} : {points[i]}") for i in range(len(points))]
    cmd = input("\nSELECT A PROGRAM TO EXECUTE\n\n\n>>>\t")
    try: # let the user choose
      cmd = int(cmd)
      os.system(
                 f"python {endpoints[cmd]}.py"
               )
    except: # if not, let run a custom terminal command
      os.system(f"{cmd}")
    input("\nPRESS [ENTER] in order to continue")
    commands(points)

if __name__ == '__main__':
  commands(points)
