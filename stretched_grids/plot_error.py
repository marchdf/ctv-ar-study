#!/usr/bin/env python3

# ========================================================================
#
# Imports
#
# ========================================================================
import argparse
import os
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import netCDF4 as nc


# ========================================================================
#
# Some defaults variables
#
# ========================================================================
plt.rc("text", usetex=True)
cmap_med = [
    "#F15A60",
    "#7AC36A",
    "#5A9BD4",
    "#FAA75B",
    "#9E67AB",
    "#CE7058",
    "#D77FB4",
    "#737373",
]
cmap = [
    "#EE2E2F",
    "#008C48",
    "#185AA9",
    "#F47D23",
    "#662C91",
    "#A21D21",
    "#B43894",
    "#010202",
]
dashseq = [
    (None, None),
    [10, 5],
    [10, 4, 3, 4],
    [3, 3],
    [10, 4, 3, 4, 3, 4],
    [3, 3],
    [3, 3],
]
markertype = ["s", "d", "o", "p", "h", "^"]


# ========================================================================
#
# Function definitions
#
# ========================================================================
def parse_error(fname):
    df = pd.read_csv(fname, skiprows=1, delim_whitespace=True)

    df.rename(
        columns={"Node": "NodeCount", "Count": "Loo", "Loo": "L1", "L1": "L2"},
        inplace=True,
    )
    df.dropna(axis=1, how="any", inplace=True)
    df.replace(
        {
            "velocity\[0\]": "u",
            "velocity\[1\]": "v",
            "velocity\[2\]": "w",
            "dpdx\[0\]": "dpdx",
            "dpdx\[1\]": "dpdy",
            "dpdx\[2\]": "dpdz",
        },
        regex=True,
        inplace=True,
    )
    return df


# ========================================================================
def get_aspect_ratio(fname, aspect):
    "Get the min/max/mean aspect ratio of a mesh"

    # Load the data
    dat = nc.Dataset(fname)

    # Get coordinates
    coord = (
        dat.variables["coordx"][:],
        dat.variables["coordy"][:],
        dat.variables["coordz"][:],
    )

    # Subset on the nodes on the face
    actual_idx = np.where(coord[2] <= 0.0 + 1e-10)
    coord = (coord[0][actual_idx], coord[1][actual_idx], coord[2][actual_idx])
    N = int(np.sqrt(coord[0].shape[0]) - 1)
    x = coord[0].reshape((N + 1, N + 1))
    y = coord[1].reshape((N + 1, N + 1))

    # Aspect ratio in each cell
    ar = np.diff(x, axis=1)[:-1, :] / np.diff(y, axis=0)[:, :-1]

    # plot histogram
    plt.figure(0)
    ax = plt.gca()
    n, bins, patches = plt.hist(ar.flatten(), 100, density=True, facecolor=cmap[0])
    plt.xlabel(r"aspect ratio", fontsize=22, fontweight="bold")
    plt.ylabel(r"Frequency", fontsize=22, fontweight="bold")
    plt.setp(ax.get_xmajorticklabels(), fontsize=18, fontweight="bold")
    plt.setp(ax.get_ymajorticklabels(), fontsize=18, fontweight="bold")
    plt.tight_layout()
    plt.savefig("hist_ar{0:d}.png".format(aspect), format="png", dpi=300)
    plt.clf()

    return np.min(ar), np.max(ar), np.mean(ar)


# ========================================================================
def parse_time_nalu(fname):
    with open(fname, "r") as f:
        for line in f:
            if "STKPERF: Total Time:" in line:
                return float(line.split()[-1])
    return np.nan


# ========================================================================
def parse_time_nek(fname):
    with open(fname, "r") as f:
        for line in f:
            if "total elapsed time" in line:
                return float(line.split()[-2])
    return np.nan


# ========================================================================
#
# Main
#
# ========================================================================
if __name__ == "__main__":

    # ========================================================================
    # Parse arguments
    parser = argparse.ArgumentParser(description="A simple plot tool")
    parser.add_argument("-s", "--show", help="Show the plots", action="store_true")
    args = parser.parse_args()

    # ======================================================================
    # Setup
    fields = ["u", "v", "dpdx", "dpdy"]
    edf = []
    tfinal = 0.009765625

    # Get min/max/mean aspect ratios
    aspects = {}
    mdir = os.path.abspath("mesh")
    for j, aspect in enumerate([1, 10, 100, 1000, 10000]):
        mname = os.path.join(mdir, "mesh_512x512_{0:d}.exo".format(aspect))
        aspects[aspect] = get_aspect_ratio(mname, aspect)

    # ======================================================================
    # Load nalu and nek data
    methods = [
        "edge",
        "cvfem",
        "cvfemshifted",
        "cvfemsegregated",
        "edgesegregated",
        "nek",
    ]
    for i, method in enumerate(methods):
        for j, aspect in enumerate(sorted(aspects)):

            if method == "nek":
                ename = os.path.join(method, "ar{0:d}".format(aspect), "error.dat")
                lname = os.path.join(method, "ar{0:d}".format(aspect), "run.out")
                df = pd.read_csv(ename, delim_whitespace=True)
                df = df.rename(index=str, columns={"time": "Time"})
                df = pd.melt(df, id_vars=["Time"], var_name="Field", value_name="L2")
                walltime = parse_time_nek(lname)

            else:
                ename = os.path.join(method, "ar{0:06d}".format(aspect), "ctv.dat")
                lname = os.path.join(method, "ar{0:06d}".format(aspect), "ctv.log")
                df = parse_error(ename)
                walltime = parse_time_nalu(lname)

            df["aspect"] = aspect
            df["min_aspect"] = aspects[aspect][0]
            df["max_aspect"] = aspects[aspect][1]
            df["avg_aspect"] = aspects[aspect][2]
            df["method"] = method
            df["walltime"] = walltime
            edf.append(df)

    # Concatenate all
    edf = pd.concat(edf, ignore_index=True, sort=False)
    np.set_printoptions(linewidth=100)

    # ======================================================================
    # Plot

    # Plot field errors
    for i, field in enumerate(fields):
        for j, method in enumerate(methods):
            subdf = edf[(edf.Field == field) & (edf.method == method)]
            gsubdf = subdf.groupby(["aspect"], sort=False)["Time"].idxmax()
            subdf = edf.loc[gsubdf.values]
            subdf.loc[np.fabs(subdf.Time - tfinal) > 1e-5, ["L1", "L2", "Loo"]] = np.nan

            plt.figure(i)
            p = plt.loglog(
                subdf.aspect,
                subdf.L2,
                lw=2,
                color=cmap[j],
                marker=markertype[j],
                mec=cmap[j],
                mfc=cmap[j],
                ms=10,
                label=method,
            )

    # Plot walltime
    subdf = edf.drop_duplicates(subset=["aspect", "method", "walltime"]).groupby(
        ["method"], sort=False
    )
    for j, (name, group) in enumerate(subdf):
        plt.figure(len(fields) + 1)
        p = plt.loglog(
            group.aspect,
            group.walltime,
            lw=2,
            color=cmap[j],
            marker=markertype[j],
            mec=cmap[j],
            mfc=cmap[j],
            ms=10,
            label=group.method.iloc[0],
        )

    # ======================================================================
    # Format plots
    plt.figure(0)
    ax = plt.gca()
    plt.xlabel(r"max aspect ratio", fontsize=22, fontweight="bold")
    plt.ylabel(r"$L_2(u)$", fontsize=22, fontweight="bold")
    plt.setp(ax.get_xmajorticklabels(), fontsize=18, fontweight="bold")
    plt.setp(ax.get_ymajorticklabels(), fontsize=18, fontweight="bold")
    legend = ax.legend(loc="best")
    ax.set_ylim([1e-6, 1e-1])
    plt.tight_layout()
    plt.savefig("u_norm.png", format="png", dpi=300)

    plt.figure(1)
    ax = plt.gca()
    plt.xlabel(r"max aspect ratio", fontsize=22, fontweight="bold")
    plt.ylabel(r"$L_2(v)$", fontsize=22, fontweight="bold")
    plt.setp(ax.get_xmajorticklabels(), fontsize=18, fontweight="bold")
    plt.setp(ax.get_ymajorticklabels(), fontsize=18, fontweight="bold")
    legend = ax.legend(loc="best")
    ax.set_ylim([1e-6, 1e-1])
    plt.tight_layout()
    plt.savefig("v_norm.png", format="png", dpi=300)

    plt.figure(2)
    ax = plt.gca()
    plt.xlabel(r"max aspect ratio", fontsize=22, fontweight="bold")
    plt.ylabel(r"$L_2\left(\frac{dp}{dx}\right)$", fontsize=22, fontweight="bold")
    plt.setp(ax.get_xmajorticklabels(), fontsize=18, fontweight="bold")
    plt.setp(ax.get_ymajorticklabels(), fontsize=18, fontweight="bold")
    legend = ax.legend(loc="best")
    ax.set_ylim([1e-4, 1e-2])
    plt.tight_layout()
    plt.savefig("dpdx_norm.png", format="png", dpi=300)

    plt.figure(3)
    ax = plt.gca()
    plt.xlabel(r"max aspect ratio", fontsize=22, fontweight="bold")
    plt.ylabel(r"$L_2\left(\frac{dp}{dy}\right)$", fontsize=22, fontweight="bold")
    plt.setp(ax.get_xmajorticklabels(), fontsize=18, fontweight="bold")
    plt.setp(ax.get_ymajorticklabels(), fontsize=18, fontweight="bold")
    legend = ax.legend(loc="best")
    ax.set_ylim([1e-4, 1e0])
    plt.tight_layout()
    plt.savefig("dpdy_norm.png", format="png", dpi=300)

    plt.figure(len(fields) + 1)
    ax = plt.gca()
    plt.xlabel(r"max aspect ratio", fontsize=22, fontweight="bold")
    plt.ylabel(r"$t$", fontsize=22, fontweight="bold")
    plt.setp(ax.get_xmajorticklabels(), fontsize=18, fontweight="bold")
    plt.setp(ax.get_ymajorticklabels(), fontsize=18, fontweight="bold")
    legend = ax.legend(loc="best")
    plt.tight_layout()
    plt.savefig("walltime.png", format="png", dpi=300)
