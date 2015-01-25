==========
Installing
==========

This package uses a distutils setup script. As the module is written in pure
Python, no build procedure is needed. You can install python-ly using::

    python setup.py install


If you want to install into /usr instead of /usr/local::

    python setup.py install --prefix=/usr


If you have a Debian-based system such as Ubuntu, and you get an error
message like "ImportError: No module named ly.cli.main", try::

    python setup.py install --install-layout=deb


See the distutils documentation for more install options.

Building the documentation
--------------------------

The documentation resides in the ``doc`` directory and can be built using
the Sphinx toolchain (http://sphinx-doc.org/).

Typing ``make html`` in the ``doc`` directory generates full HTML documentation
in the ``doc/build/html` directory.

Typing ``make man`` in the ``doc`` directory generates a manpage for the ``ly``
command. This manpage is created in ``doc/build/man/ly.1`` and can be installed
on UNIX systems in a location like ``/usr/share/man/man1/``.

The documentation is not installed by default.

