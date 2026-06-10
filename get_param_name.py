import os
import gdl_gsm
import os
import convert
import batch_modify
import gdl_gsm
from settings import *
import asyncio
import json
force_conv = False
from_fname = "Nummerierung POLY Line_mod"



def set_path(path):
    path = os.path.abspath(path)
    if not os.path.exists(path):
        os.makedirs(path, exist_ok=True)
    return os.path.abspath(path)

curr_dir = "C:\\Users\\kuvbur\\YandexDisk\\Работа\\PyGDL\\CONVERT"
os.chdir(curr_dir)
convert_old_dir = set_path(os.path.join(curr_dir, 'gsm'))
convert_temp_dir = set_path(os.path.join(curr_dir, 'xml'))
convert_new_dir = set_path(os.path.join(curr_dir, 'gsmnew'))
base = batch_modify.get_base()

abs_gsm_from_name = os.path.join(convert_old_dir, from_fname + ".gsm")
abs_xml_from_name = os.path.join(convert_temp_dir, from_fname + ".xml")
if not os.path.isfile(abs_xml_from_name) or force_conv:
    r = convert.gsm2xml(abs_xml_from_name, abs_gsm_from_name, 25)
from_obj = gdl_gsm.gdl_gsm(abs_xml_from_name, base)
param_from = from_obj.get_param_list()



async def get_translate_param(param_from):
    MPROMPT = """Мы переводим наименования параметров GDL объекта Archicad на русский язык.
    Используй понятные общепринятые термины. В ответ пришли только перевод, сохраняя исходную структуру и форматирование.
    Не пиши ничего дополнительно. Не сопровождай текстовыми комментариями. """
    prompt = ""
    param_name = {}
    param_inx = {}
    for k, v in param_from.items():
        if 'List' in v:
            for n in v['List']:
                if n not in param_name and len(n)>2:
                    param_name[n]= str(len(param_name)+1)+" : " + n
                    param_inx[len(param_name)] = n
        else:
            n = v['Description']
            if n not in param_name and len(n)>2:
                param_name[n]= str(len(param_name)+1)+" : " + n
                param_inx[len(param_name)] = n
    prompt = " , ".join(list(param_name.values()))
    response = await ask_openrouter(prompt, MPROMPT)
    response.replace('\n', '')
    namelist = response.split(',')
    assert(len(namelist)==len(param_name))
    for n in namelist:
        name = n.split(':')[1].replace('"', '').strip()
        inx = int(n.split(':')[0].replace('"', '').strip())
        k = param_inx[inx]
        param_name[k] = name
    
    
    for k, v in param_from.items():
        if 'List' in v:
            for i, n in enumerate(v['List']):
                if n in param_name:
                    param_from[k]['List'][i] = param_name[n]
        else:
            n = v['Description']
            if n in param_name:
                param_from[k]['Description'] = param_name[n]
    return param_from

param_dict_translate = asyncio.run(get_translate_param(param_from))
n_err, n_mod, n_new, n_skip = from_obj.set_param_dic(param_dict_translate)
from_obj.close()
convert.xml2gsm_batch(convert_temp_dir, convert_new_dir, 25)