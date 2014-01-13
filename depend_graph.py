#!/usr/bin/env python
"""Produce a dependency graph in the DOT language.
"""
import collections
import itertools
import fileinput


def get_deps_by_module(infile):
    library_name = None
    dependencies = {}
    libraries = {}
    for n, line in enumerate(fileinput.input(infile)):
        if line.startswith('== '):
            # New lib
            library_name = line.strip().strip('=').strip()
            libraries[library_name] = []
            module_name = None
        elif line.startswith('=== '):
            # New module
            module_name = line.strip().strip('=').strip()
            libraries[library_name].append(module_name)
            dependencies[module_name] = []
        elif line.startswith(':Depends on:'):
            # Dependencies
            if not module_name:
                raise ValueError('found dependencies on line %d without a module' % n)
            depstr = line.rpartition(':')[-1].strip()
            if depstr != '(none)':
                deps = [d.strip() for d in depstr.split(',')]
                dependencies[module_name] = deps
    return libraries, dependencies

    
_node_namer = iter('N%d' % i for i in itertools.count())
_node_names = collections.defaultdict(_node_namer.next)
_known_nodes = set()
def generate_node(label):
    if label not in _known_nodes:
        print '  %s [ label = "%s" ];' % (_node_names[label], label)
        _known_nodes.add(label)

    
def print_graph(libraries, dependencies):

    print 'digraph oslo {'

    # Each library is a subgraph
    for name, modules in sorted(libraries.items()):
        n = _node_namer.next()
        print 'subgraph %s {' % n
        print '  label = "%s";' % name
        print '  style = filled;'
        print '  color=black;'
        print '  node [style=filled,color=lightgrey];'
        for mod in modules:
            generate_node(mod)
        print '}'

    # Generate node label statements
    for mod, deps in sorted(dependencies.items()):
        generate_node(mod)
        for d in deps:
            generate_node(d)
                
    print

    # Generate the edges
    for mod, deps in sorted(dependencies.items()):
        for d in deps:
            print '  %s -> %s;' % (_node_names[mod], _node_names[d])

    print '}'


libraries, dependencies = get_deps_by_module('status.txt')
print_graph(libraries, dependencies)
