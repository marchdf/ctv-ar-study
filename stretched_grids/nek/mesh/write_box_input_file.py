#!/usr/bin/env python

# ========================================================================
#
# Imports
#
# ========================================================================
import argparse
import pandas as pd


# ========================================================================
#
# Main
#
# ========================================================================
parser = argparse.ArgumentParser(description='Write Nek5000 box')
parser.add_argument('-i',
                    '--iname',
                    dest='iname',
                    help='Input file of (x,y) coordinates',
                    type=str,
                    default=8)
parser.add_argument('-o',
                    '--oname',
                    dest='oname',
                    help='Output Nek5000 box',
                    type=str,
                    default='ctv.box')
args = parser.parse_args()

# read the data
df = pd.read_csv(args.iname)
npoints = len(df.x) - 1

# write box input file
with open(args.oname, 'w') as of:
    of.write("-2\n")
    of.write("1\n")
    of.write("Box\n")
    of.write("%d\t%d\n" % (npoints, npoints))

    for i in range(npoints + 1):
        of.write("%10.8e " % (df.x[i]))
        if(i % 5 == 0):
            of.write("\n")
    of.write("\n")

    for i in range(npoints + 1):
        of.write("%10.8e " % (df.y[i]))
        if(i % 5 == 0):
            of.write("\n")

    of.write("\n")

    of.write("P  ,P  ,P  ,P  ,   ,  ")
