# -*- coding: utf-8 -*-
"""
Created on Tue Sep  3 11:33:42 2019

@author: kuvbur
"""
import os

import convert

gsm_file_name = "аорtest.gsm"
version_to = 20

curr_dir = os.path.dirname(os.path.abspath (__file__))
os.chdir (curr_dir)
abs_gsm_file_name = convert.get_fname_gsm(gsm_file_name)
version_gsm, rezult = convert.get_version_gsm(abs_gsm_file_name)
if rezult:
    print('Версия файла - %d' % (version_gsm))
    fname_gsm_to = convert.convert_gsm(version_to, abs_gsm_file_name)
    assert os.path.isfile(fname_gsm_to)
#if len(fname_gsm_to):
#    version_gsm, rezult = convert.get_version_gsm(fname_gsm_to)
#    print(version_gsm, rezult)
#convert.finalizexml(os.path.abspath(os.path.join(curr_dir,'CONVERT','xml')),os.path.abspath(os.path.join(curr_dir,'CONVERT','gsm_out')),version_to, reportlevel=1, verbosityLevel=2)
else:
    print("Неизвестная версия")

