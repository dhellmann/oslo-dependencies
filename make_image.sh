#!/bin/sh

set -ex

function draw {
    typeset base=$1
    dot -Tpng -o${base}.png ${base}.dot
    neato -Tpng -o${base}_neato.png ${base}.dot
    twopi -Tpng -o${base}_twopi.png ${base}.dot
    circo -Tpng -o${base}_circo.png ${base}.dot
}

depend_graph.py > modules.dot
draw modules

lib_graph.py > libs.dot
draw libs
