#!/usr/bin/env python
"""Produce a dependency graph in the DOT language.
"""
import collections
import itertools
import fileinput


def get_deps_by_module(infile):
    library_name = None
    dependencies = {}
    for n, line in enumerate(fileinput.input(infile)):
        if line.startswith('== '):
            # New lib
            library_name = line.strip().strip('=').strip()
            module_name = None
        elif line.startswith('=== '):
            # New module
            module_name = line.strip().strip('=').strip()
            dependencies[module_name] = []
        elif line.startswith(':Depends on:'):
            # Dependencies
            if not module_name:
                raise ValueError('found dependencies on line %d without a module' % n)
            depstr = line.rpartition(':')[-1].strip()
            if depstr != '(none)':
                deps = [d.strip() for d in depstr.split(',')]
                dependencies[module_name] = deps
    return dependencies

def print_graph(dependencies):
    node_namer = iter('N%d' % i for i in itertools.count())
    names = collections.defaultdict(node_namer.next)

    print 'digraph oslo {'

    nodes = set()

    # Generate node label statements
    for mod, deps in sorted(dependencies.items()):
        if mod not in nodes:
            print '  %s [ label = "%s" ];' % (names[mod], mod)
            nodes.add(mod)
        for d in deps:
            if d not in nodes:
                print '  %s [ label = "%s" ];' % (names[d], d)
                nodes.add(d)
                
    print

    # Generate the edges
    for mod, deps in sorted(dependencies.items()):
        if mod not in names:
            names[mod] = node_namer.next()
        for d in deps:
            if d not in names:
                names[d] = node_namer.next()
            print '  %s -> %s;' % (names[mod], names[d])

    print '}'


dependencies = get_deps_by_module('status.txt')
print_graph(dependencies)
