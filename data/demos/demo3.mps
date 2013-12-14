NAME          DEMO3
ROWS
 N  OBJECTIVE
 G  C1
 L  C2
COLUMNS
    X1      OBJECTIVE          5   C1                 2
    X2      OBJECTIVE          4   C1                 3
    X2      C2                 4
    X3      OBJECTIVE          6   C2                 1
RHS
    RHS1    C1                 2   C2                 3
BOUNDS
 UP BND1    X1                 1
 LO BND1    X1                 0
 UP BND1    X2                 1
 LO BND1    X2                 0
 UP BND1    X3                 1
 LO BND1    X3                 0
ENDATA
