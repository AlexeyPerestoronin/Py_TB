import json

import common.faf as faf

import tb_common.params_manager.errors as errors

# brief: class for ma
# note1: PM - is a Parameters Manger abbreviation
class PM:
    def __init__(self):
        self._parameters = {
            # (object)name : [(object)value, (bool)is_required]
        }

    def Add(self, name, *, default=None, is_required=True):
        if name in self._parameters.keys():
            raise errors.ParameterIsAlreadyExist()
        self._parameters[name] = [default, is_required]

    def Get(self, name):
        if name not in self._parameters.keys():
            raise errors.ParameterIsNotExist()
        return self._parameters[name][0]

    def Set(self, name, value, is_required=True):
        if name not in self._parameters.keys():
            raise errors.ParameterIsNotExist()
        self._parameters[name] = [value, is_required]

    def Check(self):
        for name, param in self._parameters.items():
            value, is_required = param
            if is_required and value is None:
                error = errors.RequiredParameterIsNotInitialized()
                error.SetName(name)
                raise error

    def SaveToStr(self):
        return json.dumps(self._parameters, indent=4)

    def RestoreFromStr(self, save_string):
        self._parameters = dict(json.loads(save_string))

    def SaveToFile(self, filepath):
        faf.SaveContentToFile1(filepath, self.SaveToStr())

    def RestoreFromFile(self, filepath):
        self.RestoreFromStr(faf.GetFileContent(filepath))
