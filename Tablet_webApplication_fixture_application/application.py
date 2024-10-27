from time import sleep
from rich.console import Console
from rich.panel import Panel
from art import text2art
from pyadb import ADB
import os
from pathlib import Path
import subprocess
from glob import glob
from shutil import copy

# due to setting appData/Local directory as root path, this program can only used as console script of py2exe -> inno setup pipeline.
current_path = Path(os.getcwd())
username = os.getlogin()
local_appdata_path = os.getenv('LOCALAPPDATA')

application_name = "Artiman Samrt Home-Tablets Upgrader"

local_appdata_application_path = os.path.join(local_appdata_path, application_name)
# adb_path = os.path.join(os.getcwd(), Path("platform-tools/adb.exe"))
adb_path = os.path.join(local_appdata_path, application_name , Path("platform-tools/adb.exe"))
adb = ADB(adb_path=adb_path)

console = Console()
console.print()
console.print()

current_process = None

def print_header():
    header1 = text2art("Artiman Smart", font="colossal")
    console.print(f"[green]{header1}")

def print_help():
    console.print("First, make sure the USB debugging option is enabled on the desired tablet. Then, press any key to continue...", style="bold red")

def print_introduction():

    console.print(Panel(
        "[bold blue]This program is designed to make significant changes to Android 6.0.1 tablets. These devices have two main problems:\n\n1. The default WebView application is outdated, so we need to update it with a newer version. Due to Android security restrictions, we need to modify some OS files, recompile them, and then push the new files to the device for the OS to allow the use of the updated WebView application.\n\n2. The absence of the required SSL certificate. We need to install CA certificates to enable secure connections with our server over TLS.",
        padding=1
    ))

def command_process(command_list):
    try:
        adb_proc = subprocess.Popen(
                command_list,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                shell=False)
        (output, error) = adb_proc.communicate()
        # return_code = adb_proc.returncode
        output = output.decode('utf-8')
        error = error.decode('utf-8')

        if len(output) == 0:
            output = None
        else:
            output = [x.strip() for x in output.split('\n')
                        if len(x.strip()) > 0]

    except Exception as err:
        console.print("Unexpected exception")
        raise RuntimeError(str(err))

    return output, error

########################################
############### TASKS ##################
########################################

def check_adb_existance():
    try:
        console.print(f"task 1 -> Check ADB Software Existance", style="blink bold white underline on green")
        sleep(1)
        adb_version = adb.get_version()
        if adb_version:
            console.print(f"ADB Software is exist :: current version: {adb_version}")
        else:
            raise RuntimeError("Can't find ADB software. please make sure it is installed on your system and try again!")
    except Exception as e:
        raise RuntimeError(f"adb command not work :: command: adb version :: Exception : {e}")


def restart_adb_daemon():
    try:
        console.print(f"task 2 -> Start ADB Daemon", style="blink bold white underline on green")
        sleep(1)
        adb_version = adb.start_server()
        console.print(f"[bold green]ADB Daemon started Successfully.")
    except Exception as e:
        console.print(f"[bold green]ADB Daemon not started Successfully.")
        console.print(f"Restart ADB Daemon")
        adb.restart_server()
        console.print(f"[bold green]ADB Daemon started Successfully.")
        # raise RuntimeError(f"adb command not work :: command: adb reconnect :: Exception : {e}")
    

def get_devices():
    try:
        console.print(f"task 3 -> Get Connected Devices", style="blink bold white underline on green")
        sleep(1)
        ## note: get error "Must set target device first". so i comment it.
        # console.print(f"Wait for device", style="blink bold magenta")
        # while True:
        #     status = adb.wait_for_device()
        #     # this condition checking is not correct because "adb wait_for_device" command not return any output or error until detect a device.after that only close terminal.
        #     # so if we passed from this function means any device connect to computer and we don't need to while and break and condition.
        #     if status:
        #         break
        #     sleep(0.5)
        adb_devices = adb.get_devices()
        if adb_devices:
            if len(adb_devices) > 1:
                console.print(f"Please Connect Only One device")
            elif len(adb_devices) == 0:
                console.print(f"No device detected. please make sure that the USB debuging is ON. Also check USB connection!!!")
            elif len(adb_devices) == 1:
                console.print(f"Detect Conencted Device :: Device Serial Number: {adb_devices[0]}")
                adb.set_target_device(adb_devices[0])
                console.print(f"Set Conencted Device as Target Device.")
        else:
            raise RuntimeError("Can't find any devices. please make sure that the USB debuging is ON. Also check USB connection and try again!")
    except Exception as e:
        raise RuntimeError(f"adb command not work :: command: adb devices :: Exception : {e}")



def change_user_to_root():
    try:
        console.print(f"task 4 -> restarts the adbd daemon with root permissions.", style="blink bold white underline on green")
        sleep(1)
        adb_version = adb.set_adb_root()
        if adb_version:
            console.print(f"the adb daemon set as root.")
        else:
            raise RuntimeError("Can't start the adbd daemon with root permissions.")
    except Exception as e:
        raise RuntimeError(f"adb command not work :: command: adb remount :: Exception : {e}")

def mount_system_writable():
    try:
        console.print(f"task 5 -> Mounts /system as Read/Write", style="blink bold white underline on green")
        sleep(1)
        adb_version = adb.set_system_rw()
        if adb_version:
            console.print(f"Mount seccessfully.")
        else:
            raise RuntimeError("Can't mount system directory.")
    except Exception as e:
        raise RuntimeError(f"adb command not work :: command: adb remount :: Exception : {e}")


def install_lets_encrypt_certs():
    console.print(f"task 6 -> Start installing Let's Encrypt Certificates.", style="blink bold white underline on green")
    sleep(1)
    try:
        for file_path in glob(str(os.path.join(local_appdata_application_path , Path("resources/letsencrypt-certs/pem_cert_files/"),  "*.pem"))):
            file_path = Path(file_path)
            file_name = file_path.parts[-1]
            cert_name = file_name.replace("-", " ").upper()
            console.print(f"[bold magenta]Using let's encrypt {cert_name} certificate.")
            output = command_process([os.path.join(local_appdata_application_path, Path("resources/openssl/openssl.exe")), 
                                      "x509", 
                                      "-inform", 
                                      "PEM", 
                                      "-subject_hash_old", 
                                      "-in", 
                                      Path(f"{local_appdata_application_path}/resources/letsencrypt-certs/pem_cert_files/{file_name}")
                                      ])
            console.print("Generate subject hash code.")
            cert_subject_hash = output[0][0].strip()
            cert_body = output[0][1:]
            console.print(cert_body)
            console.print("Regenerate certificate file.")
            copy(Path(f"{local_appdata_application_path}/resources/letsencrypt-certs/pem_cert_files/{file_name}"), Path(f"{local_appdata_application_path}/resources/letsencrypt-certs/generated_certs/{cert_subject_hash}.0"))
            source_path = os.path.join(local_appdata_application_path, Path(f"resources/letsencrypt-certs/generated_certs/{cert_subject_hash}.0"))
            dest_path = "/system/etc/security/cacerts/"
            adb.shell_command(f"push {source_path} {dest_path}")
            adb.shell_command(f"chmod 644 {dest_path}{cert_subject_hash}.0")
            console.print("[bold blue]Placed certificate file to system directory.")

    except Exception as e:
        raise RuntimeError(f"get error while working with cert files. error: {e}")


def reboot_device():
    try:
        adb._output_if_no_error(adb.run_cmd("reboot"))
    except Exception as e:
        raise RuntimeError(f"reboot process not complete successfully.")


def wait_to_complete_reboot_process():
    console.print("wait to complete reboot process.")
    while True:
        try:
            sleep(1)
            state = adb.get_state()
            if state[0] == "device":
                console.print("Wait for the operating system to load completely.")
                boot_status = adb.shell_command("getprop sys.boot_completed | grep 1")
                if str(boot_status[0][0]) == "1":
                    console.print("The operating system is up now.")
                    break
        except Exception as e:
            console.print("please wait...")
            # raise RuntimeError(f"get error while waiting for device. error: {e}")


def verify_certificates_installation():
    console.print(f"task 7 -> [bold magenta]Verify certificates installation.", style="blink bold white underline on green")
    verified_counter = 0
    cert_counter = 0
    try:
        for file_path in glob(str(os.path.join(local_appdata_application_path , Path("resources/letsencrypt-certs/pem_cert_files/"),  "*.pem"))):
            file_path = Path(file_path)
            file_name = file_path.parts[-1]
            cert_counter += 1
            cert_name = file_name.replace("-", " ").upper()
            console.print(f"[bold magenta]check let's encrypt {cert_name} certificate installation status.")
            output = command_process([os.path.join(local_appdata_application_path, Path("resources/openssl/openssl.exe")), "x509", "-inform", "PEM", "-subject_hash_old", "-in", Path(f"{local_appdata_application_path}/resources/letsencrypt-certs/pem_cert_files/{file_name}")])
            cert_subject_hash = output[0][0].strip()
            output:str = adb.shell_command(f"ls /system/etc/security/cacerts/ | grep \"{cert_subject_hash}.0\"")
            if output[0][0].strip() == f"{cert_subject_hash}.0":
                verified_counter += 1
        if verified_counter == cert_counter:
            console.print("All certificates installed successfully")
        else:
            raise RuntimeError("Certificates installation verification failed. some certs not installed successfully.")
    except Exception as e:
        raise RuntimeError(f"get error while working with cert files. error: {e}")


# don't need to delete older version.
# def remove_com_android_webview_application():
#     pass

def install_com_google_android_webview_application():
    try:
        console.print("Task 8 -> Installing new webview version...", style="blink bold white underline on green")
        adb.shell_command("mkdir /system/app/ChromiumWebview")
        webview_apk_source = str(Path(f"{local_appdata_application_path}/resources/ChromiumWebview/webview.apk"))
        webview_lib_source_path = str(Path(f"{local_appdata_application_path}/resources/ChromiumWebview/lib"))
        adb.shell_command(f"push {webview_apk_source} /system/app/ChromiumWebview/webview.apk")
        adb.shell_command(f"push {webview_lib_source_path} /system/app/ChromiumWebview/")
        adb.shell_command("find /system/app/ChromiumWebview/ -type d -exec chmod 775 {} +")
        adb.shell_command('find . -type f -name "*.so" -exec chmod 644 {} +')
        adb.shell_command("chmod 644 /system/app/ChromiumWebview/webview.apk")
        console.print("[bold blue]successfully transfer webview files.")
    except Exception as e:
        console.print(f"occur error while installing new webview application. error: {e}")

def verify_package_registered_with_the_package_manager():
    try:
        console.print("Task 9 -> Verifying new webview installation...", style="blink bold white underline on green")
        output = adb.shell_command("pm list packages | grep com.google.android.webview")
        if output[0][0] in "package:com.google.android.webview":
            output = adb.shell_command("cat /data/system/packages.xml | grep com.google.android.webview")
            if output[0][0]:
                console.print("[bold blue]webview installation verified.")
    except Exception as e:
        console.print(f"error occur in checking package manager. error: {e}")

def replace_framework_res_apk_file():
    try:
        console.print("Task 10 -> Editing Operation system files...", style="blink bold white underline on green")
        os.makedirs(Path(f"{local_appdata_application_path}/resources/original_framework_res_files/{adb._target}"), exist_ok=True)
        destination_path = str(Path(f"{local_appdata_application_path}/resources/original_framework_res_files/{adb._target}/"))
        adb.shell_command(f"pull /system/framework/framework-res.apk {destination_path}")
        source_path = str(Path(f"{local_appdata_application_path}/resources/modified_framework_res/framework-res.apk"))
        adb.shell_command(f"push {source_path} /system/framework/framework-res.apk")
        sleep(10)
        console.print("[bold blue]Successfully Modify Operation System Files.")
    except Exception as e:
        console.print(f"error occur in modifying Operation System Files. error: {e}")


def restore_original_framework_res_file():
    try:
        console.print("Restoring Original Operation Files...", style="blink bold white underline on green")
        source_path = str(Path(f"{local_appdata_application_path}/resources/original_framework_res_files/{adb._target}/framework-res.apk"))
        adb.shell_command(f"push {source_path} /system/framework/framework-res.apk")
    except Exception as e:
        console.print(f"error occur in reverting Operation system files. error: {e}")

def wait_to_complete_reboot_process_after_change_framework_res_file():
    console.print("wait to complete reboot process.")
    timer = 0
    while True:
        try:
            sleep(1)
            timer += 1
            if timer > 100 :
                console.print(Panel("It seems an unknown problem has occurred.Press any key to revert recent changes...", style="bold red"))
                input()
                restore_original_framework_res_file()
                reboot_device()
                wait_to_complete_reboot_process()
                break
            state = adb.get_state()
            if state[0] == "device":
                boot_status = adb.shell_command("getprop sys.boot_completed | grep 1")
                if str(boot_status[0][0]) == "1":
                    console.print("The operating system is up now.")
                    break

        except Exception as e:
            console.print("please wait...")
            # raise RuntimeError(f"get error while waiting for device. error: {e}")


def main():
    print_header()
    print_introduction()
    print_help()
    input()

    with console.status("[bold green]Working on tasks...", spinner="bouncingBar") as status:
        try:
            check_adb_existance()
            sleep(1)
            restart_adb_daemon()
            sleep(1)
            get_devices()
            sleep(1)
            change_user_to_root()
            sleep(1)
            mount_system_writable()
            sleep(1)
            # start of installing certificate process
            install_lets_encrypt_certs()
            sleep(1)
            reboot_device()
            sleep(1)
            wait_to_complete_reboot_process()
            sleep(1)
            verify_certificates_installation()
            sleep(1)
            # start of installing webview process
            restart_adb_daemon()
            sleep(1)
            get_devices()
            sleep(1)
            change_user_to_root()
            sleep(1)
            mount_system_writable()
            sleep(1)
            install_com_google_android_webview_application()
            sleep(1)
            reboot_device()
            sleep(1)
            wait_to_complete_reboot_process()
            sleep(1)
            change_user_to_root()
            sleep(1)
            mount_system_writable()
            sleep(1)
            verify_package_registered_with_the_package_manager()
            sleep(1)
            replace_framework_res_apk_file()
            sleep(1)
            reboot_device()
            sleep(1)
            wait_to_complete_reboot_process_after_change_framework_res_file()
            sleep(1)

        except Exception as e:
            console.print(e, style="bold black on red")
            sleep(10)
            return
    
    console.print(Panel("All processes were successfully completed. Press any keys to close program...", padding=1, style="bold green"))
    input()

if __name__ == "__main__":
    main()

