# Refactoring RST Convergences

import os
from rsttext2dict import text_dict_list

# baselines
#from refactor_v5b import rp_list   # stair-step
#from refactor_v5d import rp_list   # Ladder + listification
#from refactor_v5e import rp_list   # Ladder + listification disabled
from refactor_v5g import rp_list    # Ladder + Scoping

from rs3list import rs3list     # RS3 input list
from rp2rs3 import rp2rs3       # Cameron's rp to RST conversion code

outpath = "./refactored"

for i in range(len(rp_list)):
    
    rel_info = rp_list[i]    
    text_dict = text_dict_list[i]

    outfile = os.path.splitext(os.path.basename(rs3list[i]))[0] + '.rs3'

    rs_obj = rp2rs3(rel_info, text_dict)
    rs_obj.save_to_XML(outpath, outfile)
 
    print(outfile, i)


