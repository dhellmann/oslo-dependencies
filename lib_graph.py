#!/usr/bin/env python
"""Produce a dependency graph in the DOT language.
"""
import collections
import itertools
import fileinput

NOT_LIB = set([
    'Undecided',
    #'oslo.server',
    #'oslo.utils',
    #'oslo.concurrency',
])

def get_deps_by_module(infile):
    library_name = None
    dependencies = {}
    libraries = {}
    for n, line in enumerate(fileinput.input(infile)):
        if line.startswith('== '):
            # New lib
            library_name = line.strip().strip('=').strip()
            if library_name not in NOT_LIB:
                libraries[library_name] = []
            module_name = None
        elif line.startswith('=== '):
            # New module
            module_name = line.strip().strip('=').strip()
            if library_name in NOT_LIB:
                libraries[module_name] = []
            else:
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
def generate_node(label, shape='oval'):
    if label not in _known_nodes:
        print '  %s [ label = "%s", shape=%s ];' % (_node_names[label], label, shape)
        _known_nodes.add(label)

    
def print_graph(libraries, dependencies):

    # Invert the library contents so we can link
    # to the library instead of its contents
    mods_to_lib = {}
    for name, modules in sorted(libraries.items()):
        for mod in modules:
            mods_to_lib[mod] = name

    print 'digraph oslo {'

    # Represent the module dependencies as library dependencies
    # with the module name as the edge label
    edges = set()
    for mod, deps in sorted(dependencies.items()):
        src_lib_name = mods_to_lib.get(mod, mod)
        #generate_node(src_lib_name)
        src_lib = _node_names[src_lib_name]
        for d in deps:
            dest_lib_name = mods_to_lib.get(d, d)
            if dest_lib_name == src_lib_name:
                continue
            #generate_node(dest_lib_name)
            dest_lib = _node_names[dest_lib_name]
            #edge = '%s -> %s [ label = "%s" ];' % (src_lib, dest_lib, d)
            edge = '%s -> %s;' % (src_lib, dest_lib)
            if edge not in edges:
                generate_node(src_lib_name)
                generate_node(dest_lib_name)
                print edge
                edges.add(edge)

    print '}'


libraries, dependencies = get_deps_by_module('status.txt')
print_graph(libraries, dependencies)
