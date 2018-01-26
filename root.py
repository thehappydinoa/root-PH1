#!/usr/bin/env python2
import os
import os.path
import platform
from time import sleep
from zipfile import ZipFile
from urllib import urlretrieve
from subprocess import check_output

platformTools = "platform-tools"
platformToolsZip = platformTools + ".zip"

if not os.path.isdir(platformTools):
    print("Setting up ADB")
    if "Linux" in platform.system():
        urlretrieve(
            "https://dl.google.com/android/repository/platform-tools-latest-linux.zip", platformToolsZip)
    elif "Darwin" in platform.system():
        urlretrieve(
            "https://dl.google.com/android/repository/platform-tools-latest-darwin.zip", platformToolsZip)
    elif "Windows" in platform.system():
        urlretrieve(
            "https://storage.googleapis.com/essential-static/Essential-PH1-WindowsDrivers.exe", "driver.exe")
        os.system('driver.exe')
        urlretrieve(
            "https://dl.google.com/android/repository/platform-tools-latest-windows.zip", platformToolsZip)

    zip = ZipFile(platformToolsZip)
    zip.extractall()
    os.remove(platformToolsZip)

os.chdir(platformTools)


if "Linux" in platform.system() or "Darwin" in platform.system():
    os.system("chmod +x adb")
    os.system("chmod +x fastboot")
    adbCommand = "./adb"
    fastbootCommand = "./fastboot"
elif "Windows" in platform.system():
    adbCommand = "adb.exe"
    fastbootCommand = "fastboot.exe"


def getDevices():
    print("Getting device list..."),
    adb_devices = check_output([adbCommand, "devices", "-l"])

    if "unauthorized" in adb_devices:
        print("Allow access to the computer")
        exit(1)
    elif not "device:mata" in adb_devices:
        print("Not Found")
        print("Please connect your Essential Phone")
        exit(1)
    else:
        print("Found")


def getBuild():
    print("Finding build number... "),
    adb_build_id = check_output(
        [adbCommand, "shell", "getprop", "ro.build.display.id"])
    print(adb_build_id)

    beta_build_ids = ["OPM1.170911.130",
                      "OPM1.170911.213", "OPM1.170911.254"]
    if not adb_build_id in beta_build_ids:
        print("Beta builds are supported only")
        exit(1)


def magiskManager():
    print("Downloading Magisk Manager... "),
    magiskManagerPath = "../Magisk/MagiskManager-v5.5.5.apk"
    urlretrieve(
        "https://github.com/topjohnwu/MagiskManager/releases/download/v5.5.5/MagiskManager-v5.5.5.apk", magiskManagerPath)
    print("Done\n")

    print("Installing Magisk Manager... "),
    adb_install_magiskManager = check_output(
        [adbCommand, "install", magiskManagerPath])
    print("Done")


def rebootBootloader():
    print("Rebooting into bootloader... "),
    check_output(
        [adbCommand, "reboot", "bootloader"])

    fastboot_devices = check_output([fastbootCommand, "devices"])
    checks = 0
    while not "fastboot" in fastboot_devices and checks < 3:
        sleep(3)
        fastboot_devices = check_output([fastbootCommand, "devices"])
        checks += 1
    if not "fastboot" in fastboot_devices:
        print("Please try again")
        exit(1)
    print("Done")


def unlockBootloader():
    fastboot_oem_info = check_output([fastbootCommand, "oem", "device-info"])
    if "Device unlocked: false" in fastboot_oem_info:
        print("To root your device your bootloader must be unlocked")
        print("Unlocking your bootloader will wipe your device")
        response = raw_input("Unlock bootloader now? (y/n)").lower()
        if response == "y":
            bootloader_unlock = check_output(
                [fastbootCommand, "flashing", "unlock"])
            print("Press the Volume-down button to navigate to the YES option, then press the Power button to confirm")
        else:
            print("To root your device your bootloader must be unlocked")
            print("Rebooting...")
            check_output(
                [fastbootCommand, "continue"])
            exit(1)


def installTWRP():
    print("Installing TWRP... "),
    twrpImage = "../boot-images/twrp-mata_11.img"
    fastboot_flash = check_output(
        [fastbootCommand, "flash", "boot", twrpImage])
    if "error: cannot load" in fastboot_flash:
        print("Please try again")
        exit(1)
    print("Done")


def installMagisk():
    print("Downloading Magisk... "),
    magiskPath = "../Magisk/Magisk.zip"
    urlretrieve("http://tiny.cc/latestmagisk", magiskPath)
    print("Done")

    print("\n1. Press the Volume-down button twice to navigate to the Recovery mode option, then press the Power button to confirm")
    print("2. Enter your password/pin/pattern to decrypt your data")
    print("3. Swipe to Allow Modifications\n")
    raw_input("Click [return] when you have reached the TWRP main menu")
    sleep(1)
    adb_mount = check_output([adbCommand, "shell", "mount", "/system"])
    sleep(1)
    adb_twrp_sideload = check_output([adbCommand, "shell", "twrp", "sideload"])
    sleep(1)
    adb_sideload = check_output([adbCommand, "sideload", magiskPath])
    print("\nClick on Reboot then select the bootloader option. Make sure to select 'Do not install' when asked about TWRP app\n")
    raw_input("Click [return] when you have reached the bootloader main menu")
    patchedImagePath = "../boot-images/patched/%s.img" % adb_build_id
    fastboot_flash = check_output(
        [fastbootCommand, "flash", "boot", patchedImagePath])
    check_output([fastbootCommand, "continue"])


if __name__ == "__main__":
    getDevices()
    getBuild()
    try:
        magiskManager()
        rebootBootloader()
        unlockBootloader()
        installTWRP()
        print("Your Essential Phone should now be rooted")
    except KeyboardInterrupt:
        print("Please do not quit while your device is being rooed")
