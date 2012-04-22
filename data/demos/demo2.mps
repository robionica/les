*
* maximaze 8*X1 + 2*X2 + 5*X3 + 5*X4 + 8*X5 + 3*X6 + 9*X7 + 7*X8 + 6*X9
*
* R1: 2*X1 + 3*X2 + 4*X3 + 1*X4
* R2: 1*X1 + 2*X2 + 3*X3 + 2*X4
* R3:        1*X2 + 4*X3 + 3*X4 + 4*X5 + 2*X6
* R4:        2*X2 + 1*X3 + 1*X4 + 2*X5 + 5*X6
* R5:                      2*X4 + 1*X5 + 2*X6
* R6:                      3*X4 + 4*X5 + 1*X6
*
NAME          DEMO1
ROWS
 N  OBJ
 L  R1
 L  R2
 L  R3
 L  R4
 L  R5
 L  R6
COLUMNS
    X1      OBJ                8   R1                 2
    X1      R2                 1
    X2      OBJ                2   R1                 3
    X2      R2                 2
    X3      OBJ                5   R1                 4
    X3      R2                 3   R3                 1
    X3      R4                 2
    X4      OBJ                5   R1                 1
    X4      R2                 2   R3                 4
    X4      R4                 1
    X5      OBJ                8   R3                 3
    X5      R4                 1
    X6      OBJ                3   R3                 4
    X6      R4                 2
    X7      OBJ                9   R3                 2
    X7      R4                 5   R5                 2
    X7      R6                 3
    X8      OBJ                7   R5                 1
    X8      R6                 4
    X9      OBJ                6   R5                 2
    X9      R6                 1
RHS
    RHS1      R1                 7   R2                 6
    RHS1      R3                 9   R4                 7
    RHS1      R5                 3   R6                 5
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
