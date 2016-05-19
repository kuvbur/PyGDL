# -*- coding: utf-8 -*-
from subprocess import Popen, PIPE, STDOUT

def gsm2xml(fname_gsm, fname_xml, version = 16):
    """
    Переводит объект gsm в xml
    """
    path_LP_XMLConverter = set_converter_version(version)
    fname_gsm, fname_xml = get_fname(fname_gsm, fname_xml)
    cmd = '%s%sLP_XMLConverter.exe%s libpart2xml %s %s' % ('"', path_LP_XMLConverter, '"', fname_gsm, fname_xml)
    p = Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE,
            stderr=STDOUT)
    while True:
        s = p.stdout.readline()
        if not s: break
        print (s.decode('cp1251'))

def xml2gsm(fname_gsm, fname_xml, version = 16):
    """
    Переводит объект xml в gsm
    """
    path_LP_XMLConverter = set_converter_version(version)
    fname_gsm, fname_xml = get_fname(fname_gsm, fname_xml)
     
    cmd = '%s%sLP_XMLConverter.exe%s xml2libpart %s %s' % ('"', path_LP_XMLConverter, '"', fname_gsm, fname_xml)
    p = Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE,
            stderr=STDOUT)
    while True:
        s = p.stdout.readline()
        if not s: break
        print (s.decode('cp1251'))

def get_fname(fname_gsm, fname_xml):
    fname_gsm = '"' + fname_gsm + '"'
    fname_xml = '"' + fname_xml + '"'
    return fname_gsm, fname_xml
    
def set_converter_version(version):
    path_16 = 'C:\\Program Files\\GRAPHISOFT\\ArchiCAD 16\\'
    dict_version = {16: path_16}
    path_version = dict_version[version]
    return path_version
