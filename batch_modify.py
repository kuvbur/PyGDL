import os
import convert
import gdl_gsm
import logging

curr_dir = os.path.dirname(os.path.abspath (__file__))
os.chdir (curr_dir)
convert_data_dir = os.path.abspath(os.path.join(curr_dir,'MODYFY_DATA'))
convert_temp_dir = os.path.abspath(os.path.join(curr_dir,'CONVERT','xml'))

add_param_file = os.path.join(convert_data_dir, 'add_param.txt')
del_param_file = os.path.join(convert_data_dir, 'del_param.txt')
log_file = os.path.join(convert_temp_dir, 'convert.log')
logging.basicConfig(filename=log_file, level=logging.INFO)

convert_old_dir = os.path.abspath(os.path.join(curr_dir,'CONVERT','gsm'))
convert_new_dir = os.path.abspath(os.path.join(curr_dir,'CONVERT','gsm_out'))
DataBase_MainGUID_fname = os.path.join(convert_data_dir,'DataBase_MainGUID.csv')
def read_code(code_key):
    file = os.path.join(convert_data_dir, 'code_'+ code_key +'.txt')
    with open (file, "r", encoding="utf-8") as f:
        code=f.readlines()
    code = "\n".join(code)
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
                param_name,param_description,param_type,param_value,param_Child, param_Hidden,param_BoldName,param_Unique = line.split('\t')
                if len(param_name)>1:
                    add_param[param_name] = {}
                    add_param[param_name]['Type'] = param_type
                    add_param[param_name]['Description'] = str(param_description)
                    add_param[param_name]['Value'] = str(param_value)
                    add_param[param_name]['ParFlg_Child'] = bool(param_Child)
                    add_param[param_name]['ParFlg_Hidden'] = bool(param_Hidden)
                    add_param[param_name]['ParFlg_BoldName'] = bool(param_BoldName)
                    add_param[param_name]['ParFlg_Unique'] = bool(param_Unique)
                    add_param[param_name]['Fix'] = None
                    if param_Child or param_Hidden or param_BoldName or param_Unique:
                        param_Flg = True
                    else:
                        param_Flg = False
                    add_param[param_name]['Flags'] = param_Flg
    return add_param
code_dic = get_code_dic()
param_dic = get_param_dic()
base = gdl_gsm.database_guid(DataBase_MainGUID_fname)

convert.gsm2xml_batch(convert_temp_dir, convert_old_dir, 20)
for root, dirs, files in os.walk(convert_temp_dir):
    for nm in files:       
        if nm.find(".xml")>0:
            fname_xml = os.path.join(root, nm)
            test_obj = gdl_gsm.gdl_gsm(fname_xml, base)
            mid, name = test_obj.get_type()
            if name.find("Элемент Модели")==-1:
                test_obj.set_param_dic(param_dic)
                test_obj.addcode_dic(code_dic)
                test_obj.close()
                print(nm)
convert.finalizexml(convert_temp_dir,convert_new_dir,20, reportlevel=2, verbosityLevel=2)