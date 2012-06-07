
import os, time
from optparse import OptionParser

from metisreader import MetisReader
from nsdp import generate_problem, NSDP
from cvxopt import matrix, spmatrix, printing

import networkx
import matplotlib.pyplot as pyplot
import pymetis
import chompack
import md
from minfill import *
from lex_bfs import *

global options

def usage():
    return """[options] files"""
# usage()

def touch(target_path):
    global options
    metis_path = None
    print "Touch file '%s'" % target_path
    target_basename, target_ext = os.path.splitext(target_path)
    print "Read graph"
    reader = MetisReader(target_path, input_format=options.format)
    if options.format != 'metis':
        metis_path = target_basename + ".metis"
        reader.save_as(metis_path)
    else:
        metis_path = target_path
    print "\tNumber of vertices:", reader.get_number_vertices()
    print "\tNumber of edges:", reader.get_number_edges()
    (objective, constraints) = generate_problem(reader.get_graph())
    print "\tNumber of constraints:", len(constraints)
    exit()
    print "Generate problem"
    problem = NSDP(objective, constraints)
    # Draw and save the interaction graph
    gfile_path = target_basename + ".png"
    print "Draw and save interaction graph as '%s'" % gfile_path
    networkx.draw(problem.get_interaction_graph(), node_size=400, node_color='w')
    pyplot.savefig(gfile_path)
    pyplot.clf()
    # Perform the tests
    run("MD", problem, get_md_ordering, [metis_path])
    run("ND", problem, get_nd_ordering, [reader])
    run("MCS", problem, get_mcs_ordering, [reader])
    run("MF", problem, get_minfill_ordering, [reader])
    run("LBFS", problem, get_lbfs_ordering, [reader])
# touch()

def get_md_ordering(f):
    return list(md.md_ordering(f))

def get_nd_ordering(reader):
    (perm, iperm) = pymetis.egde_md(reader.get_adjacency())    
    return perm

def get_lbfs_ordering(reader):
    return lex_bfs(reader.get_graph())

def get_mcs_ordering(reader):
    V = []
    I = []
    J = []
    for node in reader.get_graph().nodes():
        for neighbor in reader.get_graph().neighbors(node) + [node]:
            V.append(1.0)
            J.append(node)
            I.append(neighbor)
    A = spmatrix(V, I, J)
    return chompack.maxcardsearch(A)

def get_minfill_ordering(reader):
    (fillins, order) = minfill(reader.get_graph())
    return order

def run(info, problem, f, f_args):
    order = res = f(*f_args)
    elimination_order = ["x%d" % _ for _ in order]
    found_value = problem.profile_eval(elimination_order)
    found_solution = problem.get_solution()
    print info
    #print "\tOrder:", elimination_order
    print "\tValue:", found_value
    #print "\tSolution:", [found_solution[_] for _ in sorted(found_solution)]
    print "\tTime: %0.3f sec = %0.3f min" % (problem.estimated_time, problem.estimated_time / 60.0)
# run()

def main():
    global options
    parser = OptionParser(usage=usage())
    parser.add_option("-v", "--verbose", action="store_true", dest="verbose", default=False)
    parser.add_option("-f", "--format", metavar="FORMAT", default="METIS")
    (options, args) = parser.parse_args()
    for fpath in args:
        touch(fpath)
# main()

if __name__=='__main__':
    print time.ctime()
    main()
    print time.ctime()
    exit(0)
