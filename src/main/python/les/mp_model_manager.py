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

'''MP model manager is used to initialize and optimize models. It
also does the bookkeeping, maintaining the list of currently solving
models.
'''

from les import mp_model

def build_mp_model(*args, **kwargs):
  return mp_model.build(*args, **kwargs)

def find_mp_model_by_name(name):
  raise NotImplementedError()

def get_all_mp_models():
  raise NotImplementedError()

def optimize_mp_model(model, optimization_parameters):
  if not isinstance(model, mp_model.MPModel):
    raise TypeError()
  return model.optimize(optimization_parameters)
