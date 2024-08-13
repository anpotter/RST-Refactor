# Convert RST text to dictionary.

import xml.etree.ElementTree as ET
import os
from inspect import currentframe

from rs3list import rs3list

debugging = True
def debug(*arg):
    if debugging:
        frameinfo = currentframe()
        print(frameinfo.f_back.f_lineno,":",*arg)
 #       input()
    return None

def rst2dict(rstFile):
    
    text_dict = {}

#    debug('rsttext2dict: ', rstFile)
    
    xmlroot = ET.parse(rstFile).getroot()
    body = xmlroot.find('body')
    seglist = body.findall('segment')
    segnum = 1          # Do not rely on RSTTool segment numbering

    for span in seglist:
        
        text = span.text if span.text else ''      
        text = text.strip().replace('\n','')
        id = str(segnum)
        text_dict[id] = text
        segnum += 1 

    return text_dict

ct = 0
text_dict_list = []

for rstFile in rs3list:
    text_dict = rst2dict(rstFile)
    text_dict_list.append(text_dict)
    ct += 1

if __name__ == "__main__":
    print('Total: ', ct)
    i = 0
    max = 5
    for td in text_dict_list:
        for key, value in td.items():
            print('\'{}\':\'{}\','.format(key, value))
        print()
        i += 1
        if i > max:
            break

print('Total texts rp:', ct)
