Writing Validators
==================

:class:`PayloadValidator` is the main validator class that must be
sub-classed to write validators for validating your JSON. For example:

    >>> class PersonValidator(PayloadValidator):
    ...    name = datatypes.String()
    ...    age = datatypes.Integer()
    >>>
    >>> payload = dict(name='Man', age=23)
    >>> PersonValidator().validate(payload)
    (True, None)

Every field/key in the payload that you wish to validate must be added as an
attribute in the sub-class of :class:`incoming.PayloadValidator`. The attribute
must be initialized and should be a an object of one of the classes of
:class:`incoming.datatypes`. These classes provide validation tests. See the
:ref:`available-datatypes`. And see :ref:`creating-your-datatypes`.

Validating Nested JSON
----------------------

Validating nested JSON is similar to how you validate payloads without nested
JSON. What you do is that you write a separate validator for nested JSON as
well and use the :class:`incoming.datatypes.JSON` datatype to tell incoming
to use another validator for the nested JSON.

Global Validator Class for Nested JSON
++++++++++++++++++++++++++++++++++++++

Here is an example of writing validators for nested JSON::

    >>> class AddressValidator(PayloadValidator):
    ...     street = datatypes.String()
    ...     country = datatypes.String()
    ...
    >>> class PersonValidator(PayloadValidator):
    ...     name = datatypes.String()
    ...     age = datatypes.Integer()
    ...     address = datatypes.JSON(AddressValidator)
    ...
    >>> PersonValidator().validate(dict(name='Some name', age=19, address=dict(street='Brannan, SF', country='USA')))
    (True, None)
    >>>
    >>> PersonValidator().validate(dict(name='Some name', age=19, address=dict(street='Brannan, SF', country=0)))
    (False, {'address': ['Invalid data. Expected JSON.', {'country': ['Invalid data. Expected a string.']}]})

Nested Validator Class for Nested JSON
++++++++++++++++++++++++++++++++++++++

Here is another way of writing the above example where the ``AddressValidator``
is a nested class of ``PersonValidator``::

    >>> class PersonValidator(PayloadValidator):
    ...     name = datatypes.String()
    ...     age = datatypes.Integer()
    ...     
    ...     # Note that the validator class' name is provided as a str value
    ...     address = datatypes.JSON('AddressValidator')
    ...     
    ...     class AddressValidator(PayloadValidator):
    ...         street = datatypes.String()
    ...         country = datatypes.String()
    ...
    >>> PersonValidator().validate(dict(name='Some name', age=19, address=dict(street='Brannan, SF', country='USA')))
    (True, None)
    >>>
    >>> PersonValidator().validate(dict(name='Some name', age=19, address=dict(street='Brannan, SF', country=0)))
    (False, {'address': ['Invalid data. Expected JSON.', {'country': ['Invalid data. Expected a string.']}]})

.. note:: when the validator class is nested, the name of the class must be
          provided as an :class:`str` value.

Custom error messages for every field
-------------------------------------

Every ``datatype`` provides its own default error message (``_DEFAULT_ERROR``)
which are very generic and good enough if you are using just those datatypes
and not validation functions. However, you would mostly want to have your own
error messages for every field according to your application's requirements.

:mod:`incoming` allows you to specify different error messages for every field
so that whenever validation fails, these error messages are used instead of the
default error messages.

For example:

.. code-block:: python

    def validate_age(val, *args, **kwargs):
        if not isinstance(val, int):
            return False
        if val < 0:
            return False
        return True

    class PersonValidator(PayloadValidator):
        required = False

        name = datatypes.String(required=True, error='Name must be a string.')
        age = datatypes.Function(validate_age,
                                 error='Age can never be negative.')
        hobbies = datatypes.Array(error='Please provide hobbies in an array.')

.. _custom-validation-methods:

Custom validation methods
-------------------------

``incoming`` lets you write custom validation methods for validating complex
cases as well. These functions must return a :class:`bool`, ``True`` if
validation passes, else ``False``.

A few things to keep in mind
++++++++++++++++++++++++++++

* A validation function can be any callable. The callable should be passed to
  :class:`incoming.datatypes.Function` as an argument.
* If the callable is a regular method or ``classmethod`` or ``staticmethod`` on
  on the validator class, then pass just the name of the method as a string.
* Validation functions (callables) must return :class:`bool` values only.
  ``True`` shall be passed when the validation test passes, ``False``
  otherwise.
* Validation callables get the following arguments:
  * ``val`` - the value which must be validated
  * ``key`` - the field/key in the payload that held ``val``.
  * ``payload`` - the entire payload that is being validated.
  * ``errors`` - :class:`incoming.incoming.PayloadErrors` object.
* For the above point mentioned above, you may want to use your validation
  methods elsewhere outside the scope of :mod:`incoming` where the above
  arguments are not necessary. In that case, use ``*args`` and ``**kwargs``.

Writing validation functions
++++++++++++++++++++++++++++

Write your validation functions anywhere and pass
:class:`incoming.datatypes.Function` the function you have written for
validation.

.. code-block:: python

    def validate_age(val, *args, **kwargs):
        if not isinstance(val, int):
            return False
        if val < 0:
            return False
        return True

    class PersonValidator(PayloadValidator):
        required = False
        name = datatypes.String(required=True)
        age = datatypes.Function(validate_age)
        hobbies = datatypes.Array()

Validation functions bound by other classes
+++++++++++++++++++++++++++++++++++++++++++

If you would like to organize your validation functions by keeping them in
a different class for some sort of organization that you prefer, you can do
that like so:

.. code-block:: python

    class Validations(object):
        # You can write staticmethods
        @staticmethod
        def validate_age(val, *args, **kwargs):
            if not isinstance(val, int):
                return False
            if val < 0:
                return False
            return True

        # You can write classmethods as well
        @classmethod
        def validate_hobbies(val, *args, **kwargs):
            if not isinstance(val, list):
                return False
            return True

    class PersonValidator(PayloadValidator):
        required = False

        name = datatypes.String(required=True)
        age = datatypes.Function(Validations.validate_age)
        hobbies = datatypes.Function(Validations.validate_hobbies)

Validation methods in :class:`incoming.PayloadValidator` sub-classes
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

For the sake of organization, it would probably make more sense to have all the
validation methods in your validator classes. You can do that like so:

.. code-block:: python

    class PersonValidator(PayloadValidator):
        required = True

        name = datatypes.String()

        # Note that validation method's name is provided as an str value
        age = datatypes.Function('validate_age')
        hobbies = datatypes.Function('validate_hobbies')
        sex = datatypes.Function('validate_sex')

        # You can write regular methods for validation
        def validate_age(self, val, *args, **kwargs):
            if not isinstance(val, int):
                return False
            if val < 0:
                return False
            return True

        # You can write staticmethods for validation
        @staticmethod
        def validate_hobbies(val, *args, **kwargs):
            if not isinstance(val, list):
                return False
            return True

        # You can write classmethods for validation
        @classmethod
        def validate_sex(cls, val, *wargs, **kwargs):
            if val not in ('male', 'female'):
                return False
            return True

Specifying required fields
--------------------------

``required`` can be set on all the fields or on particular fields as well. All
fields are required by default. You can explicitly specify this like so::

    >>> class PersonValidator(PayloadValidator):
    ...    required = False
    ...
    ...    name = datatypes.String(required=True)
    ...    age = datatypes.Integer(required=True)
    ...    hobbies = datatypes.Array()
    >>>
    >>> payload = dict(name='Man', age=23)
    >>> PersonValidator().validate(payload)
    (True, None)

Depending upon your use-case, you may have more required fields than fields
that are not required and vice-versa. :mod:`incoming` can help you with that.
The above example can be written this way as well::

    >>> class PersonValidator(PayloadValidator):
    ...    required = True
    ...
    ...    name = datatypes.String())
    ...    age = datatypes.Integer()
    ...    hobbies = datatypes.Array(required=False)
    >>>
    >>> payload = dict(name='Man', age=23)
    >>> PersonValidator().validate(payload)
    (True, None)

Overriding ``required`` at the time of validation
+++++++++++++++++++++++++++++++++++++++++++++++++

There can be some cases in which you might want to override the ``required``
setting defined in the validator class at the time of validating the payload.

This can be done like so::

    >>> class PersonValidator(PayloadValidator):
    ...    required = False
    ...
    ...    name = datatypes.String(required=True)
    ...    age = datatypes.Integer(required=True)
    ...    hobbies = datatypes.Array()
    >>>
    >>> payload = dict(name='Man', age=23)
    >>> PersonValidator().validate(payload, required=True)
    (False, {'hobbies': ['Expecting a value for this field.']})

Error messages for ``required`` fields
++++++++++++++++++++++++++++++++++++++

Check :attr:`incoming.PayloadValidator.required_error` for the default error
message for ``required`` fields i.e. when required fields are missing in the
payload.

Override this error message like so:

    >>> class PersonValidator(PayloadValidator):
    ...    required = False
    ...    required_error = 'A value for this field must be provided.'
    ...
    ...    name = datatypes.String(required=True)
    ...    age = datatypes.Integer(required=True)
    ...    hobbies = datatypes.Array()

``strict`` Mode
---------------

``strict`` mode, when turned on, makes sure that no extra key/field in the
payload is provided. If any extra key/field is provided, validation fails and
reports in the errors.

Example::

    >>> class PersonValidator(PayloadValidator):
    ...    strict = True
    ...
    ...    name = datatypes.String()
    ...    age = datatypes.Integer()
    ...    hobbies = datatypes.Array(required=False)
    >>>
    >>> payload = dict(name='Man', age=23, extra=0)
    >>> PersonValidator().validate(payload)
    (False, {'extra': ['Unexpected field.']})

.. note:: ``strict`` mode is turned **off** by default.

Overriding ``strict`` at the time of validation
+++++++++++++++++++++++++++++++++++++++++++++++

There can be some cases in which you might want to override the ``strict``
setting defined in the validator class at the time of validating the payload.

This can be done like so::

    >>> class PersonValidator(PayloadValidator):
    ...    strict = True
    ...
    ...    name = datatypes.String()
    ...    age = datatypes.Integer()
    ...    hobbies = datatypes.Array(required=False)
    >>>
    >>> payload = dict(name='Man', age=23, extra=0)
    >>> PersonValidator().validate(payload, strict=False)
    (True, None)

Error messages for ``strict`` fields
++++++++++++++++++++++++++++++++++++

Check :attr:`incoming.PayloadValidator.strict_error` for the default error
message for ``strict`` mode i.e. when ``strict`` mode is on and when extra
fields are present in the payload.

Override this error message like so::

    >>> class PersonValidator(PayloadValidator):
    ...    strict = True
    ...    strict_error = 'This field is not allowed.'
    ...
    ...    name = datatypes.String()
    ...    age = datatypes.Integer()
    ...    hobbies = datatypes.Array(required=False)

PayloadValidator Class
----------------------

.. autoclass:: incoming.PayloadValidator
    :members:

PayloadErrors Class
-------------------

.. autoclass:: incoming.incoming.PayloadErrors
    :members:
