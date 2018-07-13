#!/bin/bash
#
# Generate all the meshes

# temporary files
gfile="input_genbox"
tfile="box.re2"

# Generate the .rea files from the coordinate files
aspects=(1 10 100 1000 10000)
for aspect in "${aspects[@]}"
do
    cfile="xy_coords_${aspect}.dat"
    bfile="ctv_${aspect}.box"
    rfile="ctv_${aspect}.re2"
    python write_box_input_file.py -i ${cfile} -o ${bfile}
    echo ${bfile} > ${gfile}
    genbox < ${gfile}
    mv ${tfile} ${rfile}
done

# Clean up
rm ${gfile} box.tmp
