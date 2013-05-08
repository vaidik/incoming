import anyjson


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
