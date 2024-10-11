# # refactor ladder style plus listable handling
# plus scoping

import sys
import re
from inspect import currentframe

from defaulthandlers import *   # relation handlers
from pcpp import pcpp
from pycrst import rp_dict      # Potter's (2023) pycrst, pcpp, etc


filename = ''
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
    nuc = int(re.findall(r'\d+', str(rplist))[-1])
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
# This is used by another version of refactor! 
def listify(convlist):

    lhsats = []
    rhsats = []
    
    nuc = getconvnuc(convlist)
    for r in convlist:
        if islhs(r, nuc):
            lhsats.append(r)
        else:
            rhsats.append(r)

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
         #       debug('listify', filename, newrp)
           
    return convlist

# scope escalation
# See satellite-nucleus-satellite in ZPG doc.
# for scoping to apply all convergent rels must be
# in the same group

sns_groups = {
    
    'acceptance' : [#'antithesis',
                    #'concession',
                    'evidence',
                    'reason',
                    'justify',
                    ],

    'performance' : [
                    'motivation',
                    'enablement',
                    ],
    
    'comprehension' : [
                    #'background',
                    #'preparation',
                    'elaboration',
                    'summary',
                    'restatement',
                    'evaluation',
                    'evaluation_n',
                    'interpretation',
                    ],
    'resistance' : [
                    'antithesis',
                    'concession'
                    ],

    'causality' :   # this group could use further study... see e.g., GlobalWarming
        [
         #'circumstance',
         'condition',
         'means',
         'nonvolitional_cause',
         'nonvolitional_result',
         'otherwise',
         'unless',
         'purpose',
         'solutionhood',
         'unconditional',
         'unless',
         'volitional_cause',
         'volitional_result',
         'cause',
         'result'
         ],

        # otherwise and unless are treated as variants on condition

    }

# satellite-nucleus-satellite match
def sns_match(rlist):
        
    for k in sns_groups:
        v = sns_groups.get(k)
        if all(ele in v for ele in rlist):
            return True
    return False


def get_rels(convlist):
    rel_list = []
    for rel in convlist:
        rel_list.append(rel[0])
    return rel_list


# reorder sns scope 
scope_count = 0

def escalate_scope(convlist):

    lhsats = []
    rhsats = []

    global scope_count

    rel_list = get_rels(convlist)   
    nuc = getconvnuc(convlist)
    
    for r in convlist:
        if islhs(r, nuc):
            lhsats.append(r)
        else:
            rhsats.append(r)

    summary = False
    for r in rhsats:
        if r[0] == 'summary':   # scope escalation by definition
            summary = True
            break
        
    if summary or len(lhsats) and len(rhsats) and sns_match(rel_list):
        i = 0
        while i < len(rhsats):
            convlist.insert(0,convlist.pop())
            i += 1
        scope_count += 1
    return convlist



def refact(rp):
    
    if isinstance(rp, int):
        return rp

    if rp[0] == 'convergence':               # refactor it

        rplist = escalate_scope(listify(consort(tup2list(rp[1]))))
        
        if len(rplist) == 1:

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
    filename = f            # for use elsewhere
    print(filename)
    exp = refact(eval(rp))
    rp_list.append(exp)

    
if __name__ == "__main__":
    ct = 0
    for rp in rp_list:
#        debug(rp)
        ct += 1
    print('Total refactors rp:', ct)

        


