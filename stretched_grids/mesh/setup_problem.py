#!/usr/bin/env python3
"""Setup the convective Taylor vortex problem
"""

# ========================================================================
#
# Imports
#
# ========================================================================
import os
import yaml
import numpy as np
import subprocess as sp

from numpy.polynomial import Polynomial as P
from scipy.optimize import fsolve

# ========================================================================
#
# Setup
#
# ========================================================================
N = [512, 512, 1]
Lx = 2.0
dx = Lx / N[0]

# Solve for the stretching factor, given the aspect ration and
# assuming bidirectional stretching.
aspect = 1
fch = (dx/aspect)/Lx  # must be in Lx units
tlen = 0.5
L = [Lx, Lx, fch]

coeffs = np.zeros(int(N[0]/2)+1)
coeffs[-1] = fch
coeffs[1] = -tlen
coeffs[0] = -fch+tlen

p = P(coeffs)
res = p.roots()
factor = np.float(np.real(res[np.imag(res) == 0])[1])

dbname = 'mesh_{0:d}x{1:d}_{2:d}'.format(N[0], N[1], aspect)
msh_dbname = dbname + ".exo"

# Get executables
home = os.path.expanduser("~")
winddir = os.path.join(home, 'wind/NaluWindUtils/build/src')
spackbin = os.path.join(home, 'spack/bin/spack')
proc = sp.Popen(spackbin + ' location -i openmpi ',
                shell=True,
                stdout=sp.PIPE,
                stderr=sp.PIPE)
out, err = proc.communicate()
errcode = proc.returncode
mpidir = out.decode('utf-8').strip()
mpibin = os.path.join(mpidir, 'bin/mpiexec')
abl_mesh = os.path.join(winddir, 'mesh/abl_mesh')
nalu_preprocess = os.path.join(winddir, 'preprocessing/nalu_preprocess')

# ========================================================================
#
# Generate new mesh and IC files
#
# ========================================================================

# Load the skeleton data
msh_iname = "mesh.yaml"
msh_inp = yaml.load(open(msh_iname, 'r'))
msh_data = msh_inp['nalu_abl_mesh']

# New yaml mesh file
msh_oname = "msh_tmp.yaml"
msh_data['output_db'] = msh_dbname
vertices = msh_data['vertices']
vertices[1][0] = L[0]
vertices[1][1] = L[1]
vertices[1][2] = L[2]
msh_data['mesh_dimensions'] = N
y_spacing = msh_data['y_spacing']
y_spacing['stretching_factor'] = factor


with open(msh_oname, 'w') as of:
    yaml.dump(msh_inp, of, default_flow_style=False)


# ========================================================================
#
# Run the utilities
#
# ========================================================================

proc = sp.Popen(mpibin + ' -np 1 ' + abl_mesh + ' -i ' + msh_oname,
                shell=True,
                stderr=sp.PIPE)
err = proc.communicate()
errcode = proc.returncode

# ========================================================================
#
# Clean up
#
# ========================================================================
os.remove(msh_oname)
