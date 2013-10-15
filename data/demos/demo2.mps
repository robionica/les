*
* maximaze 8 X1 + 2 X2 + 5 X3 + 5 X4 + 8 X5 + 3 X6 + 9 X7 + 7 X8 + 6 X9
* subject to
* C1: 2 X1 + 3 X2 + 4 X3 + 1 X4               <= 7
* C2: 1 X1 + 2 X2 + 3 X3 + 2 X4               <= 6
* C3:        1 X2 + 4 X3 + 3 X4 + 4 X5 + 2 X6 <= 9
* C4:        2 X2 + 1 X3 + 1 X4 + 2 X5 + 5 X6 <= 7
* C5:                      2 X4 + 1 X5 + 2 X6 <= 3
* C6:                      3 X4 + 4 X5 + 1 X6 <= 5
*
NAME          DEMO2
ROWS
 N  OBJ
 L  C1
 L  C2
 L  C3
 L  C4
 L  C5
 L  C6
COLUMNS
    X1      OBJ                8   C1                 2
    X1      C2                 1
    X2      OBJ                2   C1                 3
    X2      C2                 2
    X3      OBJ                5   C1                 4
    X3      C2                 3   C3                 1
    X3      C4                 2
    X4      OBJ                5   C1                 1
    X4      C2                 2   C3                 4
    X4      C4                 1
    X5      OBJ                8   C3                 3
    X5      C4                 1
    X6      OBJ                3   C3                 4
    X6      C4                 2
    X7      OBJ                9   C3                 2
    X7      C4                 5   C5                 2
    X7      C6                 3
    X8      OBJ                7   C5                 1
    X8      C6                 4
    X9      OBJ                6   C5                 2
    X9      C6                 1
RHS
    RHS1      C1                 7   C2                 6
    RHS1      C3                 9   C4                 7
    RHS1      C5                 3   C6                 5
BOUNDS
 UP BND1      X1                 1
 LO BND1      X1                 0
 UP BND1      X2                 1
 LO BND1      X2                 0
 UP BND1      X3                 1
 LO BND1      X3                 0
 UP BND1      X4                 1
 LO BND1      X4                 0
 UP BND1      X5                 1
 LO BND1      X5                 0
 UP BND1      X6                 1
 LO BND1      X6                 0
 UP BND1      X7                 1
 LO BND1      X7                 0
 UP BND1      X8                 1
 LO BND1      X8                 0
 UP BND1      X9                 1
 LO BND1      X9                 0
ENDATA
