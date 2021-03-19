import json

import common.faf as faf

from common import CREATE_CONSTANT as CC

import tb_common.params_manager.errors as errors

# brief: class for ma
# note1: PM - is a Parameters Manger abbreviation
class PM:
    class PARAMS:
        VALUE = CC("PARAMETER'S_VALUE")
        DEMAND = CC("PARAMETER'S_DEMAND")

    # brief: collects demand indicators
    # note: DI is Demanding Indicator
    class DI:
        ALWAYS = CC('inf')
        ORDER_0 = CC('0')
        ORDER_1 = CC('1')
        ORDER_2 = CC('2')
        ORDER_3 = CC('3')
        ORDER_4 = CC('4')
        ORDER_5 = CC('5')
        NEVER = CC('nan')


    def __init__(self):
        self._parameters = {
            # (object)name : [
            #   PARAMETER'S_VALUE : (object)value,
            #   PARAMETER'S_DEMAND : (str)demanding_indicator
            # ]
        }

    # brief: add new parameter
    # param: name - the name of the new parameter
    # param: default - its default value
    # param: demanding_indicator - its demanding value
    def Add(self, name, *, default=None, demanding_indicator=DI.ALWAYS.Key):
        if name in self._parameters.keys():
            raise errors.ParameterIsAlreadyExist()
        self._parameters[name] = {
            PM.PARAMS.VALUE.Key : default,
            PM.PARAMS.DEMAND.Key : demanding_indicator
        }

    def Get(self, name):
        if name not in self._parameters.keys():
            raise errors.ParameterIsNotExist()
        return self._parameters[name][PM.PARAMS.VALUE.Key]

    def Set(self, name, value):
        if name not in self._parameters.keys():
            raise errors.ParameterIsNotExist()
        self._parameters[name][PM.PARAMS.VALUE.Key] = value

    def Check(self, demanding_indicator=DI.ALWAYS.Key):
        if demanding_indicator == PM.DI.NEVER.Key:
            return
        for name, param in self._parameters.items():
            value = param[PM.PARAMS.VALUE.Key]
            demand = param[PM.PARAMS.DEMAND.Key]
            if value is not None or demand == PM.DI.NEVER.Key:
                continue
            if demand != PM.DI.ALWAYS.Key and float(demand) > float(demanding_indicator):
                continue
            error = errors.RequiredParameterIsNotInitialized()
            error.SetName(name)
            raise error

    def GetCopyParameters(self):
        import copy
        return copy.deepcopy(self._parameters)

    # NOTE: Save and Restore

    def SaveToDict(self):
        return self.GetCopyParameters()

    def RestoreFromDict(self, save_dict):
        for name, params in save_dict.items():
            value = params[PM.PARAMS.VALUE.Key]
            self.Set(name, value)

    @classmethod
    def RestoreFromDictCls(cls, save_dict):
        restored_pm = cls()
        restored_pm._parameters = save_dict
        return restored_pm

    def SaveToStr(self, indent=4):
        return json.dumps(self.SaveToDict(), indent=indent)

    def RestoreFromStr(self, save_string):
        self.RestoreFromDict(dict(json.loads(save_string)))

    @classmethod
    def RestoreFromStrCls(cls, save_string):
        saved_dict = json.loads(save_string)
        return cls.RestoreFromDictCls(saved_dict)

    def SaveToFile(self, filepath):
        faf.SaveContentToFile1(filepath, self.SaveToStr())

    def RestoreFromFile(self, filepath):
        self.RestoreFromStr(faf.GetFileContent(filepath))

    @classmethod
    def RestoreFromFileCls(cls, filepath):
        return cls.RestoreFromStrCls(faf.GetFileContent(filepath))
