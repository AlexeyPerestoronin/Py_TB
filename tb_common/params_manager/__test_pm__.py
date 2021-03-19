import os
import copy
import unittest

import tb_common.params_manager as pm
import tb_common.params_manager.errors as errors


current_dir = os.path.dirname(__file__)


# brief: test saving and restoring for not None parameters
class Test1(unittest.TestCase):
    def setUp(self):
        self.save_filepath = os.path.join(current_dir, "save_file_Test1.txt")
        self._pm = pm.PM()
        self._pm.Add("param_1", default=1)
        self._pm.Add("param_2", default=2)
        self._pm.Add("param_3", default=3)
        self._pm.Add("param_4", default=4)
        self._pm.Add("param_5", default=5)

    def test1(self):
        save_dict = self._pm.SaveToDict()
        pmr = copy.deepcopy(self._pm)
        pmr.RestoreFromDict(save_dict)
        self.assertEqual(self._pm.Get("param_1"), pmr.Get("param_1"))
        self.assertEqual(self._pm.Get("param_2"), pmr.Get("param_2"))
        self.assertEqual(self._pm.Get("param_3"), pmr.Get("param_3"))
        self.assertEqual(self._pm.Get("param_4"), pmr.Get("param_4"))
        self.assertEqual(self._pm.Get("param_5"), pmr.Get("param_5"))

    def test2(self):
        save_dict = self._pm.SaveToDict()
        pmr = pm.PM.RestoreFromDictCls(save_dict)
        self.assertEqual(self._pm.Get("param_1"), pmr.Get("param_1"))
        self.assertEqual(self._pm.Get("param_2"), pmr.Get("param_2"))
        self.assertEqual(self._pm.Get("param_3"), pmr.Get("param_3"))
        self.assertEqual(self._pm.Get("param_4"), pmr.Get("param_4"))
        self.assertEqual(self._pm.Get("param_5"), pmr.Get("param_5"))

    def test3(self):
        save_string = self._pm.SaveToStr()
        pmr = copy.deepcopy(self._pm)
        pmr.RestoreFromStr(save_string)
        self.assertEqual(self._pm.Get("param_1"), pmr.Get("param_1"))
        self.assertEqual(self._pm.Get("param_2"), pmr.Get("param_2"))
        self.assertEqual(self._pm.Get("param_3"), pmr.Get("param_3"))
        self.assertEqual(self._pm.Get("param_4"), pmr.Get("param_4"))
        self.assertEqual(self._pm.Get("param_5"), pmr.Get("param_5"))

    def test4(self):
        save_string = self._pm.SaveToStr()
        pmr = pm.PM.RestoreFromStrCls(save_string)
        self.assertEqual(self._pm.Get("param_1"), pmr.Get("param_1"))
        self.assertEqual(self._pm.Get("param_2"), pmr.Get("param_2"))
        self.assertEqual(self._pm.Get("param_3"), pmr.Get("param_3"))
        self.assertEqual(self._pm.Get("param_4"), pmr.Get("param_4"))
        self.assertEqual(self._pm.Get("param_5"), pmr.Get("param_5"))

    def test5(self):
        self._pm.SaveToFile(self.save_filepath)
        pmr = copy.deepcopy(self._pm)
        pmr.RestoreFromFile(self.save_filepath)
        self.assertEqual(self._pm.Get("param_1"), pmr.Get("param_1"))
        self.assertEqual(self._pm.Get("param_2"), pmr.Get("param_2"))
        self.assertEqual(self._pm.Get("param_3"), pmr.Get("param_3"))
        self.assertEqual(self._pm.Get("param_4"), pmr.Get("param_4"))
        self.assertEqual(self._pm.Get("param_5"), pmr.Get("param_5"))

    def test6(self):
        self._pm.SaveToFile(self.save_filepath)
        pmr = pm.PM.RestoreFromFileCls(self.save_filepath)
        self.assertEqual(self._pm.Get("param_1"), pmr.Get("param_1"))
        self.assertEqual(self._pm.Get("param_2"), pmr.Get("param_2"))
        self.assertEqual(self._pm.Get("param_3"), pmr.Get("param_3"))
        self.assertEqual(self._pm.Get("param_4"), pmr.Get("param_4"))
        self.assertEqual(self._pm.Get("param_5"), pmr.Get("param_5"))


# brief: test saving and restoring for None parameters
class Test2(unittest.TestCase):
    def setUp(self):
        self.save_filepath = os.path.join(current_dir, "save_file_Test2.txt")
        self._pm = pm.PM()
        self._pm.Add("param_1")
        self._pm.Add("param_2")

    def test1(self):
        save_dict = self._pm.SaveToDict()
        pmr = copy.deepcopy(self._pm)
        pmr.RestoreFromDict(save_dict)
        self.assertEqual(self._pm.Get("param_1"), None)
        self.assertEqual(pmr.Get("param_1"), None)
        self.assertEqual(self._pm.Get("param_2"), None)
        self.assertEqual(pmr.Get("param_2"), None)

    def test2(self):
        save_dict = self._pm.SaveToDict()
        pmr = pm.PM.RestoreFromDictCls(save_dict)
        self.assertEqual(self._pm.Get("param_1"), None)
        self.assertEqual(pmr.Get("param_1"), None)
        self.assertEqual(self._pm.Get("param_2"), None)
        self.assertEqual(pmr.Get("param_2"), None)

    def test3(self):
        save_string = self._pm.SaveToStr()
        pmr = copy.deepcopy(self._pm)
        pmr.RestoreFromStr(save_string)
        self.assertEqual(self._pm.Get("param_1"), None)
        self.assertEqual(pmr.Get("param_1"), None)
        self.assertEqual(self._pm.Get("param_2"), None)
        self.assertEqual(pmr.Get("param_2"), None)

    def test4(self):
        save_string = self._pm.SaveToStr()
        pmr = pm.PM.RestoreFromStrCls(save_string)
        self.assertEqual(self._pm.Get("param_1"), None)
        self.assertEqual(pmr.Get("param_1"), None)
        self.assertEqual(self._pm.Get("param_2"), None)
        self.assertEqual(pmr.Get("param_2"), None)

    def test5(self):
        self._pm.SaveToFile(self.save_filepath)
        pmr = copy.deepcopy(self._pm)
        pmr.RestoreFromFile(self.save_filepath)
        self.assertEqual(self._pm.Get("param_1"), None)
        self.assertEqual(pmr.Get("param_1"), None)
        self.assertEqual(self._pm.Get("param_2"), None)
        self.assertEqual(pmr.Get("param_2"), None)

    def test6(self):
        self._pm.SaveToFile(self.save_filepath)
        pmr = pm.PM.RestoreFromFileCls(self.save_filepath)
        self.assertEqual(self._pm.Get("param_1"), None)
        self.assertEqual(pmr.Get("param_1"), None)
        self.assertEqual(self._pm.Get("param_2"), None)
        self.assertEqual(pmr.Get("param_2"), None)


# brief: testing of the error raising during of checking parameters
class Test3(unittest.TestCase):
    def test1(self):
        self._pm = pm.PM()
        self._pm.Add("param_1")
        self._pm.Add("param_2")
        # testing
        self.assertRaises(errors.ParameterIsAlreadyExist, self._pm.Add, "param_1")
        self.assertRaises(errors.ParameterIsAlreadyExist, self._pm.Add, "param_2")
        self.assertRaises(errors.ParameterIsNotExist, self._pm.Set, "param_3", 3)
        self.assertRaises(errors.ParameterIsNotExist, self._pm.Set, "param_4", 4)
        self.assertRaises(errors.RequiredParameterIsNotInitialized, self._pm.Check)
        self._pm.Set("param_1", 1)
        self._pm.Set("param_2", 2)
        self._pm.Check()

    def test2(self):
        self._pm = pm.PM()
        self._pm.Add("param_1", demanding_indicator=pm.PM.DI.ORDER_1.Key)
        self._pm.Add("param_2", demanding_indicator=pm.PM.DI.ORDER_2.Key)
        self._pm.Add("param_3", demanding_indicator=pm.PM.DI.ORDER_3.Key)
        self._pm.Add("param_4", demanding_indicator=pm.PM.DI.ORDER_4.Key)
        self._pm.Add("param_5", demanding_indicator=pm.PM.DI.ORDER_5.Key)
        # testing
        self._pm.Check(pm.PM.DI.NEVER.Key)
        self.assertRaises(errors.RequiredParameterIsNotInitialized, self._pm.Check, pm.PM.DI.ALWAYS.Key)
        self.assertRaises(errors.RequiredParameterIsNotInitialized, self._pm.Check, pm.PM.DI.ORDER_1.Key)
        self.assertRaises(errors.RequiredParameterIsNotInitialized, self._pm.Check, pm.PM.DI.ORDER_2.Key)
        self.assertRaises(errors.RequiredParameterIsNotInitialized, self._pm.Check, pm.PM.DI.ORDER_3.Key)
        self.assertRaises(errors.RequiredParameterIsNotInitialized, self._pm.Check, pm.PM.DI.ORDER_4.Key)
        self.assertRaises(errors.RequiredParameterIsNotInitialized, self._pm.Check, pm.PM.DI.ORDER_5.Key)
        self._pm.Set("param_1", 1)
        self._pm.Check(pm.PM.DI.ORDER_1.Key)
        self.assertRaises(errors.RequiredParameterIsNotInitialized, self._pm.Check, pm.PM.DI.ALWAYS.Key)
        self.assertRaises(errors.RequiredParameterIsNotInitialized, self._pm.Check, pm.PM.DI.ORDER_2.Key)
        self.assertRaises(errors.RequiredParameterIsNotInitialized, self._pm.Check, pm.PM.DI.ORDER_3.Key)
        self.assertRaises(errors.RequiredParameterIsNotInitialized, self._pm.Check, pm.PM.DI.ORDER_4.Key)
        self.assertRaises(errors.RequiredParameterIsNotInitialized, self._pm.Check, pm.PM.DI.ORDER_5.Key)
        self._pm.Set("param_2", 2)
        self._pm.Check(pm.PM.DI.ORDER_1.Key)
        self._pm.Check(pm.PM.DI.ORDER_2.Key)
        self.assertRaises(errors.RequiredParameterIsNotInitialized, self._pm.Check, pm.PM.DI.ALWAYS.Key)
        self.assertRaises(errors.RequiredParameterIsNotInitialized, self._pm.Check, pm.PM.DI.ORDER_3.Key)
        self.assertRaises(errors.RequiredParameterIsNotInitialized, self._pm.Check, pm.PM.DI.ORDER_4.Key)
        self.assertRaises(errors.RequiredParameterIsNotInitialized, self._pm.Check, pm.PM.DI.ORDER_5.Key)
        self._pm.Set("param_3", 3)
        self._pm.Check(pm.PM.DI.ORDER_1.Key)
        self._pm.Check(pm.PM.DI.ORDER_2.Key)
        self._pm.Check(pm.PM.DI.ORDER_3.Key)
        self.assertRaises(errors.RequiredParameterIsNotInitialized, self._pm.Check, pm.PM.DI.ALWAYS.Key)
        self.assertRaises(errors.RequiredParameterIsNotInitialized, self._pm.Check, pm.PM.DI.ORDER_4.Key)
        self.assertRaises(errors.RequiredParameterIsNotInitialized, self._pm.Check, pm.PM.DI.ORDER_5.Key)
        self._pm.Set("param_4", 4)
        self._pm.Check(pm.PM.DI.ORDER_1.Key)
        self._pm.Check(pm.PM.DI.ORDER_2.Key)
        self._pm.Check(pm.PM.DI.ORDER_3.Key)
        self._pm.Check(pm.PM.DI.ORDER_4.Key)
        self.assertRaises(errors.RequiredParameterIsNotInitialized, self._pm.Check, pm.PM.DI.ALWAYS.Key)
        self.assertRaises(errors.RequiredParameterIsNotInitialized, self._pm.Check, pm.PM.DI.ORDER_5.Key)
        self._pm.Set("param_5", 5)
        self._pm.Check(pm.PM.DI.ORDER_1.Key)
        self._pm.Check(pm.PM.DI.ORDER_2.Key)
        self._pm.Check(pm.PM.DI.ORDER_3.Key)
        self._pm.Check(pm.PM.DI.ORDER_4.Key)
        self._pm.Check(pm.PM.DI.ORDER_5.Key)
        self._pm.Check(pm.PM.DI.ALWAYS.Key)
        self._pm.Check()

    def test3(self):
        self._pm = pm.PM()
        self._pm.Add("param_1", demanding_indicator=pm.PM.DI.NEVER.Key)
        self._pm.Add("param_2", demanding_indicator=pm.PM.DI.NEVER.Key)
        self._pm.Add("param_3", demanding_indicator=pm.PM.DI.NEVER.Key)
        self._pm.Add("param_4", demanding_indicator=pm.PM.DI.NEVER.Key)
        self._pm.Add("param_5", demanding_indicator=pm.PM.DI.NEVER.Key)
        # testing
        self._pm.Check(pm.PM.DI.NEVER.Key)
        self._pm.Check(pm.PM.DI.ORDER_1.Key)
        self._pm.Check(pm.PM.DI.ORDER_2.Key)
        self._pm.Check(pm.PM.DI.ORDER_3.Key)
        self._pm.Check(pm.PM.DI.ORDER_4.Key)
        self._pm.Check(pm.PM.DI.ORDER_5.Key)
        self._pm.Check(pm.PM.DI.ALWAYS.Key)

    def test4(self):
        self._pm = pm.PM()
        self._pm.Add("param_1", demanding_indicator=pm.PM.DI.ALWAYS.Key)
        self._pm.Add("param_2", demanding_indicator=pm.PM.DI.ALWAYS.Key)
        self._pm.Add("param_3", demanding_indicator=pm.PM.DI.ALWAYS.Key)
        self._pm.Add("param_4", demanding_indicator=pm.PM.DI.ALWAYS.Key)
        self._pm.Add("param_5", demanding_indicator=pm.PM.DI.ALWAYS.Key)
        # testing
        self.assertRaises(errors.RequiredParameterIsNotInitialized, self._pm.Check)
        self.assertRaises(errors.RequiredParameterIsNotInitialized, self._pm.Check, pm.PM.DI.ORDER_5.Key)
        self.assertRaises(errors.RequiredParameterIsNotInitialized, self._pm.Check, pm.PM.DI.ORDER_4.Key)
        self.assertRaises(errors.RequiredParameterIsNotInitialized, self._pm.Check, pm.PM.DI.ORDER_3.Key)
        self.assertRaises(errors.RequiredParameterIsNotInitialized, self._pm.Check, pm.PM.DI.ORDER_2.Key)
        self.assertRaises(errors.RequiredParameterIsNotInitialized, self._pm.Check, pm.PM.DI.ORDER_1.Key)
        self._pm.Set("param_1", 1)
        self.assertRaises(errors.RequiredParameterIsNotInitialized, self._pm.Check)
        self.assertRaises(errors.RequiredParameterIsNotInitialized, self._pm.Check, pm.PM.DI.ORDER_5.Key)
        self.assertRaises(errors.RequiredParameterIsNotInitialized, self._pm.Check, pm.PM.DI.ORDER_4.Key)
        self.assertRaises(errors.RequiredParameterIsNotInitialized, self._pm.Check, pm.PM.DI.ORDER_3.Key)
        self.assertRaises(errors.RequiredParameterIsNotInitialized, self._pm.Check, pm.PM.DI.ORDER_2.Key)
        self.assertRaises(errors.RequiredParameterIsNotInitialized, self._pm.Check, pm.PM.DI.ORDER_1.Key)
        self._pm.Set("param_2", 2)
        self.assertRaises(errors.RequiredParameterIsNotInitialized, self._pm.Check)
        self.assertRaises(errors.RequiredParameterIsNotInitialized, self._pm.Check, pm.PM.DI.ORDER_5.Key)
        self.assertRaises(errors.RequiredParameterIsNotInitialized, self._pm.Check, pm.PM.DI.ORDER_4.Key)
        self.assertRaises(errors.RequiredParameterIsNotInitialized, self._pm.Check, pm.PM.DI.ORDER_3.Key)
        self.assertRaises(errors.RequiredParameterIsNotInitialized, self._pm.Check, pm.PM.DI.ORDER_2.Key)
        self.assertRaises(errors.RequiredParameterIsNotInitialized, self._pm.Check, pm.PM.DI.ORDER_1.Key)
        self._pm.Set("param_3", 3)
        self.assertRaises(errors.RequiredParameterIsNotInitialized, self._pm.Check)
        self.assertRaises(errors.RequiredParameterIsNotInitialized, self._pm.Check, pm.PM.DI.ORDER_5.Key)
        self.assertRaises(errors.RequiredParameterIsNotInitialized, self._pm.Check, pm.PM.DI.ORDER_4.Key)
        self.assertRaises(errors.RequiredParameterIsNotInitialized, self._pm.Check, pm.PM.DI.ORDER_3.Key)
        self.assertRaises(errors.RequiredParameterIsNotInitialized, self._pm.Check, pm.PM.DI.ORDER_2.Key)
        self.assertRaises(errors.RequiredParameterIsNotInitialized, self._pm.Check, pm.PM.DI.ORDER_1.Key)
        self._pm.Set("param_4", 4)
        self.assertRaises(errors.RequiredParameterIsNotInitialized, self._pm.Check)
        self.assertRaises(errors.RequiredParameterIsNotInitialized, self._pm.Check, pm.PM.DI.ORDER_5.Key)
        self.assertRaises(errors.RequiredParameterIsNotInitialized, self._pm.Check, pm.PM.DI.ORDER_4.Key)
        self.assertRaises(errors.RequiredParameterIsNotInitialized, self._pm.Check, pm.PM.DI.ORDER_3.Key)
        self.assertRaises(errors.RequiredParameterIsNotInitialized, self._pm.Check, pm.PM.DI.ORDER_2.Key)
        self.assertRaises(errors.RequiredParameterIsNotInitialized, self._pm.Check, pm.PM.DI.ORDER_1.Key)
        self._pm.Set("param_5", 5)
        self._pm.Check()


if __name__ == '__main__' :
    unittest.main()
