#!/usr/bin/env python2
import os
import os.path
import urllib
import platform
from zipfile import ZipFile

adbZip = "adb.zip"
platformTools = "platform-tools"

if not os.path.isdir(platformTools):
    if "Linux" in platform.system():
        urllib.urlretrieve(
            "https://dl.google.com/android/repository/platform-tools-latest-linux.zip", adbZip)
    elif "Darwin" in platform.system()
        urllib.urlretrieve(
            "https://dl.google.com/android/repository/platform-tools-latest-darwin.zip", adbZip)
    elif "Windows" in platform.system():
        urllib.urlretrieve(
            "https://storage.googleapis.com/essential-static/Essential-PH1-WindowsDrivers.exe", "driver.exe")
        os.system('driver.exe')
        urllib.urlretrieve(
            "https://dl.google.com/android/repository/platform-tools-latest-windows.zip", adbZip)
    else:
        raise OSError("ADB is not avaliable for this platform")
    zip = ZipFile(adbZip)
    zip.extractall()
    os.remove(adbZip)

os.chdir(platformTools)

if "Linux" in platform.system():
    os.system("chmod +x adb")
    adb_devices = os.system("./adb devices")
elif "Darwin" in platform.system()
    adb_devices = os.system("./adb devices")
elif "Windows" in platform.system():
    adb_devices = os.system("adb.exe devices")

if "unauthorized" in adb_devices:
    raise OSError("Allow access to the computer")
elif "unauthorized" in adb_devices:
    raise OSError("Allow access to the computer")
