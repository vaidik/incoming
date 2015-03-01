CHANGELOG
---------

Development Version
+++++++++++++++++++

0.3.0
*****

* Pass only the error list of a field in payload to its validator method.
* Pass errors and payload as keyword arguments.
* For fields that are not required and have Function as their type, call the
  validation method/function even if the field is missing in payload.

0.2.6
*****

* Support Python 3.

0.2.5
*****

* Abstract out datatypes that perform just Python type checks to reduce code.

0.2.4
*****

* Fix tests for Python 2.5 and 2.6. Fix README.

0.2.3
*****

* Package setup changes - added classifiers and manifest file.

0.2.1
*****

* First public release of Incoming.
