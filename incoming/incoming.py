import anyjson


class Types(object):
    def __init__(self, *args, **kwargs):
        self.error = kwargs.get('error', None) or self._default_error

    def validate(self, val, *args, **kwargs):
        raise NotImplementedError('validate() method must be implemented in '
            'the sub-class.')

    def test(self, payload_obj, key, val, payload):
        try:
            method = getattr(self, 'validate')
        except AttributeError:
            try:
                method = self.__class__.validate
            except AttributeError:
                raise NotImplementedError('validate() must be implemented '
                    'either as a method of the class or a staticmethod of the '
                    'class.')

        if not method(val, key=key, payload=payload, payload_obj=payload_obj):
            payload_obj.error_prepend(key, self.error)
            return False

        return True


class Integer(Types):
    def __init__(self, *args, **kwargs):
        self._default_error = 'Invalid data. Expected an integer.'

        super(Integer, self).__init__(*args, **kwargs)

    @staticmethod
    def validate(val, *args, **kwargs):
        if not isinstance(val, int):
            return False

        return True


class Float(Types):
    def __init__(self, *args, **kwargs):
        self._default_error = 'Invalid data. Expected a float.'

        super(Float, self).__init__(*args, **kwargs)

    @staticmethod
    def validate(val, *args, **kwargs):
        if not isinstance(val, float):
            return False

        return True


class Number(Types):
    def __init__(self, *args, **kwargs):
        self._default_error = 'Invalid data. Expected an integer or a float).'

        super(Number, self).__init__(*args, **kwargs)

    @staticmethod
    def validate(val, *args, **kwargs):
        if not Integer.validate(val) and not Float.validate(val):
            return False

        return True


class String(Types):
    def __init__(self, *args, **kwargs):
        self._default_error = 'Invalid data. Expected a string.'

        super(String, self).__init__(*args, **kwargs)

    @staticmethod
    def validate(val, *args, **kwargs):
        if not isinstance(val, str):
            return False

        return True


class Array(Types):
    def __init__(self, *args, **kwargs):
        self._default_error = 'Invalid data. Expected an array.'

        super(Array, self).__init__(*args, **kwargs)

    @staticmethod
    def validate(val, *args, **kwargs):
        if not isinstance(val, list):
            return False

        return True


class Boolean(Types):
    def __init__(self, *args, **kwargs):
        self._default_error = 'Invalid data. Expected a boolean value.'

        super(Boolean, self).__init__(*args, **kwargs)

    @staticmethod
    def validate(val, *args, **kwargs):
        if not isinstance(val, bool):
            return False

        return True


class Function(Types):
    def __init__(self, method=None, function=None, *args, **kwargs):
        if method is not None and function is not None:
            raise TypeError('Amongst method and function attributes, only one '
                'must be provided.')
        elif method is None and function is None:
            raise TypeError('Either method or function attribute must be '
                'provided.')

        self.method = method
        self.function = function

        self._default_error = 'Invalid data.'
        super(Function, self).__init__(*args, **kwargs)

    def validate(self, val, *args, **kwargs):
        payload_obj = kwargs['payload_obj']

        # if a method from implemented class is provided
        if self.method:
            try:
                caller = getattr(payload_obj, self.method)
            except AttributeError:
                try:
                    caller = getattr(payload_obj.__class__, self.method)
                except AttributeError:
                    raise NotImplementedError('method %s() has not been '
                        'implemented.' % self.method)

        # if a global function is provided
        else:
            caller = self.function

        if not caller(val, *args, **kwargs):
            return False

        return True


class JSON(Types):
    def __init__(self, cls, *args, **kwargs):
        self._default_error = 'Invalid data. Expected JSON.'

        self.cls = cls

        super(JSON, self).__init__(*args, **kwargs)

    def validate(self, val, *args, **kwargs):
        if not isinstance(val, dict):
            return False

        payload_obj = kwargs['payload_obj']

        obj = self.cls(anyjson.dumps(val))
        is_valid, result = obj.validate()

        if not is_valid:
            payload_obj.error_push(kwargs['key'], result)
            return False

        return True


class Payload(object):
    schema = {}
    field_strict = False
    required = True

    def __init__(self, payload, required=True, strict=False,
                 strict_error='Unexpected field.'):
        self._payload = payload
        self._parsed = anyjson.loads(payload)

        self.required = required

        self.strict = strict
        self.strict_error = strict_error

        self._errors = {}

    def error_push(self, key, error):
        try:
            self._errors[key].append(error)
        except KeyError:
            self._errors[key] = [error]

    def error_prepend(self, key, error):
        try:
            self._errors[key].insert(0, error)
        except:
            self._errors[key] = [error]

    def validate(self, *args, **kwargs):
        strict = kwargs.get('strict', None) or self.strict
        strict_error = kwargs.get('strict_error', None) or self.strict_error
        errors = {}

        fields = self.schema.keys()

        for key, value in self._parsed.iteritems():
            if key not in self.schema.keys():
                if strict is True:
                    errors[key] = strict_error
                continue

            properties = self.schema[key]
            for rule in properties['rules']:
                if key == 'class':
                    #import pdb; pdb.set_trace()
                    pass
                rule.test(self, key, value, self._parsed)

            fields.remove(key)

        for field in fields:
            if self.schema[field].get('required', self.required):
                self.error_push(field, self.schema[field].get('missing_error',
                                                              None)
                    or 'Expecting a value for this field.')

        errors = self._errors.copy()
        self._errors = {}

        return (False, errors) if len(errors.keys()) else (False, None)
