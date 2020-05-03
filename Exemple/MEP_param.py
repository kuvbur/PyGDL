# -*- coding: utf-8 -*-
import os
import batch_modify
import convert
import gdl_gsm

# =============================================================================
# Словари с добавляемым кодом, данными о параметрах и база подтипов
# =============================================================================
code_dic = batch_modify.get_code_dic()
param_dic = batch_modify.get_param_dic()
base = batch_modify.get_base() #База с именами подтипов

# =============================================================================
# Пути к объектам и временной папке
# =============================================================================
curr_dir = os.path.dirname(os.path.dirname(os.path.abspath (__file__)))
convert_temp_dir = os.path.abspath(os.path.join(curr_dir,'CONVERT','xml','Окна'))
convert_old_dir = os.path.abspath(os.path.join(curr_dir,'CONVERT','gsm','Окна'))
convert_new_dir = os.path.abspath(os.path.join(curr_dir,'CONVERT','gsm_out','Окна'))

el_add = ["Сегмент", "Фитинг", "Сочленения"]

#Конвертируем gsm в xml
convert.gsm2xml_batch(convert_temp_dir, convert_old_dir, 22)
for root, dirs, files in os.walk(convert_temp_dir):
    for nm in files:
        if nm.find(".xml")>0: #Рисунки и текстовые файлы не нужны
            fname_xml = os.path.join(root, nm) #Полный путь к файлу
            test_obj = gdl_gsm.gdl_gsm(fname_xml, base) #Экземпляр gsm объекта
            mid = test_obj.get_An_MainGUID()
            test_obj.set_param_dic(param_dic)
            test_obj.close()
            # flag_add = True
#            for n in el_add:
#                if name.find(n)!=-1:  flag_add = True
#             if name.find("Элемент Модели")==-1 and flag_add == True:
#                 test_obj.set_param_dic(param_dic) #Добавили параметры
# #                test_obj.addcode_dic(code_dic) #Добавили код
#                 test_obj.close() #Закрыли с сохранением xml
#                 print(nm)
# #Конвертируем обратно в gsm с проеркой с записью отчёта в файл convert_test.log)
convert.finalizexml(convert_temp_dir,convert_new_dir,22, reportlevel=2, verbosityLevel=2)