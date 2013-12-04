# Copyright (c) 2013 Oleksandr Sviridenko

from les import mp_model

class KnapsackModelParameters(mp_model.MPModelParameters):

  def __init__(self, model=None):
    mp_model.MPModelParameters.__init__(self, model)

  @classmethod
  def build_from_mp_model_parameters(cls, mp_model_params):
    knapsack_model_params = cls()
    knapsack_model_params.set_objective_from_scratch(mp_model_params.get_objective_coefficients())
    knapsack_model_params.set_columns_from_scratch(
      mp_model_params.get_columns_lower_bounds(),
      mp_model_params.get_columns_upper_bounds(),
      mp_model_params.get_columns_names())
    knapsack_model_params.set_rows_from_scratch(mp_model_params.get_rows_coefficients(),
                                                mp_model_params.get_rows_senses(),
                                                mp_model_params.get_rows_rhs(),
                                                mp_model_params.get_rows_names())
    return knapsack_model_params

  @classmethod
  def build(cls, *args, **kwargs):
    if len(args) and isinstance(args[0], mp_model.MPModelParameters):
      params = cls.build_from_mp_model_parameters(args[0])
    elif not len(args) and not len(kwargs):
      return cls()
    elif len(args) == 1:
      return cls(args[0])
    else:
      return cls.build_from_scratch(*args, **kwargs)
    return params

  def set_rows_from_scratch(self, *args, **kwargs):
    mp_model.MPModelParameters.set_rows_from_scratch(self, *args, **kwargs)
    if len(set(self._rows_senses)) != 1:
      raise Exception("Cannot automatically merge constraints, rows senses are "
                      "not identical: %s" % self._rows_senses)
    self._rows_senses = [self._rows_senses[0]]
    self._rows_coefs = self._rows_coefs.sum(0)
    self._rows_rhs = [sum(self._rows_rhs)]

  def get_weights(self):
    return self._rows_coefs.tolist()[0]

  def get_max_weight(self):
    return self._rows_rhs[0]

KnapsackModelParameters.get_profits = KnapsackModelParameters.get_objective_coefficients
KnapsackModelParameters.get_num_items = KnapsackModelParameters.get_num_columns
build = KnapsackModelParameters.build
