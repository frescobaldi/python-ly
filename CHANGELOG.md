<!-- Please follow this spec: https://keepachangelog.com/
[X.Y.Z] links to the GitHub list of commits in a tag/release are
defined at the bottom of this file.
-->

# ChangeLog

All notable changes to the python-ly project are documented in this file.

## [0.9.8] - 2023-06-15

### Added

- Add list of string tunings (#149)

### Changed

- Add LilyPond 2.24 words (#151)
- Require Python 3.8 (#156)
- Move packaging metadata to `pyproject.toml` (#155)

### Fixed

- Fix `\set` highlighted on its own in `\set-abcd` and similar
  cases (#150)


## [0.9.7] - 2020-12-25

### Changed

- Added LilyPond 2.20 words (#140)

### Fixed

- Fixed error when making rhythm implicit per line (#144)


## [0.9.6] - 2020-01-22


### Fixed

- eps-file -> epsfile (#1213 on Frescobaldi repository)
- MusicXML output:
  - Correctly export measures without the help of explicit barchecks (#32)
  - Export \mark (#102)
  - Fix scale_rest bug (#107)
  - Stem direction is now supported (#110)
  - Fix empty measures created with no attributes (#114)

### Changed

- Various improvements to the experimental MusicXML output by Felippe Roza,
    Peter Bjuhr, Urs Liska, Endre Oma and others, thanks!
- Improved indentation of Scheme code, thanks to Paul Morris (#132)


## [0.9.5] - 2017-02-17

### Added

- Basic support for tokenizing the MUP format

### Fixed

- Fixed wrong duration handling with \partial when
  changing durations (#832 on Frescobaldi repository)
- XML export tests now work correctly with Python 3
- Fix traversing events failing in empty \alternative (#74)


## [0.9.4] - 2016-04-20

### Added

- Add simplifier transposer and simplify-accidentals ly command (#40)
- Recognize \bookOutputName A (without quotes, although not recommended)
- Allow multi-digit fingering, e.g. c-34, LilyPond supports that since at least
  2.16.
- Add ly-server: an HTTP-server for manipulating LilyPond source, contributed by
  Urs Liska


### Changed

- Support LilyPond 2.18+ behaviour on \relative without startpitch in
  the ly.pitch.transpose, ly.pitch.rel2abs and ly.pitch.abs2rel modules.
- Support LilyPond 2.18+ behaviour on \relative without startpitch in the
  transpose, rel2abs, abs2rel and musicxml ly commands. Two new variables
  were added to influence the behaviour: rel-absolute and rel-startpitch.
- Various updates and improvements in MusicXML export contributed by Peter Bjuhr

### Fixed

- Make define-markup-command recognition working again
- Do not add durations to bass notes in chordmode (#56)
- Handle \include commands correctly when exporting to MusicXML (#59)


## [0.9.3] - 2015-12-24

### Added

- Added ly.rhythm.music_items() for a more robust way of iterating through
  chords and notes (awaiting fully fledged editing support through ly.music or
  ly.xml)

### Fixed

- Do not insert duration after a tie (#35)

### Changed

- More configurability in ly.colorize, thanks to Urs Liska
- MusicXML export various improvements and bug fixes, contributed by Peter Bjuhr


## [0.9.2] - 2015-05-14

### Added

- Add the default-language variable to the ly command; this can be set to a
  language in case a LilyPond document uses a language different than
  "nederlands" but does not specify it (#20)
- Add the `-l`, `--language` option as shorthand for setting the default language
- properly support drum notes in ly.lex and ly.music

### Changed

- Updated scheme variables in ly.data.scheme* functions for LilyPond 2.18
- MusicXML export improvements:
  - support for isolated durations (a single duration without
    explicit pitch)
  - support for implicit starting pitch in relative mode
    (issues #18 and wbsoft/frescobaldi#648)

### Fixed

- Fix TypeError: expected string or buffer in dom.ly when string was a
  dom.Reference (#667 on Frescobaldi repository)
- Fix issue #16: Duration after `\skip` may not be removed


## [0.9.1] - 2015-03-08

### Changed

- Updated LilyPond data to 2.18

## [0.9] - 2015-03-07

### Added

- Added ly.rests containing various rest manipulations
- A script `xml-export.ily` has been included to dump the music structure
  inside LilyPond to an XML file. This is not used yet, but could be used in the
  future to use LilyPond to parse files and build music, and then export it
  to other formats.

### Changed

- Robust Python 3 support, Python 3 is now recommended, although 2.7 will
  still be supported for the foreseeable future.
- MusicXML export improvements

### Fixed

- Don't yield the duration in a \tuplet command as a music token (issue
  wbsoft/frescobaldi#631)


## [0.8] -- 2015-01-24

### Added

- Basic api documentation included

### Fixed

- Fix (albeit experimental) musicxml export


## [0.7] - 2015-01-23

### Changed

- First release as an officially separate project from Frescobaldi
- Add INSTALL.md to source distribution

## [0.6] - 2015-01-23

### Changed

- node and slexer are no longer toplevel modules; only the ly package

## [0.5] - 2015-01-21

### Changed

- Large MusicXML export improvements, contributed by Peter Bjuhr (MusicXML
  export is still experimental)

### Fixed

- Handle german pitch names asas and heses correctly when writing those
- Don't transpose chord argument of \stringTuning command
- Python 3 robustness improvements

## [0.4] - 2014-03-05

### Changed

- Small MusicXML export improvements, contributed by Peter Bjuhr (MusicXML
  export is still very experimental)

### Fixed

- Fix transposing when alterations would be more than a double sharp or double
  flat; handle it by moving the note, just like LilyPond does it
- Python 3 installation fixes

## [0.3] - 2014-02-05


### Added

- New command 'highlight' ('hl') to create syntax-highlighted HTML files of
  LilyPond source files (or any file that is understood by ly.lex)
- New, very experimental, command 'musicxml' to export music to MusicXML

## [0.2] - 2014-01-08

### Added

- New commands 'abs2rel' and 'rel2abs' that convert \relative music to
  absolute and vice versa
- Support for Python 3. Not all of the ly python module has already been
  tested, but installing and running the various ly commands works well.

## [0.1] - 2014-01-07

Initial release.



[0.8]: https://github.com/frescobaldi/frescobaldi/compare/v0.7..v0.8
[0.9]: https://github.com/frescobaldi/frescobaldi/compare/v0.8..v0.9
[0.9.1]: https://github.com/frescobaldi/frescobaldi/compare/v0.9..v0.9.1
[0.9.2]: https://github.com/frescobaldi/frescobaldi/compare/v0.9.1..v0.9.2
[0.9.3]: https://github.com/frescobaldi/frescobaldi/compare/v0.9.2..v0.9.3
[0.9.4]: https://github.com/frescobaldi/frescobaldi/compare/v0.9.3..v0.9.4
[0.9.5]: https://github.com/frescobaldi/frescobaldi/compare/v0.9.4..v0.9.5
[0.9.6]: https://github.com/frescobaldi/frescobaldi/compare/v0.9.5..v0.9.6
[0.9.7]: https://github.com/frescobaldi/frescobaldi/compare/v0.9.6..v0.9.7
[0.9.8]: https://github.com/frescobaldi/frescobaldi/compare/v0.9.7..v0.9.8
