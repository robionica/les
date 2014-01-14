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
 N  COST
 L  C1
 L  C2
 L  C3
 L  C4
COLUMNS
    X1      COST          2   C1                 3
    X2      COST          3   C1                 4
    X2      C2            2   C3                 2
    X3      COST          1   C1                 1
    X3      C2            3   C4                 2
    X4      COST          5   C2                 3
    X5      COST          4   C3                 3
    X6      COST          6   C4                 3
    X7      COST          1   C4                 2
RHS
    RHS1    C1                 6   C2                 5
    RHS1    C3                 4   C4                 5
BOUNDS
 UP BND1    X1                 1
 LO BND1    X1                 0
 UP BND1    X2                 1
 LO BND1    X2                 0
 UP BND1    X3                 1
 LO BND1    X3                 0
 UP BND1    X4                 1
 LO BND1    X4                 0
 UP BND1    X5                 1
 LO BND1    X5                 0
 UP BND1    X6                 1
 LO BND1    X6                 0
 UP BND1    X7                 1
 LO BND1    X7                 0
ENDATA
