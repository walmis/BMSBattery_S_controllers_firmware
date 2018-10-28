import pip
import os
import requests
import ctypes, sys
import traceback
import subprocess
import zipfile
import tarfile
import shutil
from distutils.dir_util import copy_tree, remove_tree, mkpath
from glob import glob

try:
    def is_admin():
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            return False

    if not is_admin():
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, __file__, None, 1)
        exit(0)

    pip.main(["install", "PyQt5"])
    pip.main(["install", "wget"])

    import wget
    if not os.path.exists("dl"):
        os.mkdir("dl")


    if not os.path.exists("dl/cygwin-x86-64.exe"):
        print("Downloading Cygwin")
        wget.download("https://cygwin.com/setup-x86_64.exe", "dl/cygwin-x86-64.exe")
        print()

    if not os.path.exists("cygwin"):
        print("Installing cygwin")
        os.mkdir("cygwin")

        os.chdir("dl")
        cygwin_args = ["cygwin-x86-64.exe", "--no-desktop", "--no-shortcuts",
                       "--quiet-mode", "--no-verify", "--wait", "--no-admin"]

        #cygwin_args += ["-s", "https://sourceforge.net/projects/stm8-binutils-gdb/files/cygwin/"]
        cygwin_args += ["-s", "http://ftp.rnl.tecnico.ulisboa.pt/pub/cygwin/"]
        cygwin_args += ["-s", "http://ftp.acc.umu.se/mirror/cygwin/"]
        cygwin_args.append("-R")
        cygwin_args.append("../cygwin/")
        #cygwin_args += ["-P", "stm8-binutils-gdb"]
        #cygwin_args += ["-P", "cmake"] old version, download seperately
        cygwin_args += ["-P", "make"]
        #cygwin_args += ["-P", "sdcc"]

        if 1:
            p = subprocess.Popen(cygwin_args)
            ret = p.wait()
            if ret == 0:
                print("Cygwin install OK")
            else:
                raise Exception("Failed to install cygwin")

        os.chdir("..")

    binutils_ver = "stm8-binutils-gdb-8.1-20180304"
    if not os.path.exists(f"dl/{binutils_ver}.tar.xz"):
        print(f"Downloading {binutils_ver}")
        wget.download(f"https://sourceforge.net/projects/stm8-binutils-gdb/files/cygwin/x86_64/release/stm8-binutils-gdb/{binutils_ver}.tar.xz", "dl")
        print()

    print(f"Extracting {binutils_ver}")
    f = tarfile.open(f"dl/{binutils_ver}.tar.xz", "r")
    mkpath(f"dl/{binutils_ver}")
    f.extractall(f"dl/{binutils_ver}")
    f.close()
    print(f"Installing {binutils_ver}")
    copy_tree(f"dl/{binutils_ver}/usr/local/", "cygwin/")

# DOWNLOAD CMAKE
    cmake_ver = "cmake-3.12.3-win64-x64"
    if not os.path.exists(f"dl/{cmake_ver}.zip"):
        print(f"Downloading {cmake_ver}")
        wget.download(f"https://cmake.org/files/v3.12/{cmake_ver}.zip", "dl")
        print()

    print(f"Extracting {cmake_ver}.zip" )
    zip_ref = zipfile.ZipFile(f"dl/{cmake_ver}.zip", 'r')
    zip_ref.extractall("dl")
    zip_ref.close()

    print(f"Installing {cmake_ver}")
    copy_tree(f"dl/{cmake_ver}", "cygwin", verbose=1)
    remove_tree(f"dl/{cmake_ver}")
################

    print("Downloading stm8flash")
    wget.download("https://github.com/walmis/BMSBattery_S_controllers_firmware/releases/download/1.0/stm8flash.zip", "dl")
    print()

    print("Installing stm8flash")
    zip_ref = zipfile.ZipFile("dl/stm8flash.zip", 'r')
    zip_ref.extractall("cygwin/bin")
    zip_ref.close()

    if 1:
        if not os.path.exists("dl/sdcc-3.8.0.zip"):
            print("Downloading sdcc-3.8.0")
            wget.download("https://github.com/walmis/BMSBattery_S_controllers_firmware/releases/download/1.0/sdcc-3.8.0.zip", "dl")
            print()

        print("Installing sdcc-3.8.0")
        zip_ref = zipfile.ZipFile("dl/sdcc-3.8.0.zip", 'r')
        zip_ref.extractall("cygwin")
        zip_ref.close()


    print("Installation successful")


except Exception as e:
    print (traceback.print_exc())

input("Press any key to continue")
