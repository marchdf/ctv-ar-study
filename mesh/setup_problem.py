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

# ========================================================================
#
# Setup
#
# ========================================================================
aspect_ratio = 1

Ny = 1024
Ly = 2
dy = Ly / Ny
Nx = int(Ny / aspect_ratio)
dx = Ly / Nx

L = [Ly, Ly, dy]
N = [Nx, Ny, 1]

dbname = 'mesh_{0:d}x{1:d}'.format(N[0], N[1])
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
