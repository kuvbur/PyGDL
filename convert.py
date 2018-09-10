# -*- coding: utf-8 -*-
import os
from subprocess import Popen, PIPE, STDOUT

def gsm2xml(fname_gsm, fname_xml,version):
    """
    Переводит объект gsm в xml
    """
    fname_gsm, fname_xml = get_fname(fname_gsm, fname_xml)
    path_LP_XMLConverter = os.path.abspath(os.path.join(curr_dir,'LP_XMLConverter'+str(version),'LP_XMLConverter.exe'))
    cmd = '%s%s%s libpart2xml %s %s' % ('"', path_LP_XMLConverter, '"', fname_gsm, fname_xml)
    p = Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE,
            stderr=STDOUT)
    while True:
        s = p.stdout.readline()
        if not s: break
        print (s)

def xml2gsm(fname_gsm, fname_xml,version):
    """
    Переводит объект xml в gsm
    """
    fname_gsm, fname_xml = get_fname(fname_gsm, fname_xml)
    path_LP_XMLConverter = os.path.abspath(os.path.join(curr_dir,'LP_XMLConverter'+str(version),'LP_XMLConverter.exe'))
    cmd = '%s%s%s xml2libpart -l UTF8 %s %s' % ('"', path_LP_XMLConverter, '"', fname_xml, fname_gsm)
    p = Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE,
            stderr=STDOUT)
    while True:
        s = p.stdout.readline()
        if not s: break
        print (s)

def get_fname(fname_gsm, fname_xml):
    fname_gsm = '"' + os.path.join(convert_dir,'gsm', fname_gsm) + '"'
    fname_xml = '"' + os.path.join(convert_dir,'xml', fname_xml) + '"'
    return fname_gsm, fname_xml

def convert_gsm(version_from, version_to, fname):
    dict_version = {21:"37", 20 : "36"}
    fname_gsm_from = fname + ".gsm"
    fname_xml = fname + ".xml"
    fname_gsm_to = fname +"_" + str(version_to) + ".gsm"
    gsm2xml(fname_gsm_from, fname_xml, version_from)
    with open(os.path.join(convert_dir,'xml', fname_xml)) as file_in:
        text = file_in.read()
    txt_version_from='Version="' + dict_version[version_from] + '">'
    txt_version_to='Version="' + dict_version[version_to] + '">'    
    text = text.replace(txt_version_from, txt_version_to)
    with open(os.path.join(convert_dir,'xml', fname_xml), "w") as file_out:
        file_out.write(text)
    xml2gsm(fname_gsm_to, fname_xml, version_to)

curr_dir = os.path.dirname(os.path.abspath (__file__))
convert_dir = os.path.abspath(os.path.join(curr_dir,'CONVERT'))
os.chdir (curr_dir)
convert_gsm(21, 20, "test")