'''
    incoming.datatypes
    ~~~~~~~~~~~~~~~~~~

    Datatypes that can be used to define the rules of validation.
'''

from .compat import string_type


class Types(object):

    '''
    Base class for creating new datatypes for validation. When this class is
    sub-classed, :meth:`validate` must be implemented in the sub-class and
    this method will be resposible for the actual validation.
    '''

    def __init__(self, required=None, error=None, *args, **kwargs):
        '''
        :param bool required: if a particular (this) field is required or not.
                              This param allows specifying field level setting
                              if a particular field is required or not.
        :param str error: a generic error message that will be used by
                          :class:`incoming.PayloadValidator` when the
                          validation test fails.
        '''

        self.required = required
        self.error = error or self._DEFAULT_ERROR

    def validate(self, val, *args, **kwargs):
        '''
        This method must be overridden by the sub-class for implementing the
        validation test. The overridden method can be a regular method or
        ``classmethod`` or ``staticmethod``. This method must only return a
        :class:`bool` value.

        :param val: the value that has to be validated.

        :returns bool: if the implemented validation test passed or not.
        '''

        raise NotImplementedError('validate() method must be implemented in '
                                  'the sub-class.')

    def test(self, key, val, payload, errors):
        '''
        Responsible for running the validate method. This method hides the gory
        checks of identifying if the validate method is a normal method or a
        ``staticmethod`` or a ``classmethod``. This method is more of a helper
        for :class:`incoming.PayloadValidator`.

        :param str key: the key who's value is going to get validated.
        :param val: the value on which the test is to be validated.
        :param payload: the entire payload to which the key and val belong to.
        :param errors: a reference to list of errors for the key.
        :returns bool: if the validation passed, depends on validate.
        '''

        try:
            method = getattr(self, 'validate')
        except AttributeError:
            try:
                method = self.__class__.validate
            except AttributeError:
                raise NotImplementedError('validate() must be implemented '
                                          'either as a method of the class or'
                                          'a staticmethod of the class.')

        result = method(val, key=key, payload=payload, errors=errors)

        # Check if the value returned by the validate method is a boolean
        if not isinstance(result, bool):
            raise TypeError('The value returned by validate() method must be '
                            'a bool value.')

        if not result:
            errors.insert(0, self.error)
            return False

        return True


class Instance(Types):
    '''
    Sub-class of :class:`Types` class for Integer type. Validates if a value is
    of a given type or not.

    This class should not be used directly, it should be subclassed
    '''
    type_ = None

    @classmethod
    def validate(cls, val, *args, **kwargs):
        if cls.type_ is None:
            raise NotImplementedError
        else:
            return isinstance(val, cls.type_)


class Integer(Instance):

    '''
    Sub-class of :class:`Types` class for Integer type. Validates if a value is
    a :class:`int` value.
    '''

    _DEFAULT_ERROR = 'Invalid data. Expected an integer.'
    type_ = int


class Float(Instance):

    '''
    Sub-class of :class:`Types` class for Float type. Validates if a value is
    a :class:`float` value.
    '''

    _DEFAULT_ERROR = 'Invalid data. Expected a float.'
    type_ = float


class Number(Instance):

    '''
    Sub-class of :class:`Types` class for Number type. Validates if a value is
    a :class:`int` value or :class:`float` value.
    '''

    _DEFAULT_ERROR = 'Invalid data. Expected an integer or a float).'
    type_ = (int, float)


class String(Instance):

    '''
    Sub-class of :class:`Types` class for String type. Validates if a value is
    a :class:`str` value or :class:`unicode` value.
    '''

    _DEFAULT_ERROR = 'Invalid data. Expected a string.'
    type_ = string_type


class Array(Instance):

    '''
    Sub-class of :class:`Types` class for Array type. Validates if a value is
    a :class:`list` object.
    '''

    _DEFAULT_ERROR = 'Invalid data. Expected an array.'
    type_ = list


class Boolean(Instance):

    '''
    Sub-class of :class:`Types` class for Boolean type. Validates if a value is
    a :class:`bool`.
    '''

    _DEFAULT_ERROR = 'Invalid data. Expected a boolean value.'
    type_ = bool


class Function(Types):

    '''
    Sub-class of :class:`Types` class for Function type. This type allows using
    functions for validation. Using :class:`incoming.datatypes.Function`,
    validation tests can be written in a function or a regular method, a
    ``staticmethod`` or a ``classmethod`` on the sub-class of
    :class:`incoming.PayloadValidator`.
    '''

    _DEFAULT_ERROR = 'Invalid data.'

    def __init__(self, func, *args, **kwargs):
        '''
        :param func: any callable that accepts ``val``, ``*args`` and
                     ``**kwawrgs`` and returns a :class:`bool` value, True
                     if ``val`` validates, False otherwise.
        '''

        if not callable(func) and not isinstance(func, str):
            raise TypeError('function must be a callable or a string '
                            'representing method belonging to the validator '
                            'class.')

        self.func = func

        super(Function, self).__init__(*args, **kwargs)

    def validate(self, val, *args, **kwargs):
        result = self.func(val, *args, **kwargs)
        if not isinstance(result, bool):
            raise ValueError('Validation function does not return a bool.')

        return result


class JSON(Types):

    '''
    Sub-class of :class:`Types` class for JSON type. This type allows writing
    validation for nested JSON.
    '''

    _DEFAULT_ERROR = 'Invalid data. Expected JSON.'

    def __init__(self, cls, *args, **kwargs):
        '''
        :param cls: sub-class of :class:`incoming.PayloadValidator` for
                    validating nested JSON. Class object can be accepted. In
                    case you want to have the class nested withing the parent
                    validator, you can pass the name of the class as a string
                    as well.
        '''

        self.cls = cls
        super(JSON, self).__init__(*args, **kwargs)

    def validate(self, val, *args, **kwargs):
        if not isinstance(val, dict):
            return False

        obj = self.cls()
        is_valid, result = obj.validate(val)

        if not is_valid:
            kwargs['errors'].append(result)
            return False

        return True
