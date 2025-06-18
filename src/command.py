import subprocess
#import appscript
from sys import platform
from subprocess import check_output

class command():
    def __init__(self, parent):
        super().__init__(parent)

    #adb = adbutils.AdbClient(host="127.0.0.1", port=5037)
    #print(adb.devices())

    def openScrcpy():
        try:
            command = 'scrcpy >& /dev/null & disown'
            if platform == "linux" or platform == "linux2":
                # linux
                print('not support linux')
            elif platform == "darwin":
                # OS X
                #a = os.system('scrcpy >& /dev/null & disown')
                a = subprocess.check_output(command,shell=True,stderr=subprocess.STDOUT)
            elif platform == "win32":
                # Windows...
                #a = os.system('scrcpy >& /dev/null & disown')
                a = subprocess.check_output(command,shell=True,stderr=subprocess.STDOUT)
            return str(a)
        except ValueError as e:
            return (str(e))
        except subprocess.CalledProcessError as e:
            #return RuntimeError("command '{}' return with error (code {}): {}".format(e.cmd, e.returncode, e.output))
            return str(e.output.encode().decode('unicode-escape'))

    def installApk(path):
        try:
            command = 'adb install -r ' + path
            if platform == "linux" or platform == "linux2":
                # linux
                print('not support linux')
            elif platform == "darwin":
                # OS X
                a = subprocess.check_output(command,shell=True,stderr=subprocess.STDOUT)
                #a = os.system(command)
                #appscript.app('Terminal').do_script(command)  # or any other command you choose
            elif platform == "win32":
                # Windows...
                #a = os.system(command)
                a = subprocess.check_output(command,shell=True,stderr=subprocess.STDOUT)
                #appscript.app('cmd').do_script(command)  # or any other command you choose
            return str(a)
        except ValueError as e:
            return (str(e))
        except subprocess.CalledProcessError as e:
            #return RuntimeError("command '{}' return with error (code {}): {}".format(e.cmd, e.returncode, e.output))
            return str(e.output.encode().decode('unicode-escape'))

    #com.netzme.netzmeandroid.staging
    #id.netzme.netzmeandroid
    #id.netzme.netzstore.staging
    #id.netzme.netzstore
    def uninstallApk(path):
        try:
            #executable = ["adb", "shell", "pm", "uninstall", path]
            command = 'adb uninstall ' + path
            if platform == "linux" or platform == "linux2":
                # linux
                print('not support linux')
            elif platform == "darwin":
                # OS X
                a = check_output(command, shell=True)
                #appscript.app('Terminal').do_script(command)  # or any other command you choose
            elif platform == "win32":
                # Windows...
                a = check_output(command, shell=True)
                #appscript.app('cmd').do_script(command)  # or any other command you choose
            return str(a)
        except ValueError as e:
            return (str(e))
        except subprocess.CalledProcessError as e:
            return RuntimeError("command '{}' return with error (code {}): {}".format(e.cmd, e.returncode, e.output))

    #p = '/Users/purbajati/Downloads/staging-debug-PR-368-build-1.apk'
    # install apk
    #print(installApk(p))
