## Installation Process

1. Install all the packages listed in `requirements.txt`.
2. Install `pyadb` by running the command `pip install pyadb`.
3. The installed version of `pyadb` is outdated, so replace the files in `pyadb-container/pyadb/pyadb` with the corresponding files in the installed package.
4. Run `python setup.py install`.
5. Use Inno Setup to package all the files in the `dist` folder.
6. Install Inno Setup software. used version: 6.3.3 . [download page](https://jrsoftware.org/isdl.php) | [download link1](https://jrsoftware.org/download.php/is.exe?site=1) | [download link2](https://jrsoftware.org/download.php/is.exe?site=2) .
7. Run Inno Setup using the `script.iss` file located in `dist/inno_setup_output/script.iss`.
8. Now, the `Artiman Smart-Tablet Updater.exe` is ready for distribution and located in `dist/inno_setup_output/` folder.

## Tips:

1. The following variables must match:

        - The "application_name" variable in `application.py`
        - "MyAppName" in the `script.iss` file
        ------------------------------------------------------
        - "MyAppExeName" in the `script.iss` file
        - "dest_base" in `setup.py`

2. If you use the installation directory (e.g., `ProgramFiles/application_name/`) for locating static files and folders, you won't be able to write to this directory due to permission restrictions. Instead, use the `AppData/Local` directory for files and folders that need write access.

3. To run the application locally, use the `application_can_run_locally.py` file. Simply activate the virtual environment and run it with the command `python application_can_run_locally.py`.

4. PyInstaller cannot create an executable for the application when using the `rich` library. After extensive testing, I couldn't resolve this issue. Instead, I used the `py2exe` library, which is older than PyInstaller but worked for this project.

5. The `application.spec` file can be used with the PyInstaller library, but it is not compatible with `py2exe`. I’ve left it here in case it's needed for future projects as a starting point.

6. In inno setup application `{localappdata}` refers to `C:\Users\<YourUsername>\AppData\Local`
7. In inno setup application `{app}` refers to `C:\Program Files\application_name`
8. if inno setup we have:
>```
>[Files]
>Source:
> "D:\artimanproject\artiman_smart_home_management_system\Tablet_webApplication_fixture_application\dist\resources\*"; DestDir: "{localappdata}\{#MyAppName}\resources"; Flags: ignoreversion recursesubdirs createallsubdirs
> ```
> ### Explanation:
> - **Source:** The directory where your files are located (`D:\artimanproject\...`).
> - **DestDir:** This is the target directory. Here, `{localappdata}` refers to `C:\Users\<YourUsername>\AppData\Local`. You can add subdirectories like `MyApplication\lib` to organize your files.
> - **Flags:**
> - `ignoreversion`: Allows overwriting files regardless of version numbers.
> - `recursesubdirs`: Recursively copies all subdirectories in the source folder.
> - `createallsubdirs`: Ensures all subdirectories are created in the destination folder.
> ### Customize Application Subfolder
> You can change `MyApplication` to any name you prefer for your app. This will create a folder under `AppData\Local` specifically for your application's files.
> This setup will copy all the contents from your source folder (`dist/lib`) to the `C:\Users\<YourUsername>\AppData\Local\MyApplication\lib` directory, maintaining the subdirectory structure.   
> 

## Application Obfuscation:
- I didn't use the obfuscated version of `application.py` file and use the original one for making exe file. you know i think it is not neccessary for this project but i put some link in the end of this file to be reference of other projects.


## useful links:


1. Create Cert file and put it in android:

    - [link1](https://splitunknown.medium.com/importing-a-certificate-and-installing-it-on-android-67867b8dcd80)
    - [link2](https://gist.github.com/pwlin/8a0d01e6428b7a96e2eb)
    - [link3](https://github.com/ProxymanApp/Proxyman/issues/2121)
    - [link4](https://github.com/ProxymanApp/Proxyman/issues/2121)
    - [link5](https://github.com/Magisk-Modules-Repo/movecert/blob/master/common/post-fs-data.sh)
    - [link6](https://gist.github.com/pwlin/8a0d01e6428b7a96e2eb?permalink_comment_id=4829387#gistcomment-4829387)
    - [adguardcert- can be use for all rooted android version to install custom certs(i don't use it in this project)](https://github.com/AdguardTeam/adguardcert)


2. modify android 7 below file systems to set new webview application as main one
    #### Installation process:
    - Windows
        > info   
        As Windows is case-insensitive please adjust case sensitivity for correct operation.

        1. Download the Windows [wrapper script](https://raw.githubusercontent.com/iBotPeaches/Apktool/master/scripts/windows/apktool.bat). (Right click, Save Link As apktool.bat)
        2. Download the latest version of Apktool.
        3. Rename downloaded jar to apktool.jar.
        4. Move both apktool.jar and apktool.bat to your Windows directory. (Usually C://Windows)
        5. If you do not have access to C://Windows, you can place the two files anywhere and add that directory to your Environment Variables System PATH variable.
        6. Try running apktool via the command prompt.
        - I put files in `apktool` folder and run `apktool.bat` file in same directory in `cmd` and didn't use Environment Variables like mention up.
    
    - I use apktool version 2.3.0 and not newer one(2.10.0) because newer one not work properly and when i put framework-res.apk 
    to android system directory, OS can't boot correctly and freeze in `loading...` step, but older one can decompile and recompile correct apk. 
     
    - [Whole process we need to change android default webview application(using adb and apktool application)](https://android.stackexchange.com/questions/139413/android-system-webview-installed-but-not-used-by-apps)
    - [apktool doc](https://apktool.org/docs/install)
    - [download link](https://github.com/iBotPeaches/Apktool/releases/download/v2.3.0/apktool_2.3.0.jar)


3.linux head and tail command equivalent in windows:
    - [link](https://www.shellhacks.com/windows-powershell-tail-head-equivalents/)

4. py2exe useful links:
    - [working with data_files option](http://www.py2exe.org/index.cgi/data_files)
    - [py2exe options](http://www.py2exe.org/index.cgi/ListOfOptions) 
    - [py2exe official tutorial](www.py2exe.org/index.cgi/Tutorial)
    - [py2exe create single file executable like --onefile in pyinstaller](https://stackoverflow.com/questions/112698/py2exe-generate-single-executable-file)
    - []()
    ### tips:
    In the `py2exe` tutorial, we see the use of `from distutils.core import setup` in the `setup.py` file. However, after some research, I found that it is outdated and has been replaced by `from py2exe import freeze`.

5. Let's Encrypt chain of trust:
    - [link](https://letsencrypt.org/certificates/)
6. python code obfuscator:
    - [pyobfuscate.com](https://pyobfuscate.com/pyd)
    - [reecodingtools.org - py-obfuscator](https://freecodingtools.org/py-obfuscator)
    - [pyob.oxyry.com](https://pyob.oxyry.com/)
7. some python tips:
    - [glob tutorial](https://www.geeksforgeeks.org/how-to-use-glob-function-to-find-files-recursively-in-python/)

8. Openssl:
    - We can use openssl application from multiple source:
        - Windows github cli
            - by installing github in windows, we can use `github bash` commandline terminal
             or `C:\Program Files\Git\usr\bin\openssl.exe` to use openssl software.
        - By downloading ICS library zi file, we can access to openssl by running openssl.exe file in `ICS-OpenSSL`.
            - [ICS download link](https://wiki.overbyte.eu/arch/icsv93.zip)
---