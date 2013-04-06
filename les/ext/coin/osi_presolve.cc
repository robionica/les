#include <coin/OsiPresolve.hpp>

#include <boost/python.hpp>
#include <iostream>
using namespace boost::python;

struct OsiPresolveWrap : OsiPresolve, wrapper<OsiPresolve> {
public:
  OsiPresolveWrap() : OsiPresolve() {}

  virtual OsiSolverInterface* presolvedModel(
                  OsiSolverInterface& origModel) {
    std::cout << origModel.getNumCols() << origModel.getNumRows() << std::endl;
    return OsiPresolve::presolvedModel(origModel, 1.0e-8,
                                        false, 5, NULL,
                                        true, NULL);
  }
};

BOOST_PYTHON_MODULE(_osi_presolve)
{
  class_<OsiPresolveWrap, boost::noncopyable>("OsiPresolve")
    .def("presolved_model", &OsiPresolveWrap::presolvedModel,
         return_value_policy<manage_new_object>())
    ;
}
