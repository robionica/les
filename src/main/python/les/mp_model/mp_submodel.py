from les.mp_model import mp_model
from les.mp_model import mp_model_parameters

class MPSubmodel(mp_model.MPModel):

  @classmethod
  def build(cls, model, rows_scope, columns_scope):
    submodel = cls()
    # Build new objective function.
    columns_scope = sorted(list(columns_scope))
    var = model.get_variable_by_index(columns_scope[0])
    var_ = var.clone()
    submodel.add_variable(var_)
    objective = var_ * model.get_objective().get_coefficient(var)
    for i in range(1, len(columns_scope)):
      var = model.get_variable_by_index(columns_scope[i])
      var_ = var.clone()
      submodel.add_variable(var_)
      objective += var_ * model.get_objective().get_coefficient(var)
    submodel.set_objective(objective, model.maximization())
    # Build new constraints.
    #
    # TODO(d2rk): optimize set_constraints_from_scratch.
    params = mp_model_parameters.build(model)
    submodel.set_constraints_from_scratch(
      params.get_rows_coefficients()[list(rows_scope)][:, columns_scope],
      [params.get_rows_senses()[i] for i in rows_scope],
      [params.get_rows_rhs()[i] for i in rows_scope],
      [params.get_rows_names()[i] for i in rows_scope])
    return submodel

build = MPSubmodel.build
