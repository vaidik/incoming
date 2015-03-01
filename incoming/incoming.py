'''
    incoming.incoming
    ~~~~~~~~~~~~~~~~~

    Core module for the framework.
'''

import copy

from .compat import iteritems
from .datatypes import Function, JSON, Types


class PayloadErrors(object):

    '''
    PayloadErrors holds errors detected by :class:`PayloadValidator` and
    provides helper methods for working with errors. An instance of this
    class maintains a dictionary of errors where the keys are supposed to be
    the type of error and the value of the keys are :class:`list` objects that
    hold error strings.

    Ideally, the keys should be name of the field/key in the payload and the
    value should be a :class:`list` object that holds errors related to that
    field.
    '''

    def __init__(self):
        self._errors = {}

    def __getitem__(self, key):
        if key not in self._errors:
            self._errors[key] = []
        return self._errors[key]

    def has_errors(self):
        '''
        Checks if any errors were added to an object of this class.

        :returns bool: True if has errors, else False.
        '''

        return True if len(self.to_dict().keys()) else False

    def to_dict(self):
        '''
        Return a :class:`dict` of errors with keys as the type of error and
        values as a list of errors.

        :returns dict: a dictionary of errors
        '''

        errors = copy.deepcopy(self._errors)
        for key, val in iteritems(self._errors):
            if not len(val):
                errors.pop(key)
        return errors

    def __contains__(self, key):
        '''
        Override ``in`` operator. When ``in`` operator is used on an instance
        of this class, a check for membership in the type of errors will be
        performed.

        :param str key: key or type of error to be looked up.
        :returns bool: the test result of membership of the provided key
        '''

        return key in self.to_dict().keys()


class PayloadValidator(object):

    '''
    Main validator class that must be sub-classed to define the schema for
    validating incoming payload.
    '''

    #: If all fields/keys are required by default
    #: When required is set in the :class:`incoming.PayloadValidator`
    #: sub-class, then all the fields are required by default. In case a field
    #: must not be required, it should be set at the field/key level.
    #:
    #: .. note:: this attribute can be overridden in the sub-class.
    required = True

    #: Error message used for reporting when a required field is missing
    #:
    #: .. note:: this attribute can be overridden in the sub-class.
    required_error = 'Expecting a value for this field.'

    #: ``strict`` mode is off by default.
    #: ``strict`` mode makes sure that any field that is not defined in the
    #: schema, validation result would fail and the extra key would be reported
    #: in errors.
    #:
    #: .. note:: this attribute can be overridden in the sub-class.
    strict = False

    #: The error message that will be used when ``strict`` mode is on and an
    #: extra field is present in the payload.
    #:
    #: .. note:: this attribute can be overridden in the sub-class.
    strict_error = 'Unexpected field.'

    def __init__(self, *args, **kwargs):
        self._fields = self._collect_fields()
        self._string_args_replaced = False

    def _collect_fields(self):
        '''
        Collects all the attributes that are instance of
        :class:`incoming.datatypes.Types`. These attributes are used for
        defining rules of validation for every field/key in the incoming JSON
        payload.

        :returns: a tuple of attribute names from an instance of a sub-class
                  of :class:`PayloadValidator`.
        '''

        fields = []
        for prop in dir(self):
            if isinstance(getattr(self, prop), Types):
                fields.append(prop)

        if not len(fields):
            raise Exception('No keys/fields defined in the validator class.')

        return tuple(fields)

    def _replace_string_args(self):
        '''
        A helper method that makes passing custom validators implemented as
        methods to :class:`incoming.datatypes.Function` instances.
        '''

        if self._string_args_replaced:
            return

        for field in self._fields:
            field = getattr(self, field)
            if isinstance(field, Function):
                if isinstance(field.func, str):
                    field.func = getattr(self, field.func)
            elif isinstance(field, JSON):
                if isinstance(field.cls, str):
                    field.cls = getattr(self, field.cls)

        self._string_args_replaced = True

    def validate(self, payload, required=None, strict=None):
        '''
        Validates a given JSON payload according to the rules defiined for all
        the fields/keys in the sub-class.

        :param dict payload: deserialized JSON object.
        :param bool required: if every field/key is required and must be
                              present in the payload.
        :param bool strict: if :py:meth:`validate` should detect and report any
                            fields/keys that are present in the payload but not
                            defined in the sub-class.

        :returns: a tuple of two items. First item is a :class:`bool`
                  indicating if the payload was successfully validated and the
                  second item is ``None``. If the payload was not valid, then
                  then the second item is a :py:class:`dict` of errors.
        '''

        # replace datatypes.Function.func if not already replaced
        self._replace_string_args()

        required = required if required is not None else self.required
        strict = strict if strict is not None else self.strict

        errors = PayloadErrors()
        fields = copy.deepcopy(list(self._fields))

        for key, value in iteritems(payload):
            if key not in self._fields:
                if strict:
                    errors[key].append(self.strict_error)
            else:
                getattr(self, key).test(key, value, payload=payload,
                                        errors=errors[key])

                # Remove the key that has been checked
                fields.remove(key)

        for field in fields:
            rule = getattr(self, field)

            if rule.required is None:
                required = required
            else:
                required = rule.required

            if required:
                errors[field].append(self.required_error)
            elif isinstance(rule, Function):
                rule.test(field, payload.get(field, None),
                          payload=payload, errors=errors[field])

        return (False, errors.to_dict()) if errors.has_errors() else (True,
                                                                      None)
