# -*- coding: utf-8 -*-
import pathlib
from download_and_unzip import DownloadAndUnzip
import sys
from subprocess import Popen, PIPE, STDOUT, CalledProcessError
import json
import shlex

curr_dir = pathlib.Path(__file__).parent.absolute()


def DownloadLP_XMLConverters(version):
    devKitFolder = curr_dir / 'Tool'
    devKitFolderVersion = devKitFolder / f'LP_XMLConverter{version}'
    if not devKitFolder.exists():
        devKitFolder.mkdir(parents=True)
    if not devKitFolderVersion.exists():
        print(f"Download LP_XMLConverter {version}")
        configPath = devKitFolder / 'config.json'
        configFile = open(configPath, encoding="utf-8")
        configData = json.load(configFile)
        configFile.close()
        DownloadAndUnzip(configData['LP_XMLConverter'][str(version)], devKitFolder)
        if not devKitFolderVersion.exists():
            print(f"ERROR, folder for LP_XMLConverter {version} not exists")
            return ""
    if devKitFolderVersion.exists() and devKitFolder.exists():
        print(f"LP_XMLConverter {version} exist")
        return devKitFolderVersion

def run_shell_command(command_line):
    command_line_args = shlex.split(command_line)
    try:
        command_line_process = Popen(
            command_line_args,
            stdout=PIPE,
            stderr=STDOUT,
        )
        del_txt = os.path.dirname(os.path.normpath(command_line_args[-1]))
        for line in command_line_process.stdout:
            log_txt = line.decode('utf-8', errors='ignore')
            print_flag = True
            for i in ignore_msg:
                if log_txt.find(i)>0:
                    print_flag = False
                    break
            if print_flag:
                log_txt = log_txt.replace(del_txt, '')
                log_txt = log_txt.replace('\n', '')
                log_txt = log_txt.replace('/n', '')
                log_txt = log_txt.replace('\r\n', '')
                print(log_txt)
    except (OSError, CalledProcessError) as exception:
        print('Exception occured: ' + str(exception))
        return False
    else:
        # no exception was raised
        print('Subprocess finished')
    return True

