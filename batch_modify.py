import os
import logging
import gdl_gsm

curr_dir = os.path.dirname(os.path.abspath (__file__))
os.chdir (curr_dir)
convert_data_dir = os.path.abspath(os.path.join(curr_dir,'MODYFY_DATA'))
convert_temp_dir = os.path.abspath(os.path.join(curr_dir,'CONVERT','xml'))

add_param_file = os.path.join(convert_data_dir, 'add_param.txt')
del_param_file = os.path.join(convert_data_dir, 'del_param.txt')
log_file = os.path.join(convert_temp_dir, 'convert.log')
logging.basicConfig(filename=log_file, level=logging.INFO)


DataBase_MainGUID_fname = os.path.join(convert_data_dir,'DataBase_MainGUID.csv')
def get_base():
    base = gdl_gsm.database_guid(DataBase_MainGUID_fname)
    return base

def read_code(code_key):
    file = os.path.join(convert_data_dir, 'code_'+ code_key +'.txt')
    with open (file, "r", encoding="utf-8") as f:
        code=f.readlines()
    code = "\n".join(code)
    code = code.replace('\n\n','\n')
    return code

def get_code_dic():
    code_type = ['gen','3d','2d','spec','ui','prm']
    code_dic = {c: read_code(c) for c in code_type}
    return code_dic

def get_param_dic():
    add_param = {}
    nline = 0
    with open(add_param_file) as f:
        for line in f:
            nline += 1
            if nline>1:
                line=line.strip('\n')
                param_name,param_description,param_type,param_value,tparam_Child, tparam_Hidden,tparam_BoldName,tparam_Unique = line.split('\t')
                if len(param_name)>1:
                    add_param[param_name] = {}
                    param_Child = False
                    param_Hidden = False
                    param_BoldName = False
                    param_Unique = False
                    param_Flg = False
                    if tparam_Child == '1' : param_Child = True
                    if tparam_Hidden == '1' : param_Hidden = True
                    if tparam_BoldName == '1' : param_BoldName = True
                    if tparam_Unique == '1' : param_Unique = True
                    if param_Child or param_Hidden or param_BoldName or param_Unique:
                        param_Flg = True
                    add_param[param_name]['Type'] = param_type
                    add_param[param_name]['Description'] = param_description
                    add_param[param_name]['Value'] = param_value
                    add_param[param_name]['ParFlg_Child'] = param_Child
                    add_param[param_name]['ParFlg_Hidden'] = param_Hidden
                    add_param[param_name]['ParFlg_BoldName'] = param_BoldName
                    add_param[param_name]['ParFlg_Unique'] = param_Unique
                    add_param[param_name]['Fix'] = None
                    add_param[param_name]['Flags'] = param_Flg
    return add_param
