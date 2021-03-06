#!/usr/bin/env python3

# ========================================================================
#
# Imports
#
# ========================================================================
import argparse
import os
import numpy as np
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd


# ========================================================================
#
# Some defaults variables
#
# ========================================================================
plt.rc('text', usetex=True)
plt.rc('font', family='serif', serif='Times')
cmap_med = ['#F15A60', '#7AC36A', '#5A9BD4', '#FAA75B',
            '#9E67AB', '#CE7058', '#D77FB4', '#737373']
cmap = ['#EE2E2F', '#008C48', '#185AA9', '#F47D23',
        '#662C91', '#A21D21', '#B43894', '#010202']
dashseq = [(None, None), [10, 5], [10, 4, 3, 4], [
    3, 3], [10, 4, 3, 4, 3, 4], [3, 3], [3, 3]]
markertype = ['s', 'd', 'o', 'p', 'h']


# ========================================================================
#
# Function definitions
#
# ========================================================================
def parse_error(fname):
    df = pd.read_csv(fname, skiprows=1, delim_whitespace=True)

    df.rename(columns={'Node': "NodeCount",
                       'Count': 'Loo',
                       'Loo': 'L1',
                       'L1': 'L2'},
              inplace=True)
    df.dropna(axis=1, how='any', inplace=True)
    df.replace({'velocity\[0\]': 'u',
                'velocity\[1\]': 'v',
                'velocity\[2\]': 'w',
                'dpdx\[0\]': 'dpdx',
                'dpdx\[1\]': 'dpdy',
                'dpdx\[2\]': 'dpdz'},
               regex=True,
               inplace=True)
    return df


# ========================================================================
#
# Main
#
# ========================================================================
if __name__ == '__main__':

    # ========================================================================
    # Parse arguments
    parser = argparse.ArgumentParser(
        description='A simple plot tool')
    parser.add_argument(
        '-s', '--show', help='Show the plots', action='store_true')
    args = parser.parse_args()

    # ======================================================================
    # Load the data
    methods = ['edge', 'cvfem']
    aspects = [1, 2, 4, 8, 16, 32, 64, 128]

    edf = []
    for i, method in enumerate(methods):
        for j, aspect in enumerate(aspects):
            ename = os.path.abspath(os.path.join(method,
                                                 'ar{0:03d}'.format(aspect),
                                                 'ctv.dat'))
            df = parse_error(ename)
            df['Aspect'] = aspect
            df['Method'] = method
            edf.append(df)

    edf = pd.concat(edf)
    edf['theory'] = edf.Aspect**2 * 1e-5

    # ======================================================================
    # Plot
    fields = ['u', 'v', 'dpdx', 'dpdy']
    for i, field in enumerate(fields):
        for j, method in enumerate(methods):
            plt.figure(i)
            subdf = edf[(edf.Time == 1.0) &
                        (edf.Field == field) &
                        (edf.Method == method)]
            p = plt.loglog(subdf.Aspect,
                           subdf.L2,
                           lw=2,
                           color=cmap[j],
                           marker=markertype[j],
                           mec=cmap[j],
                           mfc=cmap[j],
                           ms=10,
                           label=method)
            if j == 0:
                p = plt.loglog(subdf.Aspect,
                               subdf.theory,
                               lw=2,
                               color=cmap[-1],
                               label='2nd order')

    # Format plots
    plt.figure(0)
    ax = plt.gca()
    plt.xlabel(r"aspect ratio", fontsize=22, fontweight='bold')
    plt.ylabel(r"$L_2(u)$", fontsize=22, fontweight='bold')
    plt.setp(ax.get_xmajorticklabels(), fontsize=18, fontweight='bold')
    plt.setp(ax.get_ymajorticklabels(), fontsize=18, fontweight='bold')
    legend = ax.legend(loc='best')
    #ax.set_ylim([1e-6, 1e0])
    plt.tight_layout()
    plt.savefig('u_norm.png', format='png')

    plt.figure(1)
    ax = plt.gca()
    plt.xlabel(r"aspect ratio", fontsize=22, fontweight='bold')
    plt.ylabel(r"$L_2(v)$", fontsize=22, fontweight='bold')
    plt.setp(ax.get_xmajorticklabels(), fontsize=18, fontweight='bold')
    plt.setp(ax.get_ymajorticklabels(), fontsize=18, fontweight='bold')
    legend = ax.legend(loc='best')
    ax.set_ylim([1e-6, 1e0])
    plt.tight_layout()
    plt.savefig('v_norm.png', format='png')

    plt.figure(2)
    ax = plt.gca()
    plt.xlabel(r"aspect ratio", fontsize=22, fontweight='bold')
    plt.ylabel(r"$L_2\left(\frac{dp}{dx}\right)$",
               fontsize=22, fontweight='bold')
    plt.setp(ax.get_xmajorticklabels(), fontsize=18, fontweight='bold')
    plt.setp(ax.get_ymajorticklabels(), fontsize=18, fontweight='bold')
    legend = ax.legend(loc='best')
    ax.set_ylim([1e-6, 1e0])
    plt.tight_layout()
    plt.savefig('dpdx_norm.png', format='png')

    plt.figure(3)
    ax = plt.gca()
    plt.xlabel(r"aspect ratio", fontsize=22, fontweight='bold')
    plt.ylabel(r"$L_2\left(\frac{dp}{dy}\right)$",
               fontsize=22, fontweight='bold')
    plt.setp(ax.get_xmajorticklabels(), fontsize=18, fontweight='bold')
    plt.setp(ax.get_ymajorticklabels(), fontsize=18, fontweight='bold')
    legend = ax.legend(loc='best')
    ax.set_ylim([1e-6, 1e0])
    plt.tight_layout()
    plt.savefig('dpdy_norm.png', format='png')
