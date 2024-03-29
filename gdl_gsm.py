# -*- coding: utf-8 -*-
import os
from datetime import datetime
from lxml import etree
import convert
import csv

curr_dir = os.path.dirname(os.path.abspath(__file__))
convert_data_dir = os.path.abspath(os.path.join(curr_dir, 'MODYFY_DATA'))
DataBase_mainguid_fname = os.path.join(
    convert_data_dir, 'DataBase_mainguid.csv')


def indent(elem, level=0):
    i = "\n" + level * "  "
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + "  "
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
        for elem in elem:
            indent(elem, level + 1)
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = i


class database_guid(object):
    def __init__(self, fname_base):
        self.fname_base = fname_base
        self.mainguid = {}
        self.objname = {}
        self.level = {}
        self.read()

    def write(self):
        with open(self.fname_base, 'w', newline='') as csv_file:
            writer = csv.writer(csv_file, delimiter=';')
            for mainguid, objname in self.mainguid.items():
                try:
                    level = self.level[mainguid]
                except KeyError:
                    level = 0
                writer.writerow([mainguid, objname, level])
        self.read()

    def read(self):
        data_base_main_guid = {}
        data_base_level = {}
        with open(self.fname_base) as csv_file:
            reader = csv.reader(csv_file, delimiter=';')
            for row in reader:
                mid, name, level = row
                mid = mid.strip()
                if len(mid) > 0 and len(name) > 0:
                    data_base_main_guid[mid] = str(name)
                    data_base_level[mid] = int(level)
        self.mainguid = data_base_main_guid
        self.level = data_base_level
        self.inv()
        return data_base_main_guid

    def inv(self):
        self.objname = {v: k for k, v in self.mainguid.items()}

    def add(self, newmainguid):
        add_flag = 0
        if type(newmainguid) is list:
            newmainguid = dict(enumerate(newmainguid))
        if type(newmainguid) is str:
            newmainguid = {"???": newmainguid}
        for name, mid in newmainguid.items():
            try:
                name = self.mainguid[mid]
            except KeyError:
                self.mainguid[mid] = name
                add_flag = add_flag + 1
        if add_flag:
            self.write()
            self.read()
        return add_flag


class gdl_gsm(object):
    def __init__(self, fname_xml, base_id, fname_gsm=None, fname_template=None):
        self.mainguid = 0
        if fname_template is None:
            fname_template = fname_xml
        self.defult_value = {'Length': '0', 'Boolean': '0', 'String': '', 'Angle': '0', 'Title': '', 'Integer': '0',
                             'LineType': '1', 'PenColor': '1', 'FillPattern': '1', 'Material': '1', 'RealNum': '0',
                             'Profile': '0', 'BuildingMaterial': '0', 'Dictionary': None}
        self.valid_type_param = list(self.defult_value.keys())
        self.mode_dic = {'gen': 'Script_1D', '3d': 'Script_3D', '2d': 'Script_2D',
                         'spec': 'Script_PR', 'ui': 'Script_UI', 'prm': 'Script_VL',
                         'mig': 'Script_FWM', 'rmig': 'Script_BWM', 'com': 'Comment',
                         'key': 'Keywords'}
        self.fname_gsm = fname_gsm
        self.fname_xml = fname_xml
        self.base_id = base_id
        self._get_(fname_template)
        self.code_add = {c: [] for c in self.mode_dic.keys()}

    def _get_(self, fname_template):
        parser = etree.XMLParser(strip_cdata=False)
        self.root = etree.parse(fname_template, parser)
        self.croot = self.root.getroot()
        self.parameters = self.get_param_list()
        self.list_mainguid = self.get_an_mainguid()
        self.mainguid = self.get_mainguid()
        self.istemplate = self.get_Template()
        self.isplaceable = self.get_Placeable()
        self.version = self.get_Version()

    def get_an_mainguid(self):
        list_list_main_guid = []
        an = self.croot.find('Ancestry')
        for child in an:
            list_list_main_guid.append(child.text)
            self.base_id.add(child.text)
        return list_list_main_guid

    def get_type(self):
        mainguid = None
        name = None
        level = 0
        t_level = 0
        for mid in self.get_an_mainguid():
            if mid in self.base_id.level:
                t_level = self.base_id.level[mid]
            else:
                self.base_id.add(mid)
            if t_level > level:
                level = self.base_id.level[mid]
                mainguid = mid
        if level > 0:
            name = self.base_id.mainguid[mainguid]
        return mainguid, name

    def set_an_mainguid(self, list_mainguid):
        an = self.croot.find('Ancestry')
        ex_mainguid = []
        add_id = 0
        del_id = 0
        for child in an:
            if not (child.text in list_mainguid):
                an.remove(child)
                del_id = del_id - 1
            else:
                ex_mainguid.append(child.text)
        for mainguid in list_mainguid:
            if not (mainguid in ex_mainguid):
                MGUID = etree.SubElement(an, "mainguid")
                MGUID.text = mainguid
                add_id = add_id + 1
        self.list_mainguid = self.get_an_mainguid()
        return add_id, del_id

    def get_Template(self):
        istemplate = self.croot.get('IsArchivable')
        return istemplate

    def set_Template(self, newIstemplate):
        if newIstemplate != self.istemplate:
            self.croot.attrib['IsArchivable'] = newIstemplate

    def get_Placeable(self):
        isplaceable = self.croot.get('IsPlaceable')
        return isplaceable

    def set_Placeable(self, newIsplaceable):
        if newIsplaceable != self.isplaceable:
            self.croot.attrib['IsPlaceable'] = newIsplaceable

    def get_Version(self):
        code_version = self.croot.get('Version')
        version = convert.inv_dict_version[code_version]
        return version

    def set_Version(self, newVersion):
        if newVersion != self.version:
            code_version = convert.dict_version[newVersion]
            self.croot.attrib['Version'] = code_version

    def get_mainguid(self):
        mainguid = self.croot.get('mainguid')
        return mainguid

    def set_mainguid(self, newmainguid):
        if newmainguid != self.mainguid:
            self.croot.attrib['mainguid'] = newmainguid

    def _write_(self):
        """
        Запись файла xml с последубщим конвертированием его в gsm
        """
        etree.indent(self.root, space="\t")
        txt = etree.tostring(self.root, encoding='UTF-8',
                             xml_declaration=True).decode()
        txt = txt.replace('[""', '["')
        txt = txt.replace('""]', '"]')
        txt = txt.replace('["]', '[""]')
        with open(self.fname_xml, 'tw', encoding='utf-8') as f:
            f.write(txt)
        # self.root.write(self.fname_xml, encoding='utf-8')

    #        if self.fname_gsm != None : convert.xml2gsm(self.fname_xml,self.fname_gsm, self.version)

    def close(self):
        """
        Запись кода во вкладки, вывод готового gsm
        """
        for k, c in self.code_add.items():
            tab = self._chek_CDATA_(self.get_tab(k))
            if len(c) > 0 and tab is not None:
                c.append('\n!-------------- end generated -------------')
                c = "\n".join(c)
                tab.text = etree.CDATA(c + '\n' + tab.text)
        self._write_()

    def _value_(self, key, val):
        if len(self.root.findall(".//" + key)):
            self.root.findall(".//" + key)[0].text = val

    def addcode(self, code, key):
        if len(self.code_add[key]) < 1:
            header = self.get_header()
            self.code_add[key].append(header)
        self.code_add[key].append(code)

    def addcode_dic(self, code_dic):
        for k, i in code_dic.items():
            self.addcode(i, k)

    def _addc_(self, code, comment):
        if comment != '':
            code = code + " !-> " + comment
        return code

    def _chek_CDATA_(self, data_tab):
        if data_tab is not None:
            data_tab_txt = etree.tostring(data_tab, encoding="utf-8")
            cdata_txt = "<![CDATA[".encode()
            if data_tab_txt.find(cdata_txt) == -1:
                data_tab.text = etree.CDATA(data_tab.text + ' ')
        return data_tab

    def set_defult_pen(self):
        param = self.croot.find('ParamSection').find('Parameters')
        for child in param:
            if child.tag == 'PenColor' and child.find('ArrayValues') is None:
                name = child.get('Name')
                pen = 1
                if name[-2:].lower() == 'bg':
                    pen = 19
                child.find('Value').text = str(pen)

    def get_tab(self, type_script, purge=False):
        """
        Возвращает объект вкладки
        Очишает выбранную вкладку, записывает загаловок и возвращает объект
        Ключи вкладок
        'gen' - Основной скрипт
        '3d' - 2D скрипт
        '2d' - 3D скрипт
        'spec' - Спецификации
        'ui' - Интерфейс
        'prm' - Параметры
        """
        data_tab = self.croot.find(self.mode_dic[type_script])
        if purge:
            data_tab.text = etree.CDATA('')
        return data_tab

    def get_code(self, type_script):
        data_tab = self.get_tab(type_script, purge=False)
        code = data_tab.text
        return code

    def get_header(self):
        """
        Добавляет шапку к вкладке
        """
        date = datetime.strftime(datetime.now(), "%Y.%m.%d %H:%M:%S")
        header = '\n!-----------%s------------\n!------------generated by ' \
                 'pygdl------------\n!------------------------------------------\n' % date
        return header

    def set_param(self, param_name, param_type=None, param_description=None, param_value=None, param_Child=None,
                  param_Hidden=None, param_BoldName=None, param_Unique=None, param_Fix=None):
        """
        Изменяет значение параметра, если он не существует - создаёт его
        """
        param_name = param_name.strip()
        try:
            param_type_exist = self.parameters[param_name]['Type']
        except KeyError:
            param_type_exist = None
        if param_type is not None and param_type != param_type_exist and param_type_exist is not None:
            print('Diff type', param_type_exist,
                  param_type, param_name, self.fname_xml)
            return 0
        if not (param_type in self.valid_type_param):
            print('Type error', param_type_exist, param_type, param_name)
            return 0
        param_node = None
        param = self.croot.find('ParamSection').find('Parameters')
        for child in param:
            if child.get('Name') == param_name and child.tag == param_type:
                param_node = child
                break
        if param_node is None:
            new_param = etree.SubElement(param, param_type, Name=param_name)
            new_param_description = etree.SubElement(new_param, "Description")
            if param_Child is True or param_Hidden is True or param_BoldName is True or param_Unique is True or param_Fix is True:
                new_param_flag = etree.SubElement(new_param, "Flags")
            if param_Child:
                etree.SubElement(new_param_flag, "ParFlg_Child")
            if param_Hidden:
                etree.SubElement(new_param_flag, "ParFlg_Hidden")
            if param_type != 'Title':
                if param_BoldName:
                    etree.SubElement(new_param_flag, "ParFlg_BoldName")
                if param_Unique:
                    etree.SubElement(new_param_flag, "ParFlg_Unique")
                if type(param_value) == list:
                    f_dimension = len(param_value)
                    s_dimension = 0
                    if type(param_value[0]) == list:
                        s_dimension = len(param_value[0])
                    array_value = etree.SubElement(new_param, "ArrayValues", FirstDimension=str(f_dimension),
                                                   SecondDimension=str(s_dimension))
                    for i in range(0, f_dimension):
                        if s_dimension > 1:
                            for j in range(0, s_dimension):
                                pval = param_value[i][j]
                                if param_type == 'String':
                                    pval = etree.CDATA(
                                        '"' + str(pval) + '"')
                                el = etree.SubElement(
                                    array_value, "AVal", Row=str(i+1), Column=str(j+1))
                                el.text = pval
                        else:
                            pval = param_value[i]
                            if param_type == 'String':
                                pval = etree.CDATA('"' + str(pval) + '"')
                            el = etree.SubElement(
                                array_value, "AVal", Row=str(i+1))
                            el.text = pval
                else:
                    if param_value is None or param_value == '' or (param_type != param_type_exist and param_type_exist is not None):
                        param_value = \
                            self.defult_value[param_type]
                    if param_type == 'String':
                        param_value = etree.CDATA('"' + str(param_value) + '"')
                    new_param_value = etree.SubElement(new_param, "Value")
                    new_param_value.text = param_value
            if type(param_description) == str:
                new_param_description.text = etree.CDATA(
                    '"' + param_description + '"')
            else:
                new_param_description.text = etree.CDATA(
                    '""')
            return 2
        else:
            modify_flag = 0
            if param_description is not None and param_node.find('Description').text != param_description:
                modify_flag = modify_flag + 1
                param_node.find('Description').text = etree.CDATA(
                    '"' + param_description + '"')
            if param_value is not None and param_type != 'Title':
                if type(param_value) == list:
                    f_dimension = len(param_value) - 1
                    s_dimension = 1
                    if type(param_value[0]) == list:
                        s_dimension = len(param_value[0]) - 1
                # TODO Добавить перезапись массивов
                else:
                    if param_node.find('Value').text != param_value:
                        modify_flag = modify_flag + 1
                        if param_type == 'String':
                            param_value = etree.CDATA(
                                '"' + str(param_value) + '"')
                        param_node.find('Value').text = param_value
            self._set_flag(param_name, 'Fix', param_Fix)
            if param_type != 'Title':
                if self.parameters[param_name].get('ParFlg_Child', None) != param_Child:
                    modify_flag = modify_flag + 1
                self._set_flag(param_name, 'Fix', param_Child)
                if self.parameters[param_name].get('ParFlg_Hidden', None) != param_Hidden:
                    modify_flag = modify_flag + 1
                self._set_flag(param_name, 'Fix', param_Hidden)
                if self.parameters[param_name].get('ParFlg_BoldName', None) != param_BoldName:
                    modify_flag = modify_flag + 1
                self._set_flag(param_name, 'Fix', param_BoldName)
                if self.parameters[param_name].get('ParFlg_Unique', None) != param_Unique:
                    modify_flag = modify_flag + 1
                self._set_flag(param_name, 'Fix', param_Unique)
            if modify_flag:
                return 1
            else:
                return 3
        return 0

    def _set_flag(self, param_name, key_flag, value):
        if value is not None:
            param = self.croot.find('ParamSection').find('Parameters')
            for child in param:
                if child.get('Name') == param_name and child.tag == self.parameters[param_name]['Type']:
                    param_node = child
                    break
            if not (self.parameters[param_name].setdefault(
                    'Flags') is not None) and value is True and key_flag != 'Fix':
                param_flag = etree.SubElement(param_node, "Flags")
            else:
                param_flag = param_node.find("Flags")
            if key_flag == 'Fix':
                param_flag = param_node
            if value is True and self.parameters[param_name][key_flag] is False:
                etree.SubElement(param_flag, key_flag)
            if value is False and self.parameters[param_name][key_flag] is True:
                param_flag.remove(param_flag.find(key_flag))
            self.parameters = self.get_param_list()

    def get_param_list(self):
        """
        Получить список параметров объекта в формате
        {param_name : {type,description,value,Child, Hidden,BoldName,Unique,Fix, Flags}}
        """
        try:
            param = self.croot.find('ParamSection').find('Parameters')
        except AttributeError:
            print(self.fname_xml)
        title = 'Empty_Title'
        param_list = {title: {}}
        for child in param:
            param_type = child.tag
            if param_type in self.valid_type_param:
                param_name = child.get('Name').strip()
                if param_type == 'Title':
                    title = param_name
                    param_list[title] = {}
                    param_list[title]['Type'] = 'Title'
                    param_list[title]['List'] = []
                else:
                    param_list[param_name] = {}
                if child.find('Description') is not None:
                    param_list[param_name]['Description'] = child.find(
                        'Description').text
                array_child = child.find('ArrayValues')
                if array_child is not None:
                    f_dimension = int(array_child.get('FirstDimension'))
                    s_dimension = int(array_child.get('SecondDimension'))
                    if s_dimension > 0:
                        row = [None for i in range(0, s_dimension)]
                        value = [row for i in range(0, f_dimension)]
                    else:
                        value = [None for i in range(0, f_dimension)]
                    for c in array_child.findall('AVal'):
                        val = c.text
                        r = int(c.get('Row'))-1
                        c = c.get('Column')
                        if c is not None:
                            c = int(c)-1
                            value[r][c] = val
                        else:
                            try:
                                value[r] = val
                            except IndexError:
                                print(r)

                    param_list[param_name]['Value'] = value
                else:
                    if child.find('Value') is not None:
                        param_list[param_name]['Value'] = child.find(
                            'Value').text
                ParFlg = child.find("Flags")
                param_list[param_name]['Fix'] = (child.find("Fix") is not None)
                if ParFlg is not None:
                    param_list[param_name]['ParFlg_Child'] = (
                        ParFlg.find("ParFlg_Child") is not None)
                    param_list[param_name]['ParFlg_Hidden'] = (
                        ParFlg.find("ParFlg_Hidden") is not None)
                    param_list[param_name]['ParFlg_BoldName'] = (
                        ParFlg.find("ParFlg_BoldName") is not None)
                    param_list[param_name]['ParFlg_Unique'] = (
                        ParFlg.find("ParFlg_Unique") is not None)
                    param_list[param_name]['Flags'] = True
                try:
                    param_list[title]['List'].append(param_name)
                except KeyError:
                    param_list[title] = {}
                    param_list[title]['List'] = []
                    param_list[title]['Type'] = 'EmptyTitle'
                    param_list[title]['List'].append(param_name)
                param_list[param_name]['Type'] = param_type
        return param_list

    def del_param_dic(self, param_dic):
        n_del = 0
        param = self.croot.find('ParamSection').find('Parameters')
        for param_name, val in param_dic.items():
            param_type = val.setdefault('Type')
            for child in param:
                if child.get('Name') == param_name and child.tag == param_type:
                    param.remove(child)
                    n_del = n_del + 1
                    break
            self.parameters.pop(param_name, None)
        return n_del

    def set_param_dic(self, param_dic):
        rezult = [0, 0, 0, 0]
        for param_name, val in param_dic.items():
            param_type = val.setdefault('Type')
            if param_type in self.valid_type_param:
                param_value = val.setdefault('Value')
                param_description = val.setdefault('Description')
                param_Child = val.setdefault('ParFlg_Child')
                param_Hidden = val.setdefault('ParFlg_Hidden')
                param_BoldName = val.setdefault('ParFlg_BoldName')
                param_Unique = val.setdefault('ParFlg_Unique')
                param_Fix = None
                rez = self.set_param(param_name, param_type, param_description, param_value, param_Child, param_Hidden,
                                     param_BoldName, param_Unique, param_Fix)
                rezult[rez] = rezult[rez] + 1
        n_err, n_mod, n_new, n_skip = rezult
        return n_err, n_mod, n_new, n_skip

    def gen(self, code):
        """
        Добавить код в основной скрипт
        """
        self.addcode(code, 'gen')

    def d2d(self, code):
        """
        Добавить код в 2d скрипт
        """
        self.addcode(code, '2d')

    def d3d(self, code):
        """
        Добавить код в 3d скрипт
        """
        self.addcode(code, '3d')

    def spec(self, code):
        """
        Добавить код в скрипт спецификаций
        """
        self.addcode(code, 'spec')

    def param(self, code):
        """
        Добавить код в скрипт параметров
        """
        self.addcode(code, 'prm')

    def set_keywords(self, keywords):
        """
        Записывает ключевые слова
        """
        self._value_('Keywords', keywords)

    def set_comment(self, comment):
        """
        Записывает комментарии
        """
        self._value_('Comment', comment)

    def set_copyright(self, author):
        """
        Записывает данные об авторе
        """
        self._value_('Author', author)

    def add(self, x, y, z, comment=''):
        code = 'ADD %f, %f, %f' % (x, y, z)
        self.d3d(self._addc_(code, comment))

    def add2(self, x, y, comment=''):
        code = 'ADD2 %f, %f' % (x, y)
        self.d2d(self._addc_(code, comment))

    def addx(self, x, comment=''):
        code = 'ADDX %f' % x
        self.d3d(self._addc_(code, comment))

    def addy(self, x, comment=''):
        code = 'ADDY %f' % x
        self.d3d(self._addc_(code, comment))

    def addz(self, x, comment=''):
        code = 'ADDZ %f' % x
        self.d3d(self._addc_(code, comment))

    def block(self, x, y, z, comment=''):
        code = 'BLOCK %f, %f, %f' % (x, y, z)
        self.d3d(self._addc_(code, comment))

    def citcle2(self, x, y, r, comment=''):
        code = 'CIRCLE2 %f, %f, %f' % (x, y, r)
        self.d2d(self._addc_(code, comment))

    def component(self, name, quantity, unit, comment=''):
        code = 'COMPONENT %s, %f, %s' % (name, quantity, unit)
        self.spec(self._addc_(code, comment))

    def cone(self, h, r1, r2, alpha1, alpha2, comment=''):
        code = 'CONE %f, %f, %f, %f, %f' % (h, r1, r2, alpha1, alpha2)
        self.d3d(self._addc_(code, comment))

    def cylind(self, h, r, comment=''):
        code = 'CYLIND %f, %f' % (h, r)
        self.d3d(self._addc_(code, comment))

    def del_top(self, comment=''):
        code = 'DEL TOP'
        self.d3d(self._addc_(code, comment))

    def del_n(self, n, comment=''):
        code = 'DEL %i' % n
        self.d3d(self._addc_(code, comment))

    def hotline(self, x1, y1, z1, x2, y2, z2, comment=''):
        code = 'HOTLINE %f, %f, %f, %f, %f, %f, unID : unID=unID+1' % (
            x1, y1, z1, x2, y2, z2)
        self.d3d(self._addc_(code, comment))

    def hotline2(self, x1, y1, x2, y2, comment=''):
        code = 'HOTLINE2 %f, %f, %f, %f' % (x1, y1, x2, y2)
        self.d2d(self._addc_(code, comment))

    def hotspot(self, x, y, z, paramReference, flags, displayParam, comment=''):
        code = 'HOTSPOT %f, %f, %f, unID , %s, %i, %s : unID=unID+1' % (
            x, y, z, paramReference, flags, displayParam)
        self.d3d(self._addc_(code, comment))

    def hotspot2(self, x, y, paramReference, flags, displayParam, comment=''):
        code = 'HOTSPOT2 %f, %f, unID, %s, %i, %s : unID=unID+1' % (
            x, y, paramReference, flags, displayParam)
        self.d2d(self._addc_(code, comment))

    def lin_(self, x1, y1, z1, x2, y2, z2, comment=''):
        code = 'LIN_ %f, %f, %f, %f, %f, %f' % (x1, y1, z1, x2, y2, z2)
        self.d3d(self._addc_(code, comment))

    def line2(self, x1, y1, x2, y2, comment=''):
        code = 'LINE2 %f, %f, %f, %f' % (x1, y1, x2, y2)
        self.d2d(self._addc_(code, comment))

    def model_wire(self, comment=''):
        code = 'MODEL WIRE'
        self.d3d(self._addc_(code, comment))

    def model_surface(self, comment=''):
        code = 'MODEL SURFACE'
        self.d3d(self._addc_(code, comment))

    def model_solid(self, comment=''):
        code = 'MODEL SOLID'
        self.d3d(self._addc_(code, comment))

    def mul2(self, x, y, comment=''):
        code = 'MUL2 %f, %f' % (x, y)
        self.d2d(self._addc_(code, comment))

    def mulx(self, x, comment=''):
        code = 'MULX %f' % x
        self.d3d(self._addc_(code, comment))

    def muly(self, x, comment=''):
        code = 'MULY %f' % x
        self.d3d(self._addc_(code, comment))

    def mulz(self, x, comment=''):
        code = 'MULZ %f' % x
        self.d3d(self._addc_(code, comment))

    def rect2(self, x1, y1, x2, y2, comment=''):
        code = 'RECT2 %f, %f, %f, %f' % (x1, y1, x2, y2)
        self.d2d(self._addc_(code, comment))

    def rot2(self, a, comment=''):
        code = 'ROT2 %f' % a
        self.d2d(self._addc_(code, comment))

    def rotx(self, a, comment=''):
        code = 'ROTX %f' % a
        self.d3d(self._addc_(code, comment))

    def roty(self, a, comment=''):
        code = 'ROTY %f' % a
        self.d3d(self._addc_(code, comment))

    def rotz(self, a, comment=''):
        code = 'ROTZ %f' % a
        self.d3d(self._addc_(code, comment))

    def text2(self, x1, y1, txt, comment=''):
        code = 'TEXT2 %f, %f, "%s"' % (x1, y1, txt)
        self.d2d(self._addc_(code, comment))

    def define_style(self, name, font_family, size, anchor, face_code, comment=''):
        code = 'DEFINE STYLE "%s" %s, %s, %s, %s' % (
            name, font_family, size, anchor, face_code)
        self.gen(self._addc_(code, comment))

    def set_style(self, name, comment=''):
        code = 'SET STYLE "%s"' % name
        self.d2d(self._addc_(code, comment))

    def prism_get(self, thickness, comment=''):
        code = 'PRISM NSP/2, %f, GET(NSP)' % thickness
        self.d3d(self._addc_(code, comment))

    def project2(self, projection_code, angle, method, comment=''):
        code = 'PROJECT2 %i, %f, %i' % (projection_code, angle, method)
        self.d2d(self._addc_(code, comment))


if __name__ == "__main__":
    convert_old_dir = os.path.abspath(os.path.join(curr_dir, 'CONVERT', 'gsm'))
    convert_new_dir = os.path.abspath(
        os.path.join(curr_dir, 'CONVERT', 'gsm_out'))
    convert_temp_dir = os.path.abspath(
        os.path.join(curr_dir, 'CONVERT', 'xml'))
    base = database_guid(DataBase_mainguid_fname)
    for root, dirs, files in os.walk(convert_temp_dir):
        for nm in files:
            if nm.find(".xml") > 0:
                fname_xml = os.path.join(root, nm)
                test_obj = gdl_gsm(fname_xml, base)
                mid, name = test_obj.get_type()
                print(name)
