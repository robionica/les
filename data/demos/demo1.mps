*
* maximize 2 * X1 + 3 * X2 + X3 + 5 * X4 + 4 * X5 + 6 * X6 + X7
*
* C1: 3*X1 + 4*X2 + X3                               <= 6
* C2:        2*X2 + 3*X3 + 3*X4                      <= 5
* C3:        2*X2               + 3*X5               <= 4
* C4:               2*X3               + 3*X6 + 2*X7 <= 5
* C5:
*
NAME          DEMO1
ROWS
 N  OBJECTIVE
 L  C1
 L  C2
 L  C3
 L  C4
COLUMNS
    X1      OBJECTIVE          2   C1                 3
    X2      OBJECTIVE          3   C1                 4
    X2      C2                 2   C3                 2
    X3      OBJECTIVE          1   C1                 1
    X3      C2                 3   C4                 2
    X4      OBJECTIVE          5   C2                 3
    X5      OBJECTIVE          4   C3                 3
    X6      OBJECTIVE          6   C4                 3
    X7      OBJECTIVE          1   C4                 2
RHS
    RHS1    C1                 6   C2                 5
    RHS1    C3                 4   C4                 5
BOUNDS
 UP BND1    X1                 1
 LO BND1    X1                 0
ENDATA
