==========
Installing
==========

See `Installing Packages <pug-installing_>`_ in the Python Packaging User Guide
for help on installing Python packages such as python-ly.


Building the documentation
--------------------------

The documentation resides in the ``doc`` directory and can be built using
the Sphinx toolchain (http://sphinx-doc.org/).

Typing ``make html`` in the ``doc`` directory generates full HTML documentation
in the ``doc/build/html`` directory.

Typing ``make man`` in the ``doc`` directory generates a manpage for the ``ly``
command. This manpage is created in ``doc/build/man/ly.1`` and can be installed
on UNIX systems in a location like ``/usr/share/man/man1/``.

The documentation is not installed by default.



.. _pug-installing: https://packaging.python.org/en/latest/tutorials/installing-packages/
