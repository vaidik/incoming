.. incoming documentation master file, created by
   sphinx-quickstart on Sat Oct  5 15:42:51 2013.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

incoming: JSON validation framework for Python
==============================================

**incoming** is a JSON validation framework.

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

    python setup.py install

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
        'release_year': 2014
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

Tests
-----

Run tests like so::

    python setup.py test

or::

    py.test incoming

User Guide
==========

.. toctree::
   :maxdepth: 2

   payloadvalidators
   datatypes



Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

