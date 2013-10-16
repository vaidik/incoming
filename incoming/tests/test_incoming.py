'''
    test_incoming
    ~~~~~~~~~~~~~

    Tests for incoming.incoming module.
'''

from . import TestCase
from .. import datatypes
from ..incoming import PayloadErrors
from ..incoming import PayloadValidator


class TestPayloadErrors(TestCase):

    def setUp(self):
        self.error_key = 'error_key'
        self.error_msg = 'Error message'

    def test_append_error_in_existing_key(self):
        errors = PayloadErrors()
        errors._errors['test_key'] = ['Test error']

        errors.append('test_key', self.error_msg)

        # Check that not more than 1 message was added
        self.assertEqual(len(errors._errors['test_key']), 2)
        self.assertEqual(len(errors._errors.keys()), 1)

        # Check that the error msg intended to add was added
        self.assertEqual(errors._errors['test_key'][1], self.error_msg)

    def test_append_error_in_non_existing_key(self):
        errors = PayloadErrors()
        errors._errors['test_key'] = ['Test error']

        errors.append(self.error_key, self.error_msg)

        # Check that not more than 1 message was added
        self.assertEqual(len(errors._errors['test_key']), 1)
        self.assertEqual(len(errors._errors[self.error_key]), 1)
        self.assertEqual(len(errors._errors.keys()), 2)

        # Check that the error msg intended to add was added
        self.assertEqual(errors._errors[self.error_key][0], self.error_msg)

    def test_prepend_error_in_existing_key(self):
        errors = PayloadErrors()
        errors._errors['test_key'] = ['Test error']

        errors.prepend('test_key', self.error_msg)

        # Check that not more than 1 message was added
        self.assertEqual(len(errors._errors['test_key']), 2)
        self.assertEqual(len(errors._errors.keys()), 1)

        # Check that the error msg intended to add was added
        self.assertEqual(errors._errors['test_key'][0], self.error_msg)

    def test_prepend_error_in_non_existing_key(self):
        errors = PayloadErrors()
        errors._errors['test_key'] = ['Test error']

        errors.prepend(self.error_key, self.error_msg)

        # Check that not more than 1 message was added
        self.assertEqual(len(errors._errors['test_key']), 1)
        self.assertEqual(len(errors._errors[self.error_key]), 1)
        self.assertEqual(len(errors._errors.keys()), 2)

        # Check that the error msg intended to add was added
        self.assertEqual(errors._errors[self.error_key][0], self.error_msg)

    def test_to_dict(self):
        errors = PayloadErrors()
        errors.append('key1', 'value1.1')
        errors.append('key1', 'value1.2')
        errors.append('key2', 'value2')

        errors_dict = errors.to_dict()
        self.assertTrue(isinstance(errors_dict, dict))
        self.assertDictEqual(errors_dict, errors._errors)

    def test_error_type_membership_test(self):
        errors = PayloadErrors()
        errors.append('key1', 'value1.1')
        errors.append('key1', 'value1.2')
        errors.append('key2', 'value2')

        self.assertTrue('key1' in errors)
        self.assertTrue('key2' in errors)
        self.assertFalse('key3' in errors)


class TestPayloadValidator(TestCase):

    def setUp(self):
        class DummyValidator(PayloadValidator):
            name = datatypes.String()
            age = datatypes.Integer()
            hobbies = datatypes.Array()

        self.DummyValidator = DummyValidator

    def test_collect_fields(self):
        validator = self.DummyValidator()
        fields = validator._collect_fields()
        self.assertTrue(isinstance(fields, tuple))
        self.assertItemsEqual(fields, ['name', 'age', 'hobbies'])

    def test_collected_fields_raises_exception_on_no_fields(self):
        class DummyValidator(PayloadValidator):
            pass

        self.assertRaises(Exception, DummyValidator)

    def test_validate_returns_tuple(self):
        validator = self.DummyValidator()

        # validate a valid payload
        payload = dict(name='test', age=23, hobbies=['A value'])
        result = validator.validate(payload)
        self.assertTrue(isinstance(result, tuple))
        self.assertTrue(result[0])
        self.assertEquals(result[1], None)

        # validate an invalid payload
        payload = dict(name='test', age=23)
        result = validator.validate(payload)
        self.assertTrue(isinstance(result, tuple))
        self.assertFalse(result[0])
        self.assertTrue(isinstance(result[1], dict))

    def test_required_when_global_is_true(self):
        validator = self.DummyValidator()

        payload = dict(name='test', age=23, hobbies=['A value'])
        result, errors = validator.validate(payload)
        self.assertTrue(result)

        payload = dict(name='test', age=23)
        result, errors = validator.validate(payload)
        self.assertFalse(result)
        self.assertItemsEqual(errors.keys(), ['hobbies'])

        payload = dict(age=23)
        result, errors = validator.validate(payload)
        self.assertFalse(result)
        self.assertItemsEqual(errors.keys(), ['name', 'hobbies'])

        class AnotherDummyValidator(PayloadValidator):
            name = datatypes.String()
            age = datatypes.Integer()
            hobbies = datatypes.Array(required=False)

        validator = AnotherDummyValidator()

        payload = dict(name='test', age=23, hobbies=['A value'])
        result, errors = validator.validate(payload)
        self.assertTrue(result)

        payload = dict(name='test', age=23)
        result, errors = validator.validate(payload)
        self.assertTrue(result)

        payload = dict(name='test')
        result, errors = validator.validate(payload)
        self.assertFalse(result)
        self.assertItemsEqual(errors.keys(), ['age'])

        payload = dict(name='test', hobbies=['A value'])
        result, errors = validator.validate(payload)
        self.assertFalse(result)
        self.assertItemsEqual(errors.keys(), ['age'])

    def test_required_when_global_is_false(self):

        class AnotherDummyValidator(self.DummyValidator):
            required = False

        validator = AnotherDummyValidator()

        payload = dict(name='test', age=23, hobbies=['A value'])
        result, errors = validator.validate(payload)
        self.assertTrue(result)

        payload = dict(name='test', age=23)
        result, errors = validator.validate(payload)
        self.assertTrue(result)

        payload = dict(age=23)
        result, errors = validator.validate(payload)
        self.assertTrue(result)

        class AnotherDummyValidator(self.DummyValidator):
            required = False
            name = datatypes.String(required=True)

        validator = AnotherDummyValidator()

        payload = dict(name='test', age=23, hobbies=['A value'])
        result, errors = validator.validate(payload)
        self.assertTrue(result)

        payload = dict(name='test', age=23)
        result, errors = validator.validate(payload)
        self.assertTrue(result)

        payload = dict(age=9, hobbies=['A value'])
        result, errors = validator.validate(payload)
        self.assertFalse(result)
        self.assertItemsEqual(errors.keys(), ['name'])

        payload = dict(hobbies=['A value'])
        result, errors = validator.validate(payload)
        self.assertFalse(result)
        self.assertItemsEqual(errors.keys(), ['name'])

    def test_required_with_validate_when_global_required_is_true(self):
        class AnotherDummyValidator(self.DummyValidator):
            required = True

        validator = AnotherDummyValidator()
        payload = dict(name='Testing')

        result, errors = validator.validate(payload, required=False)
        self.assertTrue(result)

        result, errors = validator.validate(payload, required=True)
        self.assertFalse(result)
        self.assertItemsEqual(errors.keys(), ['age', 'hobbies'])

    def test_required_with_validate_when_global_required_is_false(self):
        class AnotherDummyValidator(self.DummyValidator):
            required = False

        validator = AnotherDummyValidator()
        payload = dict(name='Testing')

        result, errors = validator.validate(payload, required=False)
        self.assertTrue(result)

        result, errors = validator.validate(payload, required=True)
        self.assertFalse(result)
        self.assertItemsEqual(errors.keys(), ['age', 'hobbies'])

    def test_strict_when_global_is_True(self):

        class AnotherDummyValidator(self.DummyValidator):
            strict = True

        validator = AnotherDummyValidator()

        payload = dict(name='Something', age=9, hobbies=['a value'],
                       missing1='a value', missing2='a value')
        result, errors = validator.validate(payload)

        self.assertFalse(result)
        self.assertItemsEqual(errors.keys(), ['missing1', 'missing2'])
        self.assertEquals(errors['missing1'][0],
                          AnotherDummyValidator.strict_error)
        self.assertEquals(errors['missing2'][0],
                          AnotherDummyValidator.strict_error)

    def test_strict_when_global_is_false(self):

        class AnotherDummyValidator(self.DummyValidator):
            strict = False

        validator = AnotherDummyValidator()

        payload = dict(name='Something', age=9, hobbies=['a value'],
                       missing1='a value', missing2='a value')
        result, errors = validator.validate(payload)

        self.assertTrue(result)
        self.assertEquals(errors, None)

    def test_strict_with_validate_when_global_strict_is_true(self):
        class AnotherDummyValidator(self.DummyValidator):
            strict = True

        validator = AnotherDummyValidator()
        payload = dict(name='Something', age=9, hobbies=['a value'],
                       missing1='a value', missing2='a value')

        result, errors = validator.validate(payload, strict=False)
        self.assertTrue(result)

        result, errors = validator.validate(payload, strict=True)
        self.assertFalse(result)
        self.assertItemsEqual(errors.keys(), ['missing1', 'missing2'])

    def test_strict_with_validate_when_global_strict_is_false(self):
        class AnotherDummyValidator(self.DummyValidator):
            strict = False

        validator = AnotherDummyValidator()
        payload = dict(name='Something', age=9, hobbies=['a value'],
                       missing1='a value', missing2='a value')

        result, errors = validator.validate(payload, strict=False)
        self.assertTrue(result)

        result, errors = validator.validate(payload, strict=True)
        self.assertFalse(result)
        self.assertItemsEqual(errors.keys(), ['missing1', 'missing2'])

    def test_replace_string_args_replaces_strings_with_methods(self):
        class CustomValidator(PayloadValidator):
            age = datatypes.Function(func='validate_age')
            hobbies = datatypes.Function(func='validate_hobbies')

            def validate_hobbies(self, val, *args, **kwargs):
                return False if len(val) == 0 else True

            def validate_age(self, val, *args, **kwargs):
                if val < 18:
                    return False
                return True

        validator = CustomValidator()
        self.assertTrue(isinstance(validator.age.func, str))
        self.assertTrue(isinstance(validator.hobbies.func, str))

        validator._replace_string_args()

        self.assertTrue(callable(validator.age.func))
        self.assertTrue(callable(validator.hobbies.func))

    def test_replace_string_args_gets_called_only_once(self):
        class CustomValidator(PayloadValidator):
            age = datatypes.Function(func='validate_age')
            hobbies = datatypes.Function(func='validate_hobbies')

            def validate_hobbies(self, val, *args, **kwargs):
                return False if len(val) == 0 else True

            def validate_age(self, val, *args, **kwargs):
                if val < 18:
                    return False
                return True

        validator = CustomValidator()
        self.assertFalse(validator._string_args_replaced)
        validator._replace_string_args()
        self.assertTrue(validator._string_args_replaced)

        validator.age.func = 'validate_hobbies'
        validator._replace_string_args()
        self.assertFalse(callable(validator.age.func))

    def test_function_datatype_validates_with_validator_method(self):
        '''
        Tests the working of Function datatype with
        PayloadValidator._replace_string_args.
        '''

        class CustomValidator(PayloadValidator):
            age = datatypes.Function(func='validate_age')
            hobbies = datatypes.Function(func='validate_hobbies')

            def validate_hobbies(self, val, *args, **kwargs):
                return False if len(val) == 0 else True

            def validate_age(self, val, *args, **kwargs):
                if val < 18:
                    return False
                return True

        result, errors = CustomValidator().validate(
            dict(age=10, hobbies=['a']))
        self.assertFalse(result)

        result, errors = CustomValidator().validate(
            dict(age=18, hobbies=[]))
        self.assertFalse(result)

        result, errors = CustomValidator().validate(
            dict(age=10, hobbies=['a']))
        self.assertFalse(result)

        result, errors = CustomValidator().validate(
            dict(age=18, hobbies=['a']))
        self.assertTrue(result)


class TestNestedPayloadValidator(TestCase):

    def test_validates_nested_json_when_cls_is_global(self):
        class AddressValidator(PayloadValidator):
            street = datatypes.String()
            pincode = datatypes.Integer()

        class CustomValidator(PayloadValidator):
            name = datatypes.String()
            age = datatypes.Integer()
            address = datatypes.JSON(AddressValidator)

        validator = CustomValidator()

        # valid payload
        payload = dict(name='Test', age=9,
                       address=dict(street='Test street', pincode=123))
        result, errors = validator.validate(payload)
        self.assertTrue(result)
        self.assertTrue(errors is None)

        # invalid case
        payload = dict(name=True, age=9,
                       address=dict(street='Test street', pincode=123))
        result, errors = validator.validate(payload)
        self.assertFalse(result)
        self.assertTrue('name' in errors.keys())
        self.assertItemsEqual(errors.keys(), ['name'])

        # invalid case with invalid nested payload
        payload = dict(name='True', age=9,
                       address=dict(street='Test street', pincode='123'))
        result, errors = validator.validate(payload)
        self.assertFalse(result)
        self.assertTrue('pincode' in errors['address'][1].keys())
        self.assertItemsEqual(errors['address'][1].keys(), ['pincode'])

    def test_validates_nested_json_when_cls_is_nested_declared_earlier(self):
        class CustomValidator(PayloadValidator):
            class AddressValidator(PayloadValidator):
                street = datatypes.String()
                pincode = datatypes.Integer()

            name = datatypes.String()
            age = datatypes.Integer()
            address = datatypes.JSON(AddressValidator)

        validator = CustomValidator()

        # valid payload
        payload = dict(name='Test', age=9,
                       address=dict(street='Test street', pincode=123))
        result, errors = validator.validate(payload)
        self.assertTrue(result)
        self.assertTrue(errors is None)

        # invalid case
        payload = dict(name=True, age=9,
                       address=dict(street='Test street', pincode=123))
        result, errors = validator.validate(payload)
        self.assertFalse(result)
        self.assertTrue('name' in errors.keys())
        self.assertItemsEqual(errors.keys(), ['name'])

        # invalid case with invalid nested payload
        payload = dict(name='True', age=9,
                       address=dict(street='Test street', pincode='123'))
        result, errors = validator.validate(payload)
        self.assertFalse(result)
        self.assertTrue('pincode' in errors['address'][1].keys())
        self.assertItemsEqual(errors['address'][1].keys(), ['pincode'])

    def test_validates_nested_json_when_cls_is_nested_declared_later(self):
        class CustomValidator(PayloadValidator):
            name = datatypes.String()
            age = datatypes.Integer()
            address = datatypes.JSON('AddressValidator')

            class AddressValidator(PayloadValidator):
                street = datatypes.String()
                pincode = datatypes.Integer()

        validator = CustomValidator()

        # valid payload
        payload = dict(name='Test', age=9,
                       address=dict(street='Test street', pincode=123))
        result, errors = validator.validate(payload)
        self.assertTrue(result)
        self.assertTrue(errors is None)

        # invalid case
        payload = dict(name=True, age=9,
                       address=dict(street='Test street', pincode=123))
        result, errors = validator.validate(payload)
        self.assertFalse(result)
        self.assertTrue('name' in errors.keys())
        self.assertItemsEqual(errors.keys(), ['name'])

        # invalid case with invalid nested payload
        payload = dict(name='True', age=9,
                       address=dict(street='Test street', pincode='123'))
        result, errors = validator.validate(payload)
        self.assertFalse(result)
        self.assertTrue('pincode' in errors['address'][1].keys())
        self.assertItemsEqual(errors['address'][1].keys(), ['pincode'])

    def test_validates_nested_json_when_cls_is_global_with_function_type(self):
        class AddressValidator(PayloadValidator):
            street = datatypes.Function('validate_street')
            pincode = datatypes.Function('validate_pincode')

            @staticmethod
            def validate_street(val, *args, **kwargs):
                if not isinstance(val, str):
                    return False
                if len(val) > 30:
                    return False
                return True

            def validate_pincode(self, val, *args, **kwargs):
                if not isinstance(val, str):
                    return False
                if len(val) > 6:
                    return False
                return True

        class CustomValidator(PayloadValidator):
            name = datatypes.String()
            age = datatypes.Integer()
            address = datatypes.JSON(AddressValidator)

        validator = CustomValidator()

        # valid payload
        payload = dict(name='Test', age=9,
                       address=dict(street='Test street', pincode='123'))
        result, errors = validator.validate(payload)
        self.assertTrue(result)
        self.assertTrue(errors is None)

        # invalid case
        payload = dict(name='True', age=9,
                       address=dict(street='Test street', pincode=123))
        result, errors = validator.validate(payload)
        self.assertFalse(result)
        self.assertTrue('pincode' in errors['address'][1].keys())
        self.assertItemsEqual(errors['address'][1].keys(), ['pincode'])

        # invalid case with invalid nested payload
        payload = dict(name='True', age=9,
                       address=dict(street='Test'*10, pincode='123'))
        result, errors = validator.validate(payload)
        self.assertFalse(result)
        self.assertTrue('street' in errors['address'][1].keys())
        self.assertItemsEqual(errors['address'][1].keys(), ['street'])

    def test_validates_nested_json_within_nested_json(self):
        class CustomValidator(PayloadValidator):

            class AddressValidator(PayloadValidator):
                street = datatypes.String()
                pincode = datatypes.Integer()
                region = datatypes.JSON('RegionValidator')

                class RegionValidator(PayloadValidator):
                    city = datatypes.String()
                    country = datatypes.String()

            name = datatypes.String()
            age = datatypes.Integer()
            address = datatypes.JSON(AddressValidator)

        validator = CustomValidator()

        # valid payload
        payload = dict(name='Test', age=9,
                       address=dict(street='Test street', pincode=123,
                                    region=dict(city='vns', country='in')))
        result, errors = validator.validate(payload)
        self.assertTrue(result)
        self.assertTrue(errors is None)

        # invalid case
        payload = dict(name=True, age=9,
                       address=dict(street='Test street', pincode='123',
                                    region=dict(city='vns', country=19)))
        result, errors = validator.validate(payload)
        self.assertFalse(result)
        self.assertTrue('name' in errors.keys())
        self.assertItemsEqual(errors.keys(), ['name', 'address'])
        self.assertItemsEqual(errors['address'][1].keys(),
                              ['region', 'pincode'])
        self.assertItemsEqual(errors['address'][1]['region'][1].keys(),
                              ['country'])
