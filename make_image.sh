#!/bin/sh

depend_graph.py > graph.dot
dot -Tpng -ograph.png graph.dot
