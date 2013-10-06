.. incoming documentation master file, created by
   sphinx-quickstart on Sat Oct  5 15:42:51 2013.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Datatypes
=========

Incoming provides basic datatypes for validation. These datatypes are
responsible for performing validation tests on values. Incoming provides
some datatypes and it also allows writing your own datatypes.

.. note:: also see using :ref:`custom-validation-methods` for implementing
          custom validations.

.. _available-datatypes:

Available Datatypes
-------------------

Following datatypes are provided:

.. autoclass:: incoming.datatypes.Integer
.. autoclass:: incoming.datatypes.Float
.. autoclass:: incoming.datatypes.Number
.. autoclass:: incoming.datatypes.String
.. autoclass:: incoming.datatypes.Boolean
.. autoclass:: incoming.datatypes.Array
.. autoclass:: incoming.datatypes.Function
.. autoclass:: incoming.datatypes.JSON

.. _creating-your-datatypes:

Creating your own datatypes
---------------------------

You can create your own set of datatypes if you like.

.. note:: also see using :ref:`custom-validation-methods` for implementing
          custom validations.

A few things to keep in mind
++++++++++++++++++++++++++++

* Sub-class :class:`incoming.datatypes.Types` to implement a custom datatype.
* The sub-class must add ``_DEFAULT_ERROR`` attribute to provide the default
  error message that will be used when validation fails.
* The sub-class must implement :meth:`validate` method as a regular method or
  as a ``staticmethod`` or as a ``classmethod``.
* :meth:`validate` must return a :class:`bool` value. ``True`` if validation
  passes, ``False`` otherwise.
* :meth:`validate` method gets the following arguments:
  * ``val`` - the value which must be validated
  * ``key`` - the field/key in the payload that held ``val``.
  * ``payload`` - the entire payload that is being validated.
  * ``errors`` - :class:`incoming.incoming.PayloadErrors` object.
* For the above point mentioned above, you may want to use your
  :meth:`validate` method elsewhere outside the scope of incoming where the
  above arguments are not necessary. In that case, use ``*args`` and
  ``**kwargs``.

Example
+++++++

The example below shows how you can use a ``staticmethod`` to implement
validation test.

.. code-block:: python

    class Gender(datatypes.Types):
        _DEFAULT_ERROR = 'Gender must be either male or female.'

        @staticmethod
        def validate(val, *args, **kwargs):
            if not isinstance(val, str):
                return False
            if val.lower() not in ('male', 'female'):
                return False
            return True

    class PersonValidator(PayloadValidator):
        name = datatypes.String()
        age = datatypes.Integer()
        gender = Gender()

datatypes.Types Base Class
--------------------------

.. autoclass:: incoming.datatypes.Types

    .. automethod:: incoming.datatypes.Types.validate
