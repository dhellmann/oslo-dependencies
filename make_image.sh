#!/bin/sh

set -ex

format=$1
if [ -z "$format" ]
then
    format="png"
fi

function draw {
    typeset base=$1
    dot -T${format} -o${base}.${format} ${base}.dot
#    neato -T${format} -o${base}_neato.${format} ${base}.dot
#    twopi -T${format} -o${base}_twopi.${format} ${base}.dot
    circo -T${format} -o${base}_circo.${format} ${base}.dot
}

depend_graph.py > modules.dot
draw modules

lib_graph.py > libs.dot
draw libs

lib_graph_verbose.py > libs_verbose.dot
draw libs_verbose

lib_graph_uncluttered.py > libs_uncluttered.dot
draw libs_uncluttered
