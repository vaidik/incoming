import anyjson


TYPES = {
    'string': str,
    'integer': int,
    'float': float,
    'array': list,
    'boolean': bool,
    'json': dict,
    'function': None,
}


class Payload(object):
    schema = {}
    field_strict = False

    def __init__(self, payload, strict=False,
                 strict_error='Unexpected field.'):
        self._payload = payload
        self._parsed = anyjson.loads(payload)

        self.strict = strict
        self.strict_error = strict_error

    def validate(self, *args, **kwargs):
        strict = kwargs.get('strict', None) or self.strict
        strict_error = kwargs.get('strict_error', None) or self.strict_error
        errors = {}

        for key, value in self._parsed.iteritems():
            if key not in self.schema.keys():
                if strict is True:
                    errors[key] = strict_error
                continue

            # construct the right error message
            if isinstance(self.schema[key], tuple):
                match_type = self.schema[key][0][0]
                try:
                    field_error = self.schema[key][1]
                except IndexError:
                    field_error = 'Invalid value. Expected %s.' % match_type
            else:
                match_type = self.schema[key]
                field_error = 'Invalid value. Expected %s.' % match_type

            if match_type == 'function':
                method = getattr(self, self.schema[key][0][1])
                result = method(value)

                if result is True:
                    pass
                else:
                    if not isinstance(result, str):
                        result = self.schema[key][1]
                    errors[key] = result
            elif match_type == 'json':
                pass
            else:
                if not isinstance(value, TYPES[match_type]):
                    errors[key] = field_error
                else:
                    pass

        return errors
