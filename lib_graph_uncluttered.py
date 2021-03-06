#!/usr/bin/env python
"""Produce a dependency graph in the DOT language.
"""
import collections
import itertools
import fileinput

def get_deps_by_module(infile):
    library_name = None
    module_name = None
    dependencies = {}
    libraries = {}
    for n, line in enumerate(fileinput.input(infile)):
        if line.startswith('== '):
            # New lib
            library_name = line.strip().strip('=').strip()
            if library_name.startswith('INCUBATOR:'):
                library_name = None
                continue
            libraries[library_name] = {
                'status': 'dev',
                'modules': [],
            }
            module_name = None
        elif library_name and line.startswith('=== '):
            # New module
            module_name = line.strip().strip('=').strip()
            libraries[library_name]['modules'].append(module_name)
            dependencies[module_name] = []
        elif not module_name and line.startswith(':S:'):
            # library status
            libraries[library_name]['status'] = line.rsplit(':', 1)[-1].strip() or 'dev'
        elif line.startswith(':Depends on:'):
            # Dependencies
            if not module_name:
                raise ValueError('found dependencies on line %d without a module' % n)
            depstr = line.rpartition(':')[-1].strip()
            if depstr != '(none)':
                deps = [d.strip() for d in depstr.split(',')]
                dependencies[module_name] = deps
    return libraries, dependencies


_node_colors = {
    'dev': ('lightgrey', 'black'),
    'Released': ('steelblue', 'white'),
    'Graduating': ('orange', 'black'),
    'Deleting': ('crimson', 'white'),
    'Next': ('yellow', 'black'),
    'Incubating': ('lightgrey', 'red'),
}

_node_namer = iter('N%d' % i for i in itertools.count())
_node_names = collections.defaultdict(_node_namer.next)
_known_nodes = set()
def generate_node(label, shape='oval', bgcolor='white', fgcolor='black'):
    if label not in _known_nodes:
        print '  %s [ label = "%s", shape=%s, color=%s, fontcolor=%s style=filled ];' % \
            (_node_names[label], label, shape, bgcolor, fgcolor)
        _known_nodes.add(label)


def print_graph(libraries, dependencies):

    # Invert the library contents so we can link
    # to the library instead of its contents
    mods_to_lib = {}
    for name, attrs in sorted(libraries.items()):
        for mod in attrs['modules']:
            mods_to_lib[mod] = name

    print 'digraph oslo {'

    # Build color map for library nodes and generate nodes for
    # anything that is a dependency of another module.
    lib_colors = {}
    libs_we_want = set()
    for mod, deps in sorted(dependencies.items()):
        src_lib_name = mods_to_lib.get(mod, mod)
        if src_lib_name in lib_colors:
            bg, fg = lib_colors[src_lib_name]
        else:
            bg, fg = _node_colors.get(libraries[src_lib_name]['status'],
                                      ('white', 'black'))
            lib_colors[src_lib_name] = (bg, fg)
        if deps:
            libs_we_want.add(src_lib_name)
            for d in deps:
                libs_we_want.add(mods_to_lib.get(d, d))
    for name, attrs in sorted(libraries.items()):
        bg, fg = _node_colors.get(attrs['status'], ('white', 'black'))
        lib_colors[name] = (bg, fg)

    for l in libs_we_want:
        if l not in libraries:
            continue
        bg, fg = lib_colors[l]
        generate_node(l, bgcolor=bg, fgcolor=fg)

    # Represent the module dependencies as library dependencies
    # with the module name as the edge label
    edges = set()
    for mod, deps in sorted(dependencies.items()):
        src_lib_name = mods_to_lib.get(mod, mod)
        src_lib = _node_names[src_lib_name]
        for d in deps:
            dest_lib_name = mods_to_lib.get(d, d)
            if dest_lib_name == src_lib_name:
                continue
            if dest_lib_name not in libraries:
                continue
            dest_lib = _node_names[dest_lib_name]
            edge = '%s -> %s;' % (src_lib, dest_lib)
            if edge not in edges:
                generate_node(src_lib_name)
                generate_node(dest_lib_name)
                print edge
                edges.add(edge)

    print '}'


libraries, dependencies = get_deps_by_module('status.txt')
print_graph(libraries, dependencies)
