# refactor stairstep style

import sys
import re
from inspect import currentframe

from defaulthandlers import *   # relation handlers
from pcpp import pcpp
from pycrst import rp_dict      # Potter's (2023) pycrst, pcpp, etc



debugging = False
def debug(*arg):
    if debugging:
        frameinfo = currentframe()
        print(frameinfo.f_back.f_lineno,":",*arg)
        input()
    return None

########################################
# convert nested tuple to list
def listify(data):
    if isinstance(data, tuple) or isinstance(data, list):
        data = list(data)
        for i in range(len(data)):
            if isinstance(data[i], tuple) or isinstance(data[i], list):
                data[i] = listify(data[i])
    return data

########################################
# sort convergent rps by sat
# output of pycrst may require this, e.g., see syncom
def consort(rp): 
           
    lix = []
    rix = []
    rp_ldict = {}   # left of loie
    rp_rdict = {}   # right of loie
    new_dict = {}   # merged
    
    for i in range(0,len(rp)):
        seg = rp[i]
        segnums = re.findall(r'\d+', str(rp[i]))
        satid = int(segnums[0])
        nucid = int(segnums[-1])

        if satid < nucid:
            rp_ldict[satid] = seg
            lix.append(satid)
        else:
            rp_rdict[satid] = seg
            rix.append(satid)

    lix.sort()
    rix.sort()
#    rix.reverse()        

    n = 0
    ldict = {}
    llist = []
    for i in lix:
        ldict[n] = rp_ldict[i]
        n += 1
    for s in ldict:
        llist.append(ldict[s])

    n = 0
    rdict = {}
    rlist = []
    for i in rix:
        rdict[n] = rp_rdict[i]
        n += 1
    for s in rdict:
        rlist.append(rdict[s])

    return llist, rlist



######################################## 
def consol(rlist):    # consolidate convergence list  

    while len(rlist) > 1:
                
        first = rlist.pop(0)
        second = rlist.pop(0)
        
        first = '{}({},{})'.format(first[0], refact(first[1][0]), refact(second[1][0]))

        second[1][0] = first
        rlist.insert(0, second)
        debug(rlist)
        debug(len(rlist))
                
    return rlist[0]


########################################
# refactor convergence relations
def refact(rp):
    
    if isinstance(rp, int):
        return rp

    exp = ''
    
    if rp[0] == 'convergence':               # refactor it

        llist, rlist = consort(listify(rp[1]))

        if rlist:
            rlist.reverse()
            rp = consol(rlist)
            debug(rp)
            exp = '{}({},{})'.format(rp[0], refact(rp[1][0]), refact(rp[1][1]))

        if llist:                                     
            rp = consol(llist)
            debug(rp)
            if not exp:
                exp = refact(rp[1][1])
            exp = '{}({},{})'.format(rp[0], refact(rp[1][0]), exp)

        return exp

    else:                               # otherwise just replay it

        if not isinstance(rp, (list,tuple)):
            return rp
        exp_list = []
        for arg in rp[1]:
            exp_list.append(refact(arg))   
        exp = '{}({})'.format(rp[0],','.join(map(str,exp_list)))

      #  print(exp)
        return exp

########################################
rp_list = []    # for import by rp2rs3driver

########################################
# run it
for f, rp in rp_dict.items():       # for each item from pycrst
    print(f)
    exp = refact(eval(rp))
    rp_list.append(exp)

if __name__ == "__main__":
    ct = 0
    for rp in rp_list:
        ct += 1
        print(pcpp(rp))
    print('Total refactors rp:', ct)

        


