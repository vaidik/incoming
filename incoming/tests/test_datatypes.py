'''
    test_datatypes
    ~~~~~~~~~~~~~~

    Tests for incoming.datatypes module.
'''

from . import TestCase
from .. import datatypes
from ..incoming import PayloadErrors, PayloadValidator
from ..compat import PY2


class TestTypes(TestCase):

    def test_init_raises_attribute_error(self):
        self.assertRaises(AttributeError, datatypes.Types)

    def test_validate_raises_not_implemented_error(self):
        class SomeType(datatypes.Types):
            _DEFAULT_ERROR = 'Some error message.'

        self.assertRaises(NotImplementedError, SomeType().validate, 'test')


class TestInteger(TestCase):

    def test_integer_validates(self):
        self.assertTrue(datatypes.Integer.validate(2))
        self.assertTrue(datatypes.Integer.validate(-2))
        self.assertFalse(datatypes.Integer.validate(2.1))


class TestFloat(TestCase):

    def test_float_validates(self):
        self.assertFalse(datatypes.Float.validate(2))
        self.assertFalse(datatypes.Float.validate(-2))
        self.assertTrue(datatypes.Float.validate(2.1))
        self.assertTrue(datatypes.Float.validate(-2.1))


class TestNumber(TestCase):

    def test_number_validates(self):
        self.assertTrue(datatypes.Number.validate(2))
        self.assertTrue(datatypes.Number.validate(-2))
        self.assertTrue(datatypes.Number.validate(2.1))
        self.assertTrue(datatypes.Number.validate(-2.1))


class TestString(TestCase):

    def test_string_validates(self):
        self.assertTrue(datatypes.String.validate('Some string'))
        if PY2:
            self.assertTrue(datatypes.String.validate(unicode('Some string')))
        self.assertTrue(datatypes.String.validate(r'Some string'))
        self.assertFalse(datatypes.String.validate(1))


class TestArray(TestCase):

    def test_array_validates(self):
        self.assertTrue(datatypes.Array.validate(['item1', 'item2']))
        self.assertFalse(datatypes.Array.validate({}))


class TestBoolean(TestCase):

    def test_boolean_validates(self):
        self.assertTrue(datatypes.Boolean.validate(True))
        self.assertTrue(datatypes.Boolean.validate(False))


class TestFunction(TestCase):

    def test_function_validates_with_function(self):
        def test_func(val, *args, **kwargs):
            if val < 18:
                return False
            return True

        self.assertFalse(datatypes.Function(func=test_func).validate(10))
        self.assertTrue(datatypes.Function(func=test_func).validate(18))

    def test_function_validates_with_methods(self):
        class PseudoNameSpace(object):

            @staticmethod
            def test_func_static(val, *args, **kwargs):
                if val < 18:
                    return False
                return True

            @classmethod
            def test_func_class(cls, val, *args, **kwargs):
                if val < 18:
                    return False
                return True

            def test_func_regular(self, val, *arg, **kwargs):
                if val < 18:
                    return False
                return True

        # staticmethod
        self.assertFalse(datatypes.Function(
            func=PseudoNameSpace.test_func_static).validate(10))
        self.assertTrue(datatypes.Function(
            func=PseudoNameSpace.test_func_static).validate(18))

        # classmethod
        self.assertFalse(datatypes.Function(
            func=PseudoNameSpace.test_func_class).validate(10))
        self.assertTrue(datatypes.Function(
            func=PseudoNameSpace.test_func_class).validate(18))

        # regular
        self.assertFalse(datatypes.Function(
            func=PseudoNameSpace().test_func_regular).validate(10))
        self.assertTrue(datatypes.Function(
            func=PseudoNameSpace().test_func_regular).validate(18))


class TestJSON(TestCase):

    def test_json_validates_normal_types(self):
        class CustomJSONValidator(PayloadValidator):
            age = datatypes.Integer()

        errors = PayloadErrors()
        result = datatypes.JSON(CustomJSONValidator).validate(
            dict(age=10),
            key='nested',
            errors=errors)
        self.assertTrue(result)
        self.assertFalse('nested' in errors)
        self.assertTrue(len(errors.to_dict().keys()) == 0)

        result = datatypes.JSON(CustomJSONValidator).validate(
            dict(age='10'),
            key='nested',
            errors=errors)
        self.assertFalse(result)
        self.assertTrue('nested' in errors)
        self.assertTrue(len(errors.to_dict().keys()) == 1)

    def test_json_validates_function_types(self):
        class CustomJSONValidator(PayloadValidator):
            age = datatypes.Function(func='validate_age')

            def validate_age(self, val, *args, **kwargs):
                if not isinstance(val, int):
                    return False
                if val < 18:
                    return False
                return True

        errors = PayloadErrors()
        result = datatypes.JSON(CustomJSONValidator)
        result.validate(
            dict(age=20),
            key='nested',
            errors=errors)
        self.assertTrue(result)
        self.assertFalse('nested' in errors)
        self.assertTrue(len(errors.to_dict().keys()) == 0)

        errors = PayloadErrors()
        result = datatypes.JSON(CustomJSONValidator).validate(
            dict(age=10),
            key='nested',
            errors=errors)
        self.assertFalse(result)
        self.assertTrue('nested' in errors)
        self.assertTrue(len(errors.to_dict().keys()) == 1)
