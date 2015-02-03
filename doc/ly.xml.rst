ly.xml package
===============

Introduction
------------

This package is concerned with representing a LilyPond structure (e.g. music)
as an XML tree.

The structure of the tree closely follows LilyPond's data structures. The tree
can be parsed or analysed, and could be used to convert the music to other
formats like Mei of MusicXML.

This package tries to define the exact format (dtd or schema) of the tree.

There will be three ways to build the tree:

- by hand, by creating XML elements (maybe with use of some helper methods).
- from a tokenized document
- by LilyPond, using the ``xml-export.ily`` script that is included.

The latter case is very interesting as all the music parsing and handling
is already done by LilyPond. The exported XML nearly contains all information
of a score or music object. Below, some more information about the XML.

Note that this is all in heavy development.


Module contents
---------------

.. automodule:: ly.xml
    :members:
    :undoc-members:
    :show-inheritance:


The ``xml-export.ily`` file
---------------------------


Written by Wilbert Berendsen, jan-feb 2015

This LilyPond module defines a function (``xml-export``) that converts LilyPond
datastructures to XML. For convenience, a ``\displayLilyXML`` music function is
added that converts a music expression to XML.

Usage e.g.::

    \displayLilyXML { c d e f }

The XML closely follows the LilyPond music structure.

All ``(make-music 'MusicName ...)`` objects translate to a
``<music type="MusicName">`` tag. The music in the 'element and 'elements
properties is put in the ``<element>`` and ``<elements>`` tags. (LilyPond uses
``'element`` when there is a single music argument, and ``'elements`` for a list
of music arguments, but for example ``\repeat`` uses both: ``'element`` for the
repeated music and ``'elements`` for the ``\alternatives``.)

Thus ``<element>``, if there, always has one ``<music>`` child. ``<elements>``,
if there, can have more than one <music> child.

Besides ``'element`` and ``'elements``, the following properties of music
objects are handled specially:

- ``'origin`` => ``<origin>`` element with ``filename``, ``line`` and ``char``
  attributes
- ``'pitch`` => ``<pitch>`` element with ``octave``, ``notename`` and
  ``alteration`` attributes
- ``'duration`` => ``<duration>`` element with ``log``, ``dots``, ``numer`` and
  ``denom`` attributes
- ``'articulations`` => ``<articulations>`` element containing ``<music>``
  elements

All other properties a music object may have, are translated to a ``<property>``
element with a ``name`` attribute. The value is the child element and can be any
object (string, list, pair, symbol, number etc.). (Note that the LilyPond
command ``\displayMusic`` does not display all properties.)

Markup objects are also converted to XML, where a toplevel ``<markup>`` element
is used. The individual markup commands are converted to an ``<m>`` element,
with the name in the ``name`` attribute (e.g.
``<m name="italic"><string value="Hi there!"/></m>``). Arguments to markup
commands may be other commands, or other objects (markup ``\score`` even has
a score argument, which is also supported).

Example
-------

This LilyPond music::

  \relative {
    c d e
  }

maps to Scheme (using ``\displayMusic``)::

  (make-music
    'RelativeOctaveMusic
    'element
    (make-music
      'SequentialMusic
      'elements
      (list (make-music
              'NoteEvent
              'pitch
              (ly:make-pitch -1 0 0)
              'duration
              (ly:make-duration 2 0 1))
            (make-music
              'NoteEvent
              'pitch
              (ly:make-pitch -1 1 0)
              'duration
              (ly:make-duration 2 0 1))
            (make-music
              'NoteEvent
              'pitch
              (ly:make-pitch -1 2 0)
              'duration
              (ly:make-duration 2 0 1)))))

and maps to XML (using ``\displayLilyXML``)::

  <music name="RelativeOctaveMusic">
    <origin filename="/home/wilbert/dev/python-ly/ly/xml/xml-export.ily" line="244" char="17"/>
    <element>
      <music name="SequentialMusic">
        <origin filename="/home/wilbert/dev/python-ly/ly/xml/xml-export.ily" line="244" char="27"/>
        <elements>
          <music name="NoteEvent">
            <origin filename="/home/wilbert/dev/python-ly/ly/xml/xml-export.ily" line="245" char="4"/>
            <pitch octave="-1" notename="0" alteration="0"/>
            <duration log="2" dots="0" numer="1" denom="1"/>
          </music>
          <music name="NoteEvent">
            <origin filename="/home/wilbert/dev/python-ly/ly/xml/xml-export.ily" line="245" char="6"/>
            <pitch octave="-1" notename="1" alteration="0"/>
            <duration log="2" dots="0" numer="1" denom="1"/>
          </music>
          <music name="NoteEvent">
            <origin filename="/home/wilbert/dev/python-ly/ly/xml/xml-export.ily" line="245" char="8"/>
            <pitch octave="-1" notename="2" alteration="0"/>
            <duration log="2" dots="0" numer="1" denom="1"/>
          </music>
        </elements>
      </music>
    </element>
  </music>

The XML is currently written to standard output.
