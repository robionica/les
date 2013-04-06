# Copyright (c) 2012-2013 Oleksandr Sviridenko
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Osi hint param

# Whether to do a presolve in initialSolve
OSI_DO_PRESOLVE_IN_INITIAL = 0
# Whether to use a dual algorithm in initialSolve. The reverse is to use a
# primal algorithm.
OSI_DO_DUAL_IN_INITIAL = 1
# Whether to do a presolve in resolve
OSI_DO_PRESOLVE_IM_RESOLVE = 2
# Whether to use a dual algorithm in resolve. The reverse is to use a primal
# algorithm.
OSI_DO_DUAL_IN_RESOLVE = 3
# Whether to scale problem
OSI_DO_SCALE = 4
# Whether to create a non-slack basis (only in initialSolve)
OSI_DO_CRASH = 5
# Whether to reduce amount of printout, e.g., for branch and cut
OSI_DO_REDUCE_PRINT = 6
# Whether we are in branch and cut - so can modify behavior
OSI_DO_IN_BRANCH_AND_CUT = 7
