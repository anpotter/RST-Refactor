
## pycrst 1.0
## An Algorithm for Pythonizing Rhetorical Structures
## Andrew Potter
## 6/8/2023
## 1/6/2024 Minor setup changes for refactor

'''
Current reference if citing this work:
Potter, A. (2023). An algorithm for Pythonizing rhetorical structures. In S. Carvalho, A. F. Khan, A. O. Anić, Blerina Spahiu, J. Gracia, J. P. McCrae, D. Gromann, Barbara Heinisch, & A. Salgado (Eds.), Language, data and knowledge 2023 (LDK 2023): Proceedings of the 4th Conference on Language, Data and Knowledge (pp. 493-503). NOVA CLUNL. 

Some assumptions, limitations, caveats
Hyphenated relation names are converted to snake format.
It is assumed that every text will contain at least one relation.
Some discontinuitites and span anomalies are detected.
Input files must be on local drive in rstfiles subfolder.
'''
## 8/14/2023 bug fixes, integration of convergence into main function

## 10/2023
## modularlized, and support batch processing


from inspect import currentframe
import xml.etree.ElementTree as ET
import re
import sys
import os
from pcpp import pcpp
from rs3list import rs3list
#from test_list import test_list as rs3list

batch_mode = False    
debugging = True


##################################################################
## relational proposition, generally known as rp
class RelProp:
    def __init__(self, rel, sat, nuc, type, text):
        self.rel = rel
        self.sat = sat
        self.nuc = nuc
        self.type = type
        self.text = text.strip() if text else ""

########################################
## load RST file, initialize rplist


def initialize(rstFile):

    global top
    global rplist

#    print(rstFile)
    rplist = []
    top = None
    
    xmlroot = ET.parse(rstFile).getroot()

    header = xmlroot.find('header')
    relations = header.find('relations')
    relList = relations.findall('rel')

    for rel in relList:             # make list of all multinuc predicates
        type = rel.get('type')
        if type == 'multinuc':
            name = snakify(rel.get('name'))
            multinucs.append(name)

    body = xmlroot.find('body')
    spanList = body.findall('segment') + body.findall("group")
    
    for rp in spanList:
        rel = snakify(rp.get('relname'))
        sat = rp.get('id')
        nuc = rp.get('parent')
        type = rp.get('type')
        if not type: type = 'segment'
        text = rp.text
        rplist.append(RelProp(rel,sat,nuc,type,text))

    for rp in rplist:
        if rp.nuc == None:
            top = rp
            rp.rel = "top"
            rp.nuc = ""

    
    rplist = renumber(rplist)
    return top

########################################
# Transform RST to RP 

def gen_exp(rp):

    if rp.rel == 'top' and rp.type == 'span':
        exp = gen_exp(get_nuc(rp.sat))
        
    elif rp.type == 'span':
        nuc_exp = gen_exp(get_span_nuc(rp))
        if get_sat_count(rp) > 1:   # converge
            exp_list = []
            children = get_children(rp)
            for child in children:
                if child.rel != 'span':
                    if child.type == 'span':
                        child.nuc = nuc_exp
                        exp_list.append(gen_exp(child))
                    elif child.type == 'multinuc':
                        child.nuc = nuc_exp
                        exp_list.append(format_rp(child.rel, gen_exp(child), child.nuc))
                    elif child.type == 'segment':
                        child.nuc = nuc_exp
                        exp_list.append(format_rp(child)) 
            exp = 'convergence(' + ','.join(exp_list) + ')'

        else:
            sat = get_sat(rp)
            if sat:
                if sat.type == 'multinuc':
                    sat.nuc = nuc_exp
                    exp = format_rp(sat.rel,gen_exp(sat),nuc_exp)
                else:
                    sat_rp = get_span_nuc(sat)
                    if sat_rp:
                        sat.sat = gen_exp(sat_rp)
                    exp = format_rp(sat.rel, sat.sat, nuc_exp)
            else:
                exp = format_rp(rp.rel, nuc_exp, rp.nuc)

    elif rp.type == 'segment':
        if get_sat_count(rp) > 1:   # converge
            exp_list = []
            children = get_children(rp)
            for child in children:
                if child.type == 'multinuc':
                    exp = format_rp(child.rel, gen_exp(child), child.nuc)
                elif child.type == 'span':
                    exp = gen_exp(child)
                else:
                    exp = format_rp(child)
                exp_list.append(exp)
            exp = 'convergence(' + ','.join(exp_list) + ')'
            
        else:
            sat = get_sat(rp)
            if not sat:
                exp = format_rp(rp)
##                if rp.rel == 'span':    # decorative span add to pycrst 
##                    exp = rp.sat
##                else:
##                    exp = format_rp(rp)
            elif sat.type == 'multinuc':
                exp = format_rp(sat.rel, gen_exp(sat), rp.sat)
            else:
                exp = gen_exp(sat)

    elif rp.type == 'multinuc':
        nucs = get_mn_nucs(rp)       
        nuc_exp_lst = []            # create list of nuclei rps
        for n in nucs:
            if n.type == 'span':
                nuc_exp_lst.append(gen_exp(get_children(n)[0]))
            elif n.type == 'multinuc':  # multinuc within multinuc
                nuc_exp_lst.append(gen_exp(n))
            else:
                nuc_exp_lst.append(n.sat)

        nuc_exp_lst = sort_nucs(nuc_exp_lst)
        exp = '{}({})'.format(nucs[0].rel, ','.join(nuc_exp_lst))
        
        mn_sats = get_mn_sats(rp)   # get sats for mn, if any
        
        if len(mn_sats) == 1:
            mn_sats[0].nuc = exp
            if mn_sats[0].type == 'segment':
                exp = format_rp(mn_sats[0])
            else:
                exp = gen_exp(mn_sats[0])
                if not mn_sats[0].type == 'span':
                    mn_sats[0].sat = exp
                    exp = format_rp(mn_sats[0])

        elif len(mn_sats) > 1:  # converge
            sat_exp_lst = []
            for r in mn_sats:
                r.nuc = exp
                if r.type == 'multinuc':
                    sat_exp_lst.append(format_rp(r.rel, gen_exp(r), r.nuc))
                else: 
                    sat_exp_lst.append(gen_exp(r))
            exp = 'convergence(' + ','.join(sat_exp_lst) + ')'
    return exp

###############################################################
# print debug when turned on
def debug(*arg):
    if debugging:
        frameinfo = currentframe()
        print(frameinfo.f_back.f_lineno,":",*arg)
        input()
    return None

## miscellaneous
##def is_span_type(rp): return rp.type == 'span'
##def is_multi_type(rp): return rp.type == 'multinuc'
##def is_segment(rp): return rp.type == 'segment'
def is_multi_rel(rp): return rp.rel in multinucs
#def is_top(rp): return rp.rel == 'top'
def snakify(s):
    s = 'list_' if s == 'list' else s
    return s.replace('-','_') if s else s
rplist = []
top = None
multinucs = []

########################################
## sequentialize segment numbering
def renumber(rplist):
    old_nums = []
    for rp in rplist:
        old_nums.append(int(rp.sat))
        
    new_nums = [item for item in range(1, len(rplist) + 1)]
    for rp in rplist:
        if rp.rel == 'top':
            rp.sat = str(new_nums[old_nums.index(int(rp.sat))])
        else:
            rp.sat = str(new_nums[old_nums.index(int(rp.sat))])
            rp.nuc = str(new_nums[old_nums.index(int(rp.nuc))])
    return rplist

########################################
# format rp as pythonic expression
def format_rp(*rp):

    rpexp = "{}({},{})"
    
    if len(rp) == 1:
        return rpexp.format(rp[0].rel,rp[0].sat,rp[0].nuc)
    elif len(rp) == 3:
        return rpexp.format(rp[0],rp[1],rp[2])
    
########################################
# get the nucs for a multiuclear type rp  
def get_mn_nucs(rp):
    mn_nucs = []
    children = get_children(rp)
    for child in children:
        if is_multi_rel(child):
            mn_nucs.append(child)
    return mn_nucs

########################################
#get the sats for a multiuclear type rp
def get_mn_sats(rp):
    mn_sats = []
    children = get_children(rp)
    for child in children:
        if not is_multi_rel(child): 
            mn_sats.append(child)
    return mn_sats

########################################
# Sort the nucs in multinuclear expression
def sort_nucs(nuc_exp_lst):

    mn_dict = {}
    for exp in nuc_exp_lst:
        temp = re.findall(r'\d+', exp)
        mn_dict[int(temp[0])] = exp

    myKeys = sorted(list(mn_dict.keys()))
    mn_dict = {i: mn_dict[i] for i in myKeys}

    nuc_exp_lst = []
    for key in myKeys:
        nuc_exp_lst.append(mn_dict.get(key))

    return nuc_exp_lst

########################################
# get the nucleus associated with an rp
def get_nuc(nucid):
    for rp in rplist:
        if nucid == rp.nuc:
            return rp
    debug("get_nuc not found", nucid)
    return None

########################################
# get all rps linking to an rp 
def get_children(rp):
    children = []
    for r in rplist:
        if r.nuc == rp.sat:
            children.append(r)
    return children

########################################
# get the span relation linking to an rp, if any
def get_span_nuc(rp):
    children = get_children(rp)
    for child in children:
        if child.rel == 'span':
            return child
    return False

########################################
# get the number of satellites linking to an rp
def get_sat_count(rp):
    satcount = 0
    children = get_children(rp)
    for child in children:
        if child.rel != 'span':
            satcount += 1
    return satcount

########################################
# get the (solitary) sat linking to an rp
def get_sat(rp):
    children = get_children(rp)    
    for child in children:
        if child.rel != 'span': 
            return child
    return False

def getrplist():
    return rplist


######################################rstFile = 
# run it

# exp_list = []

rp_dict = {}

ct = 0
for rstFile in rs3list:
        
    top = initialize(rstFile)
    exp = gen_exp(top)

    if __name__ == "__main__":
        print("  \'{}\': \'{}\',".format(rstFile, exp))
        print(pcpp(exp))
    else:
        rp_dict[rstFile] = exp

    ct += 1
    
print("pycrst Total texts ", ct) 
##  print("  \'" + exp + "\',")
        


          





