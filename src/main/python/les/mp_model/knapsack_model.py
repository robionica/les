# Copyright (c) 2013 Oleksandr Sviridenko
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

from les.mp_model import mp_model


class KnapsackModel(mp_model.MPModel):

  def __init__(self, model=None):
    mp_model.MPModel.__init__(self, model)

  def set_rows(self, *args, **kwargs):
    mp_model.MPModel.set_rows(self, *args, **kwargs)
    if len(set(self.rows_senses)) != 1:
      raise Exception("Cannot automatically merge constraints, rows senses are "
                      "not identical: %s" % self.rows_senses)
    self.rows_senses = [self.rows_senses[0]]
    self.rows_coefficients = self.rows_coefficients.sum(0)
    self.rows_rhs = [sum(self.rows_rhs)]
    return self

  def get_weights(self):
    return self.rows_coefficients.tolist()[0]

  def get_max_weight(self):
    return self.rows_rhs[0]


KnapsackModel.get_profits = KnapsackModel.get_objective_coefficients
KnapsackModel.get_num_items = KnapsackModel.get_num_columns
