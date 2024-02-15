# -*- coding: utf-8 -*-
"""
Created on Tue Sep  3 11:33:42 2019

@author: kuvbur
"""
import os
import convert
import batch_modify
import gdl_gsm


def set_path(path):
    path = os.path.abspath(path)
    if not os.path.exists(path):
        os.makedirs(path, exist_ok=True)
    return os.path.abspath(path)


# =============================================================================
# Имена файлов с параметрами
# =============================================================================
add_file = ['Металлическая Дверь']
dump_file = 'paramdump'
force_conv = True  # Нужно ли конвертировать gsm в xml или брать сразу из папки xml_conv
version = 25
# sourse_param = "Dump"
sourse_param = "GSMFile"
del_param = False
# =============================================================================
# Располагаем исходные файлы в папке 'gsm'
# Промежуточные файлы будут сохранены в папку 'xml'
# Откуда конвертер переводит их формат gsm и копирует в папку 'gdlnew'

curr_dir = "C:\\Users\\kuvbur\\Google Диск\\Share\\pygdl\\CONVERT"
os.chdir(curr_dir)
convert_old_dir = set_path(os.path.join(curr_dir, 'gsm'))
convert_temp_dir = set_path(os.path.join(curr_dir, 'xml'))
convert_new_dir = set_path(os.path.join(curr_dir, 'gsmnew'))
base = batch_modify.get_base()

param = {}
if sourse_param == "GSMFile":
    for from_fname in add_file:
        abs_gsm_from_name = os.path.join(curr_dir, from_fname + ".gsm")
        abs_xml_from_name = os.path.join(curr_dir, from_fname + ".xml")
        if not os.path.isfile(abs_xml_from_name) or force_conv:
            r = convert.gsm2xml(abs_xml_from_name, abs_gsm_from_name, version)
        from_obj = gdl_gsm.gdl_gsm(abs_xml_from_name, base)
        param_from = from_obj.get_param_list()
        for k in param_from.keys():
            try:
                h = param_from[k]['Fix']
            except KeyError:
                param_from[k]['Fix'] = True
            if not param_from[k]['Fix']:
                param[k] = param_from[k]
if sourse_param == "Dump":
    abs_dump_file = os.path.join(curr_dir, dump_file + ".txt")
    param = batch_modify.get_paramdump(abs_dump_file)


if force_conv:
    convert.gsm2xml_batch(convert_temp_dir, convert_old_dir, version)
for root, dirs, files in os.walk(convert_temp_dir):
    for nm in files:
        if nm.find(".xml") > 0:  # Рисунки и текстовые файлы не нужны
            fname_xml = os.path.join(root, nm)  # Полный путь к файлу
            test_obj = gdl_gsm.gdl_gsm(fname_xml, base)
            n_del = 0
            if del_param:
                n_del = test_obj.del_param_dic(param)
            n_err, n_mod, n_new, n_skip = test_obj.set_param_dic(param)
            print('%s - Error : %d, Del : %d, Modify : %d, New : %d, Skip : %d' % (
                nm, n_err, n_del, n_mod, n_new, n_skip))
            test_obj.set_defult_pen()
            test_obj.close()
convert.xml2gsm_batch(convert_temp_dir, convert_new_dir, version)
