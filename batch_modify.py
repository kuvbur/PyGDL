import os
import logging
import gdl_gsm

curr_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(curr_dir)
convert_data_dir = os.path.abspath(os.path.join(curr_dir, 'MODYFY_DATA'))
convert_temp_dir = os.path.abspath(os.path.join(curr_dir, 'CONVERT', 'xml'))

log_file = os.path.join(convert_temp_dir, 'convert.log')
logging.basicConfig(filename=log_file, level=logging.INFO)


DataBase_MainGUID_fname = os.path.join(
    convert_data_dir, 'DataBase_MainGUID.csv')


def get_base():
    base = gdl_gsm.database_guid(DataBase_MainGUID_fname)
    return base


def read_code(code_key):
    file = os.path.join(convert_data_dir, 'code_' + code_key + '.txt')
    with open(file, "r", encoding="utf-8") as f:
        code = f.readlines()
    code = "\n".join(code)
    code = code.replace('\n\n', '\n')
    return code


def get_code_dic():
    code_type = ['gen', '3d', '2d', 'spec', 'ui', 'prm']
    code_dic = {c: read_code(c) for c in code_type}
    return code_dic


def get_param_dic(add_param_file):
    add_param = {}
    nline = 0
    with open(add_param_file) as f:
        for line in f:
            nline += 1
            if nline > 1:
                line = line.strip('\n')
                param_name, param_description, param_type, param_value, tparam_Child, tparam_Hidden, tparam_BoldName, tparam_Unique = line.split(
                    '\t')
                if len(param_name) > 1:
                    add_param[param_name] = {}
                    param_Child = False
                    param_Hidden = False
                    param_BoldName = False
                    param_Unique = False
                    param_Flg = False
                    if tparam_Child == '1':
                        param_Child = True
                    if tparam_Hidden == '1':
                        param_Hidden = True
                    if tparam_BoldName == '1':
                        param_BoldName = True
                    if tparam_Unique == '1':
                        param_Unique = True
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


def get_paramdump(add_param_file):
    parametrs = {}
    start_array = False
    with open(add_param_file, "r") as f:
        for line in f:
            if '0x' in line or '[' in line:
                params = line.strip('\t').strip('\n').strip().split('\t')
                if start_array and '0x' in line:
                    parametrs[name] = {}
                    parametrs[name]['Type'] = type_param
                    parametrs[name]['Description'] = description
                    parametrs[name]['Value'] = value
                    parametrs[name]['ParFlg_Child'] = False
                    parametrs[name]['ParFlg_Hidden'] = False
                    parametrs[name]['ParFlg_BoldName'] = False
                    parametrs[name]['ParFlg_Unique'] = False
                    parametrs[name]['Fix'] = None
                    parametrs[name]['Flags'] = False
                    parametrs[name]['Array'] = (nrow, ncol)
                    start_array = False

                if 'dim [' in line:
                    name = params[0].split(' ')[0].strip()
                    type_param = params[0].split('(')[1].strip(')')
                    array = params[1].split(']')
                    nrow = int(array[0].strip('dim ['))
                    value = []
                    description = []
                    if len(array) == 3:
                        ncol = int(array[1].strip('['))
                        for i in range(0, nrow):
                            value.append([0 for i in range(0, ncol)])
                            description.append([0 for i in range(0, ncol)])
                    else:
                        ncol = 0
                        value = [0 for i in range(0, nrow)]
                        description = [0 for i in range(0, nrow)]
                    start_array = True

                if start_array and '0x' not in line:
                    array = params[0].split(']')
                    row = int(array[0].strip('['))-1
                    val = params[1].strip('"')
                    if len(array) == 3:
                        col = int(array[1].strip('['))-1
                        value[row][col] = val
                        if type_param != 'String':
                            description[row][col] = params[4].strip('"')
                    else:
                        col = 0
                        value[row] = val
                        if type_param != 'String':
                            description[row] = params[4].strip('"')

                if not start_array and '0x' in line:
                    name = params[0].split(' ')[0].strip()
                    type_param = params[0].split('(')[1].strip(')')
                    value = params[2].strip('"').strip("'")
                    description = ''
                    if type_param != 'String':
                        description = params[5].strip('"').strip("'")
                    parametrs[name] = {}
                    parametrs[name]['Type'] = type_param
                    parametrs[name]['Description'] = description
                    parametrs[name]['Value'] = value
                    parametrs[name]['ParFlg_Child'] = False
                    parametrs[name]['ParFlg_Hidden'] = False
                    parametrs[name]['ParFlg_BoldName'] = False
                    parametrs[name]['ParFlg_Unique'] = False
                    parametrs[name]['Fix'] = None
                    parametrs[name]['Flags'] = False
                    parametrs[name]['Array'] = None
    return parametrs
