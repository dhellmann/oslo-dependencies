#!/bin/sh

set -ex

depend_graph.py > graph.dot
dot -Tpng -ograph.png graph.dot
neato -Tpng -oneato.png graph.dot
twopi -Tpng -otwopi.png graph.dot
circo -Tpng -ocirco.png graph.dot
