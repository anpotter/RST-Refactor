# Baseline v 5 for listable convergences
# refactor ladder style plus listable handling

import sys
import re
from inspect import currentframe

from defaulthandlers import *   # relation handlers
from pcpp import pcpp
from pycrst import rp_dict      # input


debugging = True
def debug(*arg):
    if debugging:
        frameinfo = currentframe()
        print(frameinfo.f_back.f_lineno,":",*arg)
        input()
    return None

########################################
# convert nested tuple to list
def tup2list(data):
    if isinstance(data, tuple) or isinstance(data, list):
        data = list(data)
        for i in range(len(data)):
            if isinstance(data[i], tuple) or isinstance(data[i], list):
                data[i] = tup2list(data[i])
    return data

########################################
# sort convergent rps by sat

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
    rix.reverse()        

    n = 0
    
    for i in lix:
        new_dict[n] = rp_ldict[i]
        n += 1

    for i in rix:
        new_dict[n] = rp_rdict[i]
        n += 1

    new_list = []
    for s in new_dict:
        new_list.append(new_dict[s])
        
    return new_list


###########################################3
# find the nucleus of a convergence

def getconvnuc(rplist):
#    nuc = int(re.findall(r'\d+', str(rplist))[-1])
    return int(re.findall(r'\d+', str(rplist))[-1])


##################################################

## Find the satellites to the left of the nucleus 
#return True if rp sat less than nuc
def islhs(rp, nuc):
    sat = int(re.findall(r'\d+', str(rp))[0])
    return sat < nuc


####################################################

## Find the satellites to the right of the nucleus 
def isrhs(rp, nuc):      
    return not islhs(rp,nuc)


####################################################

## get the set of relations for rplist

def get_rel_set(rplist):
    rels = []
    for r in rplist:
        rels.append(r[0])
    return list(set(rels))


####################################
# replace eligible convergences with list relations

def listify(convlist):

    lhsats = []
    rhsats = []
    
    nuc = getconvnuc(convlist)
    for r in convlist:
        if islhs(r, nuc):
            lhsats.append(r)
        else:
            rhsats.append(r)

    listitems = []

    for sats in [lhsats, rhsats]:
        if len(sats) > 1:
            rels = get_rel_set(sats)
            if len(rels) == 1:
                for r in sats:
                    convlist.remove(r)
                rel = sats[0][0]
                nuc = sats[0][1][1]
                listitems = []
                for r in sats:
                    listitems.append(r[1][0])
                newrp = [rel, [['list_',listitems],nuc]]            
                convlist.append(newrp)
                
    if listitems:
        print('LISTIFY:', convlist)
    return convlist



def refact(rp):
    
    if isinstance(rp, int):
        return rp

    if rp[0] == 'convergence':               # refactor it
        
        rplist = listify(consort(tup2list(rp[1])))
        
        if len(rplist) == 1:
            #exp = '{}({},{})'.format(rplist[0][0], rplist[1][0],rplist[1][1])
            rp = rplist[0]
            rel = rp[0]
            sat = rp[1][0]
            nuc = rp[1][1]
            exp = '{}({},{})'.format(rel, refact(sat),refact(nuc))
        elif len(rplist) > 1:
            while len(rplist) > 1:
                ult = rplist.pop()
                pen = rplist.pop()
                pen[1][1] = ult                 # make ultimate nuc of penultimate
                rplist.append(refact(pen))      # list boils down to one formatted rp
            
            exp = rplist[0]

        return exp
    
    else:                               # otherwise just replay it

        if not isinstance(rp, (list,tuple)):
            return rp
        
        exp_list = []
        for arg in rp[1]:
            ex = refact(arg)
            exp_list.append(ex)
        exp = '{}({})'.format(rp[0],','.join(map(str,exp_list)))

        return exp

########################################
rp_list = []    # for import by rp2rs3driver

########################################
# run it
for f, rp in rp_dict.items():       # for each item from pycrst
    print(f)
    exp = refact(eval(rp))

    rp_list.append(exp)
 #   debug(exp)
 #   debug(pcpp(exp))
 

    
if __name__ == "__main__":
    ct = 0
    for rp in rp_list:
#        debug(rp)
        ct += 1
    print('Total refactors rp:', ct)

        


