====================
README for python-ly
====================


This package provides a Python library `ly` containing various Python
modules to parse, manipulate or create documents in LilyPond format.
A command line program `ly` is also provided that can be used to do various
manipulations with LilyPond files.

The LilyPond format is a plain text input format that is used by the 
GNU music typesetter LilyPond (www.lilypond.org).

The python-ly package is Free Software, licensed under the GPL. This package 
is written by the Frescobaldi developers and is used extensively by the
Frescobaldi project. The main author is Wilbert Berendsen.

| Download from: https://pypi.org/project/python-ly
| Development homepage: https://github.com/frescobaldi/python-ly


The `ly` command line tool
--------------------------

With `ly` you can reformat, or re-indent LilyPond files, transpose music,
translate pitch names, convert LilyPond to syntax-colored HTML, etc.

There is also experimental support for converting LilyPond to MusicXML.

Use::

    ly -h

to get a full list of the features of the `ly` command.

Here is an example to re-indent and transpose a LilyPond file::

    ly "indent; transpose c d" -o output.ly file.ly

To test the `ly` module from the current directory without installing, use::

    python -m ly <args...>

This will behave like running the `ly` command when the package is installed.


The `ly` Python module
----------------------

The `ly` module supports both Python2 and Python3. This is a short description
of some modules:
  
* ``ly.slexer``: generic tools to build parsers using regular expressions
* ``ly.node``: a generic list-like node object to build tree structures with
* ``ly.document``: a tokenized text document (LilyPond file)
* ``ly.lex``: a parser for LilyPond, Scheme, and other formats, using `slexer`
* ``ly.music``: a tree structure of the contents of a document
* ``ly.pitch``: functions for translating, transposing etc
* ``ly.indent``: indent LilyPond text
* ``ly.reformat``: format LilyPond text
* ``ly.dom``: (deprecated) tree structure to build LilyPond text from
* ``ly.words``: words for highlighting and autocompletion
* ``ly.data``: layout objects, properties, interfaces, font glyphs etc extracted
  from LilyPond

Documentation
-------------

The documentation is built using Sphinx and located in the doc directory.
If you have Sphinx installed, you can build nicely formatted HTML documentation
by typing ``make html`` in the doc directory.

You can also read the docs online at http://python-ly.readthedocs.org/.

