incoming: JSON validation framework for Python
==============================================

**incoming** is a JSON validation framework.

|Build Status| |Coverage Status|

.. |Build Status| image:: https://travis-ci.org/vaidik/incoming.png
   :target: https://travis-ci.org/vaidik/incoming
.. |Coverage Status| image:: https://coveralls.io/repos/vaidik/incoming/badge.png?branch=master
   :target: https://coveralls.io/r/vaidik/incoming?branch=master

Overview
--------

Validating anything can get really messy. JSON being one of the most used
formats for data exchange, **incoming** aims at solving the problem of
validating JSON with structure and ease.

**incoming** is a small framework for validating JSON. Its up to you where and
how to use it. A common use-case (and the primary reason why I wrote this
framework) was using it for writing HTTP servers to validate incoming JSON
payload.

Features
++++++++

* Classes that can be sub-classed for writing structured validators.
* Basic validators (or `datatypes`) for performing common validations, like
  string, numbers, booleans, lists, nested JSON, etc.
* Allows extending validators (`datatypes`) to write your own.
* Allows writing callables for validating values.
* Captures errors during validation and returns a complete report of errors.
* Allows reporting different errors for different validation test failures for
  the same value.

Installation
------------

Installation is simple.

.. code:: bash

    pip install incoming

Basic Usage
-----------

.. code-block:: python

    import json

    from datetime import date
    from incoming import datatypes, PayloadValidator


    class MovieValidator(PayloadValidator):

        name = datatypes.String()
        rating = datatypes.Function('validate_rating',
                                    error='Rating must be in between 1 and 10.')
        actors = datatypes.Array()
        is_3d = datatypes.Boolean()
        release_year = datatypes.Function('validate_release_year',
                                          error=('Release year must be in between '
                                                 '1800 and current year.'))

        # validation method can be a regular method
        def validate_rating(self, val, *args, **kwargs):
            if not isinstance(val, int):
                return False

            if val < 1 or val > 10:
                return False

            return True

        # validation method can be a staticmethod as well
        @staticmethod
        def validate_release_year(val, *args, **kwargs):
            if not isinstance(val, int):
                return False

            if val < 1800 or val > date.today().year:
                return False

            return True

    payload = {
        'name': 'Avengers',
        'rating': 5,
        'actors': [
            'Robert Downey Jr.',
            'Samual L. Jackson',
            'Scarlett Johansson',
            'Mark Ruffalo'
        ],
        'is_3d': True,
        'release_year': 2012
    }
    result, errors = MovieValidator().validate(payload)
    assert result and errors is None, 'Validation failed.\n%s' % json.dumps(errors, indent=2)

    payload = {
        'name': 'Avengers',
        'rating': 11,
        'actors': [
            'Robert Downey Jr.',
            'Samual L. Jackson',
            'Scarlett Johansson',
            'Mark Ruffalo'
        ],
        'is_3d': 'True',
        'release_year': 9000
    }
    result, errors = MovieValidator().validate(payload)
    assert result and errors is None, 'Validation failed.\n%s' % json.dumps(errors, indent=2)

Run the above script, you shall get a response like so::

    Traceback (most recent call last):
      File "code.py", line 67, in <module>
        assert result and errors is None, 'Validation failed.\n%s' % json.dumps(errors, indent=2)
    AssertionError: Validation failed.
    {
      "rating": [
        "Rating must be in between 1 and 10."
      ],
      "is_3d": [
        "Invalid data. Expected a boolean value."
      ],
      "release_year": [
        "Release year must be in between 1800 and current year."
      ]
    }

Documentation
-------------

Documentation is available on `Read The Docs`_.

.. _Read The Docs: http://incoming.readthedocs.org/en/latest/

Tests
-----

Run tests like so::

    python setup.py test

or::

    py.test incoming

Contributors
------------

- `Vaidik Kapoor <http://github.com/vaidik>`_ (Author)
- `Dhruv Baldawa <http://github.com/dhruvbaldawa>`_
- `James Rowe <http://github.com/JNRowe>`_

Licence
-------

See `LICENCE`_.

.. _LICENCE: https://github.com/vaidik/incoming/blob/master/LICENSE
