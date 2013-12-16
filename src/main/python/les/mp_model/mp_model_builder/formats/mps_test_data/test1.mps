* Test 1

NAME TESTPROB
ROWS
 N COST
 L LIM1
 G LIM2
 E LIM3
COLUMNS
    X      COST                 1   LIM1                 1
    X      LIM2                 1
    Y      COST                 4   LIM1                 1
    Y      LIM3                -1
    Z      COST                 9   LIM2                 1
    Z      LIM3                 1
RHS
    RHS1      LIM1                 5   LIM2                10
    RHS1      LIM3                 7
BOUNDS
 UP BND1      X                 4
 LO BND1      Y                -1
 UP BND1      Y                 1
ENDATA

