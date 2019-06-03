from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os.path
import json

class ParamPlotConfigWriter:
    def __init__(self, run_path):
      self.run_path = run_path
      self.config_dict = {}
      self._config_name = 'runparams.json'
      self._run_params_path = os.path.join(run_path, self._config_name)
    
    def AddParameter(self, name, value):
      self.config_dict[name] = value
    
    def AddParametersByDict(self, param_map):
      for name in param_map:
        self.config_dict[name] = param_map[name]
    
    def SetParameters(self, param_map):
      self.config_dict = param_map

    def Save(self):
      # create the run parameters file and save the config dictionary
      with open(self._run_params_path, 'w') as file_handle:
        file_handle.write(json.dumps(self.config_dict))


