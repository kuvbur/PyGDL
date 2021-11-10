# -*- coding: utf-8 -*-
import os
import sys
from subprocess import Popen, PIPE, STDOUT, CalledProcessError
import shlex
import logging

curr_dir = os.path.dirname(os.path.abspath(__file__))
convert_dir = os.path.abspath(os.path.join(curr_dir, 'CONVERT'))
dict_version = {19: "35", 20: "36", 21: "37", 22: "38", 24: "41", 25: "43"}
inv_dict_version = {v: k for k, v in dict_version.items()}

# https://www.graphisoft.com/ftp/techsupport/documentation/developer_docs/AC_11/APIDevKit/LPXML%20Documentation/LP_XMLConverter.html
log_file = os.path.join(curr_dir, 'convert_test.log')
logging.basicConfig(filename=log_file, level=logging.DEBUG)
ignore_msg = ['error: Missing ancestor with main GUID',
              'The libpart has unused parameters',
              'Compile ...',
              'error: Missing called macro or file',
              'Revert ...',
              'Update ... ',
              'warning: Macro may be unused',
              'error: Missing macro']

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
        logging.info('Exception occured: ' + str(exception))
        logging.info('Subprocess failed')
        return False
    else:
        # no exception was raised
        logging.info('Subprocess finished')
    return True


def getconverter(version):
    path_LP_XMLConverter = os.path.abspath(
        os.path.join(curr_dir, 'LP_XMLConverter' + str(version), 'LP_XMLConverter.exe'))
    path_LP_XMLConverter = '"' + path_LP_XMLConverter + '"'
    return path_LP_XMLConverter


def xml2gsm_batch(fpath_xml, fpath_gsm, version):
    """
    Проверяет ошибки, обновляет вкладки параметров
    """
    fpath_xml = '"' + str(fpath_xml) + '"'
    fpath_gsm = '"' + str(fpath_gsm) + '"'
    path_LP_XMLConverter = getconverter(version)
    cmd_body = '%s makelibrary -l UTF8 -reportlevel 2 -checkparams' % path_LP_XMLConverter
    cmd = '%s %s %s' % (cmd_body, fpath_xml, fpath_gsm)
    rezult = run_shell_command(cmd)
    return rezult


def gsm2xml(fname_xml, fname_gsm, version):
    """
    Переводит объект gsm в xml
    """
    fname_gsm = '"' + str(fname_gsm) + '"'
    fname_xml = '"' + str(fname_xml) + '"'
    path_LP_XMLConverter = getconverter(version)
    cmd = '%s libpart2xml -l UTF8 %s %s' % (path_LP_XMLConverter, fname_gsm, fname_xml)
    rezult = run_shell_command(cmd)
    return rezult


def gsm2xml_batch(path_xml, path_gsm, version):
    """
    Переводит папку объектов gsm в xml
    """
    path_gsm = '"' + path_gsm + '"'
    path_xml = '"' + path_xml + '"'
    path_LP_XMLConverter = getconverter(version)
    cmd = u'%s l2x %s %s' % (path_LP_XMLConverter, path_gsm, path_xml)
    rezult = run_shell_command(cmd)
    return rezult


def xml2gsm(fname_xml, fname_gsm, version):
    """
    Переводит объект xml в gsm
    """
    fname_gsm = '"' + fname_gsm + '"'
    fname_xml = '"' + fname_xml + '"'
    path_LP_XMLConverter = getconverter(version)
    cmd = '%s xml2libpart -l UTF8 %s %s' % (path_LP_XMLConverter, fname_xml, fname_gsm)
    rezult = run_shell_command(cmd)
    return rezult


def repair_xml(version, text):
    repair_text = text
    if version < 20:
        repair_text = repair_text.replace('="false"', '="no"')
        repair_text = repair_text.replace('="true"', '="yes"')
        repair_text = repair_text.replace('>false<', '>no<')
        repair_text = repair_text.replace('>true<', '>yes<')
    return repair_text


def convert_gsm(version_to, fname, version_from=None, save_gsm=True):
    fname_gsm_from = fname
    fname_path = os.path.dirname(fname).decode('utf-8')
    fname = os.path.basename(fname).decode('utf-8')
    fname = fname.split('.')[0]
    if version_from == None: version_from, rez = get_version_gsm(fname_gsm_from)
    fname_gsm_to = os.path.join(fname_path, fname + "_" + str(version_to) + ".gsm")
    fname_xml = os.path.join(fname_path, fname + "_" + str(version_to) + ".xml")
    gsm2xml(fname_xml, fname_gsm_from, version_from)
    with open(os.path.join(convert_dir, 'xml', fname_xml), encoding="utf-8") as file_in:
        text = file_in.read()
    if version_to in dict_version.keys() and version_from in dict_version.keys():
        txt_version_from = 'Version="' + dict_version[version_from] + '">'
        txt_version_to = 'Version="' + dict_version[version_to] + '">'
        text = text.replace(txt_version_from, txt_version_to)
        text = repair_xml(version_to, text)
        with open(os.path.join(convert_dir, 'xml', fname_xml), "w", encoding="utf-8") as file_out:
            file_out.write(text)
        if save_gsm: xml2gsm(fname_xml, fname_gsm_to, version_to)
    else:
        logging.error('Неизвестная версия %d -> %d' % (version_from, version_to))
        fname_gsm_to = ""
    return fname_gsm_to


def get_version_gsm(fname_gsm):
    with open(fname_gsm, 'rb') as f:
        hexdata = f.read().hex()
    txt_version = str(int(hexdata[4:6], 16))
    version = ""
    try:
        version = inv_dict_version[txt_version]
    except KeyError as e:
        logging.error(e)
        version = txt_version
        rezult = False
    else:
        rezult = True
    return version, rezult


# if __name__ == "__main__":
#     os.chdir(curr_dir)
#     version_gsm, rezult = get_version_gsm(get_fname_gsm("Перемычки .gsm"))
#     print(version_gsm, rezult)
# #    fname_gsm_to = convert_gsm(19, "test_19")
#
#
# #    if len(fname_gsm_to):
# #        version_gsm, rezult = get_version_gsm(fname_gsm_to)
# #        print(version_gsm, rezult)
# #    finalizexml(os.path.abspath(os.path.join(curr_dir,'CONVERT','xml')),os.path.abspath(os.path.join(curr_dir,'CONVERT','gsm_out')),19, reportlevel=1, verbosityLevel=2)
