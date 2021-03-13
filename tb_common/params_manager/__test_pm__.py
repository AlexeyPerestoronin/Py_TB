import os
import unittest

import tb_common.params_manager as pm
import tb_common.params_manager.errors as errors


class Test1(unittest.TestCase):
    def setUp(self):
        self._pm = pm.PM()
        self._pm.Add("param_1", default=1)
        self._pm.Add("param_2", default=2)
        self._pm.Add("param_3", default=3)
        self._pm.Add("param_4", default=4)
        self._pm.Add("param_5", default=5)

    def test1(self):
        save_string = self._pm.SaveToStr()
        pmr = pm.PM()
        pmr.RestoreFromStr(save_string)
        self.assertEqual(self._pm.Get("param_1"), pmr.Get("param_1"))
        self.assertEqual(self._pm.Get("param_2"), pmr.Get("param_2"))
        self.assertEqual(self._pm.Get("param_3"), pmr.Get("param_3"))
        self.assertEqual(self._pm.Get("param_4"), pmr.Get("param_4"))
        self.assertEqual(self._pm.Get("param_5"), pmr.Get("param_5"))


class Test2(unittest.TestCase):
    def setUp(self):
        self._pm = pm.PM()
        self._pm.Add("param_1")
        self._pm.Add("param_2")

    def test1(self):
        save_string = self._pm.SaveToStr()
        pmr = pm.PM()
        pmr.RestoreFromStr(save_string)
        self.assertEqual(self._pm.Get("param_1"), None)
        self.assertEqual(pmr.Get("param_1"), None)
        self.assertEqual(self._pm.Get("param_2"), None)
        self.assertEqual(pmr.Get("param_2"), None)


class Test3(unittest.TestCase) :
    def setUp(self) :
        self._pm = pm.PM()
        self._pm.Add("param_1", default=1)
        self._pm.Add("param_2", default=2)
        self._pm.Add("param_3", default=3)
        self._pm.Add("param_4", default=4)
        self._pm.Add("param_5", default=5)

    def test1(self):
        save_filepath = os.path.join(os.path.split(__file__)[0], "save_file.txt")
        self._pm.SaveToFile(save_filepath)
        pmr = pm.PM()
        pmr.RestoreFromFile(save_filepath)
        self.assertEqual(self._pm.Get("param_1"), pmr.Get("param_1"))
        self.assertEqual(self._pm.Get("param_2"), pmr.Get("param_2"))
        self.assertEqual(self._pm.Get("param_3"), pmr.Get("param_3"))
        self.assertEqual(self._pm.Get("param_4"), pmr.Get("param_4"))
        self.assertEqual(self._pm.Get("param_5"), pmr.Get("param_5"))


class Test4(unittest.TestCase) :
    def setUp(self) :
        self._pm = pm.PM()
        self._pm.Add("param_1")
        self._pm.Add("param_2")

    def test1(self):
        save_filepath = os.path.join(os.path.split(__file__)[0], "save_file.txt")
        self._pm.SaveToFile(save_filepath)
        pmr = pm.PM()
        pmr.RestoreFromFile(save_filepath)
        self.assertEqual(self._pm.Get("param_1"), None)
        self.assertEqual(pmr.Get("param_1"), None)
        self.assertEqual(self._pm.Get("param_2"), None)
        self.assertEqual(pmr.Get("param_2"), None)


class Test5(unittest.TestCase):
    def setUp(self) :
        self._pm = pm.PM()
        self._pm.Add("param_1")
        self._pm.Add("param_2")

    def test1(self):
        self.assertRaises(errors.ParameterIsAlreadyExist, self._pm.Add, "param_1")
        self.assertRaises(errors.ParameterIsAlreadyExist, self._pm.Add, "param_2")
        self.assertRaises(errors.ParameterIsNotExist, self._pm.Set, "param_3", 3)
        self.assertRaises(errors.ParameterIsNotExist, self._pm.Set, "param_4", 4)
        self.assertRaises(errors.RequiredParameterIsNotInitialized, self._pm.Check)
        self._pm.Set("param_1", 1)
        self._pm.Set("param_2", 2)
        self._pm.Check()


if __name__ == '__main__' :
    unittest.main()
