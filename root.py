#!/usr/bin/env python2
import sys
import os
import os.path
import platform
from time import sleep
from zipfile import ZipFile
from urllib import urlretrieve
from subprocess import check_output, CalledProcessError

platformTools = "platform-tools"
platformToolsZip = platformTools + ".zip"
magiskFolder = "magisk"

logo = '''
88""Yb  dP"Yb   dP"Yb  888888          88""Yb 88  88   .d
88__dP dP   Yb dP   Yb   88   ________ 88__dP 88  88 .d88
88"Yb  Yb   dP Yb   dP   88   """""""" 88"""  888888   88
88  Yb  YbodP   YbodP    88            88     88  88   88
'''

if not os.path.isdir(magiskFolder):
    os.mkdir(magiskFolder)

if not os.path.isdir(platformTools):
    print("Setting up ADB")
    if "Linux" in platform.system():
        urlretrieve(
            "https://dl.google.com/android/repository/platform-tools-latest-linux.zip",
            platformToolsZip)
    elif "Darwin" in platform.system():
        urlretrieve(
            "https://dl.google.com/android/repository/platform-tools-latest-darwin.zip",
            platformToolsZip)
    elif "Windows" in platform.system():
        urlretrieve(
            "https://storage.googleapis.com/essential-static/Essential-PH1-WindowsDrivers.exe",
            "driver.exe")
        os.system('driver.exe')
        urlretrieve(
            "https://dl.google.com/android/repository/platform-tools-latest-windows.zip",
            platformToolsZip)

    zip_file = ZipFile(platformToolsZip)
    zip_file.extractall()
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


def menu():
    try:
        os.system('cls' if os.name == 'nt' else 'clear')
        print(logo)
        print("1. Root with Magisk")
        print("2. Unroot")
        print("3. Unlock Bootloader Only")
        print("4. Exit\n")
        try:
            choice = int(raw_input("Enter your choice [1-4]: "))
        except ValueError:
            print("Please enter a int")
            menu()

        print('\n')

        if choice == 1:
            root()
        elif choice == 2:
            unroot()
        elif choice == 3:
            rebootBootloader()
            unlockBootloader()
        elif choice == 4:
            sys.exit()
        else:
            menu()
    except KeyboardInterrupt:
        menu()


def getDevices():
    print("Getting device list..."),
    adb_devices = check_output([adbCommand, "devices", "-l"])

    if "unauthorized" in adb_devices:
        print("Allow access to the computer")
        return False
    elif not "device:mata" in adb_devices:
        print("Not Found")
        print("Please connect your Essential Phone")
        print("Waiting...")
        found = False
        checks = 0
        while not found and checks <= 60:
            adb_devices = check_output([adbCommand, "devices", "-l"])
            found = ("device:mata" in adb_devices)
            if found:
                print("Found")
                return True
            checks += 1
            sleep(1)
        print("Could not find your Essential Phone")
        sys.exit()
    else:
        print("Found")
        return True


def getBuild():
    print("Finding build number... "),
    adb_build_id = check_output(
        [adbCommand, "shell", "getprop", "ro.build.display.id"]).strip()
    print(adb_build_id)

    build_ids = [
        "OPM1.170911.130", "OPM1.170911.213", "OPM1.170911.254",
        "OPM1.180104.010", "OPM1.180104.092", "OPM1.180104.141",
        "OPM1.180104.166"
    ]
    if not adb_build_id in build_ids:
        print("Current supported builds:")
        for build in build_ids:
            print("  " + build)
        exit(1)


def magiskManager():
    print("Downloading Magisk Manager... "),
    magiskManagerPath = "../%s/MagiskManager-v5.7.0.apk" % magiskFolder
    urlretrieve(
        "https://github.com/topjohnwu/MagiskManager/releases/download/v5.7.0/MagiskManager-v5.7.0.apk",
        magiskManagerPath)
    print("Done\n")

    print("Installing Magisk Manager... "),
    check_output([adbCommand, "install", magiskManagerPath])
    print("Done")


def rebootBootloader():
    try:
        print("Rebooting into bootloader... "),
        check_output([adbCommand, "reboot", "bootloader"])

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
    except CalledProcessError as e:
        print("Error: " + str(e))
        sleep(3)
        menu()


def unlockBootloader():
    fastboot_oem_info = check_output([fastbootCommand, "oem", "device-info"])
    if "Device unlocked: false" in fastboot_oem_info:
        print("To root your device your bootloader must be unlocked")
        print("Unlocking your bootloader will wipe your device")
        response = raw_input("Unlock bootloader now? (y/n)").lower()
        if response == "y":
            check_output([fastbootCommand, "flashing", "unlock"])
            print(
                "Press the Volume-down button to navigate to the YES option, then press the Power button to confirm"
            )
        else:
            print("To root your device your bootloader must be unlocked")
            print("Rebooting...")
            check_output([fastbootCommand, "continue"])
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
    magiskPath = "../%s/Magisk.zip" % magiskFolder
    urlretrieve("http://tiny.cc/latestmagisk", magiskPath)
    print("Done")

    print(
        "\n1. Press the Volume-down button twice to navigate to the Recovery mode option, then press the Power button to confirm"
    )
    print("2. Enter your password/pin/pattern to decrypt your data")
    print("3. Swipe to Allow Modifications\n")
    raw_input("Click [return] when you have reached the TWRP main menu")
    sleep(1)
    check_output([adbCommand, "shell", "mount", "/system"])
    sleep(1)
    check_output([adbCommand, "shell", "twrp", "sideload"])
    sleep(1)
    check_output([adbCommand, "sideload", magiskPath])
    print(
        "\nClick on Reboot then select the bootloader option. Make sure to select 'Do not install' when asked about TWRP app\n"
    )
    raw_input("Click [return] when you have reached the bootloader main menu")
    patchedImagePath = "../boot-images/patched/%s.img" % adb_build_id
    check_output([fastbootCommand, "flash", "boot", patchedImagePath])
    check_output([fastbootCommand, "continue"])


def root():
    getDevices()
    getBuild()
    try:
        magiskManager()
        rebootBootloader()
        unlockBootloader()
        installTWRP()
        installMagisk()
        print("Your Essential Phone should now be rooted")
    except KeyboardInterrupt:
        print("Please do not quit while your device is being rooted")


def unroot():
    getDevices()
    getBuild()
    raw_input(
        "Click [return] when you have made sure all passwords, pins, or patterns have been turned off"
    )
    try:
        rebootBootloader()
        raw_input(
            "Click [return] when you have reached the bootloader main menu")
        stockImagePath = "../boot-images/stock/%s.img" % adb_build_id
        check_output([fastbootCommand, "flash", "boot", stockImagePath])
        print("Your Essential Phone should now be unrooted")
    except KeyboardInterrupt:
        print("Please do not quit while your device is being unrooted")


if __name__ == "__main__":
    menu()
