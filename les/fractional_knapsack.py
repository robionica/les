#!/usr/bin/env python

__copyright__ = "Copyright (c) 2012 Alexander Sviridenko"

def fractional_knapsack(v, w, W):
    """Return result vector and solution of the fractional knapsack
    problem.

    There are n items in a bag. For i=1, 2, ..., n, item i has weight
    w[i] > 0 and worth v[i] > 0. Thief can carry a maximum weight of W
    pounds in a knapsack. In this version of a problem the items can
    be broken into smaller piece, so the thief may decide to carry
    only a fraction x[i] of object i, where 0 <= x[i] <= 1. Item i
    contributes x[i] * w[i] to the total weight in the knapsack, and
    x[i] * v[i] to the value of the bag."""
    assert len(v) == len(w), "The number of values and weights are not equal"
    n = len(v) # count items
    x = [0] * n
    o = range(n) # order
    o.sort(lambda x, y: cmp(float(v[x]) / float(w[x]), \
                                float(v[y]) / float(w[y])), reverse=True)


    t = 0
    s = 0 # solution so far
    while t < W and len(o):
        i = o.pop(0) # take best remaining item
        if (t + w[i]) <= W:
            x[i] = 1
            t += w[i]
            s += v[i]
        else:
            x[i] = (W - t) / w[i]
            t = W
    return (x, s)

if __name__ == "__main__":
    #print fractional_knapsack([8,2,5,5], [3,5,7,3], 13)
    #print fractional_knapsack([8,3,9], [4,6,7], 8)
    #print fractional_knapsack([7,6], [5,3], 8)
    ##
    print fractional_knapsack([2, 3, 1], [3, 4, 1], 6)
    print fractional_knapsack([5, 4, 6, 1], [3, 3, 3, 2], 5)
