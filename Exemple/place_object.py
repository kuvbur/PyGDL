# -*- coding: utf-8 -*-
"""
Created on Tue Apr 28 12:01:20 2020

@author: da-rogojin
"""
import lxml

coord = {'x':0, 'y':0, 'z':0}

root = lxml.etree.Element('PlacedObjects')
position_section = lxml.etree.SubElement(root, 'Position')
#Запись координат
for axsis,value in coord.items():
    c = lxml.etree.SubElement(position_section, axsis)
    c.text = str(value)
    
#Запись параметров
param_section = lxml.etree.SubElement(root, 'Parameters')

#Запись данных об элементе
libpart_section = lxml.etree.SubElement(root, 'LibPart')
gsm_abs_fname = lxml.etree.SubElement(libpart_section, 'Location') 
pure_abs_fname = abs_fname.replace(' ', '%20')
gsm_abs_fname.text = 'lan.flat:///' + pure_abs_fname

# Запись в файл
lxml.etree.indent(root, space="\t")
txt = lxml.etree.tostring(root, encoding='UTF-8', xml_declaration=True).decode()
txt = txt.replace('[""', '["')
txt = txt.replace('""]', '"]')
txt = txt.replace('["]', '[""]')
with open("test.xml", 'tw', encoding='utf-8') as f:
    f.write(txt)