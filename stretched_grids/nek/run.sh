#!/bin/bash
NPROC=$1
PROBLEMNAME=ctv
echo ${PROBLEMNAME} > input_genmap
echo 0.0000000001 >> input_genmap
genmap < input_genmap
echo ${PROBLEMNAME} > SESSION.NAME
echo $PWD >> SESSION.NAME
./makenek ${PROBLEMNAME}
mpirun -n ${NPROC} ./nek5000
visnek ${PROBLEMNAME}
