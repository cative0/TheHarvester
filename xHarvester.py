# -*- coding: utf-8 -*-
# @CreateTime:  2017/8/4 14:25 
# @CreateBy:    Alvin
# @File:        xHarvester.py
# @UpdateTime:
# @UpdateBy:

import os
import sys
import getopt

from theHarvester import usage
from theHarvester import start


def x_start(arg):
    if len(sys.argv) < 4:
        usage()
        sys.exit()
    try:
        opts, args = getopt.getopt(arg, "l:d:b:s:vf:nhcte:")
    except getopt.GetoptError:
        usage()
        sys.exit()

    opt_keys = [opt[0] for opt in opts]

    if ('-d' in opt_keys) and ('-f' in opt_keys):
        f_index = opt_keys.index('-f')
        d_index = opt_keys.index('-d')

        d_file = opts[d_index][1]

        if (not os.path.exists(d_file)) or not os.path.isfile(d_file):
            sys.exit()

        with open(d_file) as f:
            for line in f:
                d_value = line[:-1]
                f_value = os.path.join('output', line[:-1] + '.html')

                opts[d_index] = ('-d', d_value)
                opts[f_index] = ('-f', f_value)

                start(opts)


if __name__ == "__main__":
    try:
        x_start(sys.argv[1:])
    except KeyboardInterrupt:
        print "Search interrupted by user.."
    except:
        sys.exit()

