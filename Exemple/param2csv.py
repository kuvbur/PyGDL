# -*- coding: utf-8 -*-
"""
Created on Tue Sep  3 11:33:42 2019

@author: kuvbur
"""
import os
import convert
import batch_modify
import gdl_gsm
import csv
from shutil import copy
import subprocess


force_conv = True

# =============================================================================
# Имена файлов с параметрами
# =============================================================================
add_file = ['Жб обрамление проёма', 'Перемычки', 'Параметры окна']

# =============================================================================
curr_dir = os.path.dirname(os.path.dirname(os.path.abspath (__file__)))
convert_temp_dir = os.path.abspath(os.path.join(curr_dir,'CONVERT','xml'))
convert_old_dir = os.path.abspath(os.path.join(curr_dir,'CONVERT','gsm'))
convert_new_dir = os.path.abspath(os.path.join(curr_dir,'CONVERT','gsm_out'))
base = batch_modify.get_base() #База с именами подтипов
# code_dic = batch_modify.get_code_dic()

param = {}
for from_fname in add_file:
    abs_gsm_from_name = convert.get_fname_gsm(from_fname+".gsm")
    abs_xml_from_name = convert.get_fname_xml(from_fname+".xml")
    if os.path.isfile(abs_xml_from_name)==False or force_conv: 
        r =convert.gsm2xml(abs_xml_from_name,abs_gsm_from_name,22)
    from_obj = gdl_gsm.gdl_gsm(abs_xml_from_name, base)
    param_from = from_obj.get_param_list()
    for k in param_from.keys():
        try:
            h = param_from[k]['Fix']
        except KeyError:
            param_from[k]['Fix'] = True
        if param_from[k]['Fix'] == False:
            param[k] = param_from[k]

# f_name = os.path.join('Окна','Параметры окна')
# abs_gsm_name = convert.get_fname_gsm(f_name+".gsm")
# abs_xml_name = convert.get_fname_xml(f_name+".xml")
# if os.path.isfile(abs_xml_name)==False or force_conv:
#     convert.gsm2xml(abs_xml_name,abs_gsm_name,22)
# test_obj = gdl_gsm.gdl_gsm(abs_xml_name, base)
# test_obj.set_param_dic(param)
# test_obj.close()
# test_obj = gdl_gsm.gdl_gsm(abs_xml_name, base)

convert_temp_dir = os.path.abspath(os.path.join(curr_dir,'CONVERT','xml','conv'))
convert_old_dir = os.path.abspath(os.path.join(curr_dir,'CONVERT','gsm','conv'))
convert.gsm2xml_batch(convert_temp_dir, convert_old_dir, 22)
for root, dirs, files in os.walk(convert_temp_dir):
    for nm in files:
        if nm.find(".xml")>0: #Рисунки и текстовые файлы не нужны
            fname_xml = os.path.join(root, nm) #Полный путь к файлу
            test_obj = gdl_gsm.gdl_gsm(fname_xml, base)
            test_obj.set_param_dic(param)
            test_obj.close()
            copy(fname_xml, "D:\\xml")
if os.path.isfile('D:\\gdl_log.txt'):
    os.remove('D:\\gdl_log.txt')  
p = subprocess.Popen("D:\\2gdl.bat", shell=True, stdout = subprocess.PIPE)
stdout, stderr = p.communicate()

