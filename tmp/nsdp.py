"""Nonserial Dynamic Programming (NSDP)."""

import sys, time, copy, random
import operator
from types import *
from threading import Thread

# This NSDP implementation is using networkx library for graph manipulations.
# Learn more about networkx here http://networkx.lanl.gov/tutorial/tutorial.html
import networkx
from networkx import Graph
from networkx.algorithms.components.connected import is_connected
from networkx.algorithms.clique import find_cliques
import matplotlib.pyplot as pyplot

import util

#_______________________________________________________________________________
# Use meta-language for problem description

class Element(object):
    def __init__(self):
        pass

    def eval(self, env={}):
        pass

class Expression(Element):
    def __init__(self, children=[]):
        Element.__init__(self)
        self._children = children

    def profile_eval(self, env={}, depth=1):
        self.estimated_time = 0
        start_time = time.time()
        res = self.eval(env)
        end_time = time.time()
        self.estimated_time = end_time - start_time        
        return res

    def find(self, klass):
        result = set()
        children = [self]
        while True:
            if not len(children):
                break
            node = children.pop(0)
            if isinstance(node, klass):
                result.add(node)
            children.extend(node.get_children())
        return list(result)

    def get_children(self):
        return self._children

    def __rmul__(self, expr):
        if isinstance(expr, Const):
            return expr * self
        return Mul(self, expr)

    def __mul__(self, expr):
        if isinstance(expr, Const):
            return expr * self
        return Mul(self, expr)

    def __add__(self, expr):
        if isinstance(expr, Const):
            return expr + self
        return Add(self, expr)

    def __call__(self):
        return

    def __radd__(self, expr):
        return Add(expr, self)

    def __le__(self, expr):
        return LessOrEqual(self, expr)

    def __repr__(self):
        return "Unknown expression"

    def __setitem__(self, key, expr):
        for i in range(len(self._children)):
            if Symbol.__instancecheck__(self._children[i]) and str(self._children[i].get_value()) == str(key):
                kill = self._children[i]
                self._children[i] = expr
                del kill
            else:
                self._children[i].__setitem__(key, expr)
               
class Const(Expression):
    def __init__(self, value):
        Expression.__init__(self, [])
        self._value = value

    def eval(self, env={}):
        return self._value

    def get_value(self):
        return self._value

    def __call__(self):
        return self

    def __repr__(self):
        return "%d" % self.get_value()

    def __radd__(self, expr):
        if self.get_value() == 0:
            return expr
        if isinstance(expr, Const):
            return Const(self.get_value() + expr.get_value())
        return Expression.__radd__(self, expr)

    def __add__(self, expr):
        if self.get_value() == 0:
            return expr
        if isinstance(expr, Const):
            return Const(self.get_value() + expr.get_value())
        return Expression.__add__(self, expr)

    def __rmul__(self, expr):
        if isinstance(expr, Const):
            return Const(self.get_value() * expr.get_value())
        return Expression.__mul__(self, expr)

    def __mul__(self, expr):
        if isinstance(expr, Const):
            return Const(self.get_value() * expr.get_value())
        return Expression.__mul__(self, expr)

class BinaryOp(Expression):
    def __init__(self, left, right):
        Expression.__init__(self, [left, right])

    def get_left(self):
        return self._children[0]

    def get_right(self):
        return self._children[1]

    def get_children(self):
        return [self.get_left(), self.get_right()]

class LessOrEqual(BinaryOp):
    def __init__(self, left, right):
        BinaryOp.__init__(self, left, right)

    def __call__(self):
        return self.get_left().__call__() <= self.get_right().__call__()

    def eval(self, env={}):
        return self.get_left().eval(env) <= self.get_right().eval(env)

    def __repr__(self):
        return "%s <= %s" % (repr(self.get_left()), repr(self.get_right()))

    def __deepcopy__(self, memo):
        left = copy.deepcopy(self.get_left(), memo)
        right = copy.deepcopy(self.get_right(), memo)
        expr = LessOrEqual(left, right)
        return expr

class Mul(BinaryOp):
    """Multiplication. Binary operation."""
    def __init__(self, left, right):
        BinaryOp.__init__(self, left, right)

    def __call__(self):
        return self.get_left().__call__() * self.get_right().__call__()

    def eval(self, env={}):
        return self.get_left().eval(env) * self.get_right().eval(env)

    def __repr__(self):
        """Representation view: [(]expression[)] * [(]expression[)]"""
        output = ""
        if isinstance(self.get_left(), BinaryOp): 
            output = output + "(%s)" % self.get_left()
        else: 
            output = output + "%s" % self.get_left()
        output = output + " * "
        if isinstance(self.get_right(), BinaryOp): 
            output = output + "(%s)" % self.get_right()
        else: 
            output = output + "%s" % self.get_right()
        return output

    def __deepcopy__(self, memo):
        """Utility method used by copy.deepcopy()"""
        left = copy.deepcopy(self.get_left(), memo)
        right = copy.deepcopy(self.get_right(), memo)
        expr = Mul(left, right)
        return expr

class Add(BinaryOp):
    def __init__(self, left, right):
        BinaryOp.__init__(self, left, right)

    def __call__(self):
        return (self.get_left().__call__() + self.get_right().__call__())

    def eval(self, env):
        return self.get_left().eval(env) + self.get_right().eval(env)

    def __repr__(self):
        return "%s + %s" % (self.get_left().__repr__(), self.get_right().__repr__())

    def __deepcopy__(self, memo):
        """Utility method used by copy.deepcopy()"""
        left = self.get_left().__deepcopy__(memo)
        right = copy.deepcopy(self.get_right(), memo)
        expr = Add(left, right)
        return expr

class Symbol(Expression):
    def __init__(self, symb):
        Expression.__init__(self, [])
        self._symb = symb

    def get_value(self):
        return self._symb

    def __call__(self):
        return self

    def eval(self, env):
        if env.has_key(str(self)):
            return env[str(self)]
        assert False, "Should not appeard"

    def __repr__(self):
        return "%s" % self._symb

    def __deepcopy__(self, memo):
        """Utility method used by copy.deepcopy()"""
        expr = Symbol(self.get_value())
        return expr

class Function(Expression):
    def __init__(self):
        Expression.__init__(self)

    def __repr__(self):
        return "Unknown function"

#_______________________________________________________________________________

def generate_problem(graph):
    "Generate NSDP problem by a given graph."
    assert isinstance(graph, Graph), "networkx graph is required"
    objective = Const(0)
    constraints = []
    # Obtain cliques. See more about an algorithm 
    # http://networkx.lanl.gov/reference/generated/networkx.algorithms.clique.find_cliques.html
    cliques = list(find_cliques(graph))
    # Build objective function
    for i in range(graph.number_of_nodes()):
        objective = objective + Const(random.randint(1, graph.number_of_nodes())) * Symbol("x%d" % i)
    # Build constraints. Each constraint is represented by a single clique
    for clique in cliques:
        expr = Const(0)
        A = []
        for variable in clique:
            k = random.randint(1, random.randint(1, graph.number_of_nodes()-1))
            A.append(k)
            expr += Const(k) * Symbol("x%d" % variable)
        constraint = expr <= Const(int(random.random() * sum(A)))
        constraints.append(constraint)
    return (objective, constraints)
# generate_problem()

def build_interaction_graph(constraints):
    """Build an interaction graph by a given constraints. The graph has to be
    undirected, strict and connected graph."""
    graph = Graph()
    for constraint in constraints:
        variables = [repr(_) for _ in constraint.find(Symbol)]
        for variable in variables:
            for neighbor in variables:
                if variable == neighbor:
                    continue
                graph.add_edge(variable, neighbor)
    assert is_connected(graph), "Graph is not connected!"
    return graph
# build_interaction_graph()

#_______________________________________________________________________________

class NSDP(Function):
    """NSDP"""
    _objective = None
    _constraints = None
    _graph = None # interaction graph
    _solution = {}
    _buckets = []
    _bucketmap = {}

    def __init__(self, objective, constraints):
        Function.__init__(self)
        self.reset(objective, constraints)
    # __init__()

    def reset(self, objective=None, constraints=[]):
        if objective:
            self._objective = objective
        if len(constraints):
            self._constraints = constraints
        self._graph = build_interaction_graph(self._constraints)
        self._solution = {}
        self._buckets = []
        self._bucketmap = {}
    # reset()
    
    def get_solution(self): 
        return self._solution

    def get_objective(self): 
        return self._objective

    def get_interaction_graph(self):
        return self._graph

    def get_buckets(self):
        return self._buckets

    def eval(self, order, limit=10):
        """Evaluate NSDP problem."""
        self.reset()
        assert len(order), "Elimination order has not been provided"
        available_constraints = copy.deepcopy(self._constraints)
        queue = copy.copy(order)
        # Variables and constraints to be eliminated
        eliminate_variables = []
        eliminate_constraints = []
        eliminate_neighbors = []
        # Forward part
        # Loop while we are doing elimination
        while True:
            next_variable = queue.pop(0)
            eliminate_variables.append(next_variable)
            # Finish elimination if no variables left
            if not len(queue):
                self.eliminate(eliminate_variables, eliminate_constraints)
                break
            if len(eliminate_variables) > 1:
                if (len(eliminate_variables) 
                    + len(set(eliminate_neighbors) | set(self._graph.neighbors(next_variable)))) >= limit:
                    eliminate_variables.pop()
                    self.eliminate(eliminate_variables, eliminate_constraints)
                    eliminate_variables = [next_variable]
                    eliminate_constraints = []
                    eliminate_neighbors = []
            eliminate_neighbors = list(set(eliminate_neighbors) | set(self._graph.neighbors(next_variable)))
            # Get next constraints in which variable involved
            next_constraints = []
            # Go throw available constraints and take though of them which 
            # contains eliminated variable. We will take them all.
            for _ in range(len(available_constraints)):
                constraint = available_constraints.pop()
                if next_variable in [repr(_) for _ in constraint.find(Symbol)]:
                    next_constraints.append(constraint)
                else:
                    available_constraints.insert(0, constraint)
            # If we already have some constraints to be eliminated, then we have
            # to compare them with already existed. If eliminated variable 
            # depends on more constraints than the previous variables then we 
            # assume that this variable is not interract with some variable from 
            # the current elimination order.
            if len(eliminate_constraints) \
                    and len(set(next_constraints) - set(eliminate_constraints)):
                # Remove last variable from elimination order and perform 
                # elimination to rest of them
                eliminate_variables.pop()
                self.eliminate(eliminate_variables, eliminate_constraints)
                # Go back to the elimination process but only with the 
                # last variable and their constraints
                eliminate_variables = [next_variable]
                eliminate_constraints = next_constraints
            else:
                # Add them all
                eliminate_constraints.extend(next_constraints)
            # Perform elimination if:
            # 1. There is only one variable left
            # 2. The next variable to be eliminated is not a neighbor of the 
            #    current one.
            neighbors = self._graph.neighbors(next_variable)
            if len(neighbors) == 1 or queue[0] not in neighbors \
                    or len(queue) == 1:
                eliminate_constraints = list(set(eliminate_constraints))
                self.eliminate(eliminate_variables, eliminate_constraints)
                eliminate_variables = []
                eliminate_constraints = []
        # Backward part
        # We need to wait first for of the buckets
        for bucket in self.get_buckets():
            bucket.join()
        # Get the solution and return the result value
        for _ in reversed(range(len(self.get_buckets()))):
            self._solution.update(self._buckets[_].get_solution(self._solution))
        return self._buckets[-1].eval()
    # eval()

    def eliminate(self, variables, constraints):
        """Elimination operator."""
        # Get a set of neighbors at the current elimination graph for a 
        # given elimination sequence
        neighbors = set()
        for variable in variables:
            for neighbor in self._graph.neighbors(variable):
                neighbors.add(neighbor)
        neighbors = list(neighbors) # set() --> list()
        # Remove from the neighborhood the variables which will be eliminated
        neighbors[:] = [nb for nb in neighbors if nb not in variables]
        # Start to build a new objective function for the current subproblem
        objective = copy.deepcopy(self._objective)
        for variable in [repr(_) for _ in self._objective.find(Symbol)]:
            if variable not in variables:
                objective[variable] = Const(0)
        # Connect objective function with related subproblems
        dependencies = set()
        for (variable, buckets) in self._bucketmap.iteritems():
            if variable in variables:
                for bucket in buckets:
                    dependencies.add(bucket)
        for (variable, buckets) in self._bucketmap.iteritems():
            self._bucketmap[variable] = list(set(buckets) - set(dependencies))
        # Connect dependencies with objective function
        for bucket in list(dependencies):
            objective = objective + bucket
        # Create a new bucket and start the thread which holds it
        bucket = Bucket(objective, variables, neighbors, constraints, \
                            list(dependencies))
        bucket.start() 
        self._buckets.append(bucket)
        # Register our subproblem in a bucket map
        for variable in neighbors:
            if self._bucketmap.has_key(variable):
                self._bucketmap[variable].append(bucket)
            else:
                self._bucketmap[variable] = [bucket]
        # After a variable has been eliminated all the variables connected to
        # it are joined together (making the neighborhood of this variable into 
        # a clique in the remaining graph, before deleting), modifying the 
        # structure of the interaction graph.
        for variable in variables:
            neighbors = self._graph.neighbors(variable)
            for first_neighbor in neighbors:
                for second_neighbor in neighbors:
                    if first_neighbor != second_neighbor:
                        self._graph.add_edge(first_neighbor, second_neighbor)
            self.get_interaction_graph().remove_node(variable)
    # eliminate()

    def __repr__(self):
        return repr(self._objective) + " -> max" + "\n" \
            + "subject to\n\t" \
            + "\n\t".join([repr(constraint) for constraint in self._constraints])
    # __repr__()
    
class Bucket(Function, Thread):
    def __init__(self, objective, variables, neighbors, constraints, dependencies):
        Function.__init__(self)
        Thread.__init__(self)
        self._objective = objective
        self._variables = variables
        self._neighbors = neighbors
        self._constraints = constraints
        self._dependencies = dependencies
        self.reset()
    # __init__()

    def reset(self):
        self._solution = {}
        self._table = []
        self._solved = False

    def run(self):
        """Override thread method, which represents it activity."""
        self.reset()
        return self.eval()

    def get_solution(self, env={}):
        self.eval(env)
        return self._solution

    def eval(self, env={}):
        # Solve the dependencies first 
        for bucket in self._dependencies:
            bucket.join()
        if self._solved:
            if env and len(self._neighbors): # check for the neighbors
                for neighbor in self._neighbors:
                    assert env.has_key(neighbor), "Neighbor %s cannot be found" % neighbor
                i = util.bin_to_dec([env[_] for _ in self._neighbors])
            else:
                i = 0
            sorted_table = sorted(self._table[i].items(), key=operator.itemgetter(1), reverse=True)
            (j, v) = sorted_table.pop(0)
            self._solution = dict(zip(self._variables, util.dec_to_bin(j, len(self._variables))))
            return v
        # Create an assignment for neighbors
        for i in range(1<<len(self._neighbors)):
            self._table.append({})
            neighbors_assignment = dict(zip(self._neighbors, util.dec_to_bin(i, len(self._neighbors))))
            # Create an assignment for variables
            for j in range(1 << len(self._variables)):
                v = -1
                variables_assignment = dict(zip(self._variables, util.dec_to_bin(j, len(self._variables))))
                assignment = dict(neighbors_assignment, **variables_assignment)
                ok = True
                for constraint in self._constraints:
                    ok = constraint.eval(assignment)
                    if not ok:
                        break
                for dependency in self._dependencies:
                    if dependency.eval(assignment) == -1:
                        ok = False
                        break
                if ok:
                    v = self._objective.eval(assignment)
                self._table[i][j] = v
        self._solved = True
    # eval()

    def get_table(self):
        return self._table

    def __repr__(self):
        return "h_{%s}(%s)" % (self._variables, self._neighbors)

#_______________________________________________________________________________

if __name__=='__main__':
    problem = NSDP(
        Const(2) * Symbol('x0') + Const(3) * Symbol('x1') + Const(1) * Symbol('x2') 
        + Const(5) * Symbol('x3') + Const(4) * Symbol('x4') + Const(6) * Symbol('x5') + Symbol('x6'),
        [Const(3) * Symbol('x0') + Const(4) * Symbol('x1') + Symbol('x2') <= Const(6),
         Const(2) * Symbol('x1') + Const(3) * Symbol('x2') + Const(3) * Symbol('x3') <= Const(5),
         Const(2) * Symbol('x1') + Const(3) * Symbol('x4') <= Const(4),
         Const(2) * Symbol('x2') + Const(3) * Symbol('x5') + Const(2) * Symbol('x6') <= Const(5)])
    print problem
    #import matplotlib.pyplot as pyplot
    #networkx.draw(problem.get_interaction_graph())
    #pyplot.savefig("problem.png")
    value = problem.profile_eval(['x4', 'x6', 'x5', 'x3', 'x0', 'x1', 'x2'])
    print "Value    :", value
    print "Solution :", [problem.get_solution()[_] for _ in sorted(problem.get_solution())]

