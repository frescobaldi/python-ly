# This file is part of python-ly, https://pypi.python.org/pypi/python-ly
#
# Copyright (c) 2008 - 2015 by Wilbert Berendsen
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
# See http://www.gnu.org/licenses/ for more information.

"""
LilyPond reserved words for auto completion and highlighting.
"""

from __future__ import unicode_literals

lilypond_keywords = (
    'accepts',
    'addlyrics',
    'alias',
    'consists',
    'defaultchild',
    'denies',
    # 'description',
    'grobdescriptions',  # since 2.16
    'hide',  # since 2.18
    'include',
    # 'invalid',
    'language',
    'name',
    # 'objectid',
    'omit',  # since 2.18
    'once',
    'set',
    'unset',
    'override',
    'revert',
    'remove',
    'temporary',  # since 2.18
    # 'sequential',
    # 'simultaneous',
    'type',  # since 2.14 or earlier
    'undo',  # since 2.20
    'version',
    'score',
    'book',
    'bookpart',
    'header',
    'paper',
    'midi',
    'layout',
    'with',
    'context',
    'tagGroup',  # since 2.20
    'etc',  # since 2.20
)

lilypond_music_commands = (
    'absolute',  # since 2.18
    'acciaccatura',
    'accidentalStyle',  # since 2.16
    'addChordShape',  # since 2.16
    'addInstrumentDefinition',  # deprecated in 2.23
    # 'addlyrics', # this is a keyword
    'addQuote',
    'after',  # since 2.23
    'afterGrace',
    # 'afterGraceFraction', # this is a parser variable
    'aikenHeads',
    'aikenHeadsMinor',
    'aikenThinHeads',  # since 2.23
    'aikenThinHeadsMinor',  # since 2.23
    'allowPageTurn',
    'allowVoltaHook',  # since 2.18
    'alterBroken',  # since 2.18 (?)
    'alternative',
    'ambitusAfter',  # since 2.22
    'AncientRemoveEmptyStaffContext',  # in ly/engraver-init.ly, not in docs
    'appendToTag',  # since 2.16
    'applyContext',
    'applyMusic',
    'applyOutput',
    'applySwing',  # since 2.22
    'applySwingWithOffset',  # since 2.22
    'appoggiatura',
    'arabicStringNumbers',  # since 2.20
    'arpeggio',
    'arpeggioArrowDown',
    'arpeggioArrowUp',
    'arpeggioBracket',
    'arpeggioNormal',
    'arpeggioParenthesis',
    'arpeggioParenthesisDashed',  # since 2.14 or before
    'articulate',  # since 2.14 or earlier
    'ascendens',
    'assertBeamQuant',  # since 2.20
    'assertBeamSlope',  # since 2.20
    'auctum',
    'augmentum',
    'autoAccidentals',
    'autoBeamOff',
    'autoBreaksOff',  # since 2.20
    'autoBreaksOn',  # since 2.20
    'autoBeamOn',
    'autochange',  # renamed in 2.22
    'autoChange',  # since 2.22
    'autoLineBreaksOff',  # since 2.20
    'autoLineBreaksOn',  # since 2.20
    'autoPageBreaksOff',  # since 2.20
    'autoPageBreaksOn',  # since 2.20
    'balloonGrobText',
    'balloonLengthOff',
    'balloonLengthOn',
    'balloonText',
    'bar',
    'barNumberCheck',
    'bassFigureExtendersOff',
    'bassFigureExtendersOn',
    'bassFigureStaffAlignmentDown',
    'bassFigureStaffAlignmentNeutral',
    'bassFigureStaffAlignmentUp',
    'beamExceptions',  # since 2.20
    'bendAfter',
    'bendHold',  # since 2.23
    'bendStartLevel',  # since
    'blackTriangleMarkup',
    'bookOutputName',
    'bookOutputSuffix',
    'bracketCloseSymbol',  # not in docs, in python/convertrules.py
    'bracketOpenSymbol',  # not in docs, in python/convertrules.py
    'break',
    'breathe',
    'breve',
    'cadenzaOff',
    'cadenzaOn',
    'caesura',
    'cavum',
    'change',
    'chordmode',
    'chordNameSeparator',  # not a music function, it's a property, found in ly/engraver-init.ly
    'chordPrefixSpacer',  # ditto
    'chordRootNamer',  # ditto
    'chordRepeats',  # since 2.16
    'chords',
    'clef',
    'cm',
    'codaMark',  # since 2.23
    'compoundMeter',  # since 2.16
    'compressEmptyMeasures',  # since 2.22
    'compressFullBarRests',  # renamed to compressEmptyMeasures in 2.22
    'compressMMRests',  # since 2.22
    'context',
    'cr',
    'cresc',
    'crescHairpin',
    'crescTextCresc',
    'crossStaff',  # since 2.16
    'cueClef',  # since 2.16
    'cueClefUnset',  # since 2.16
    'cueDuring',
    'cueDuringWithClef',  # since 2.16
    'dashBang',  # since 2.20
    'dashBar',  # not found in doc or code
    'dashDash',
    'dashDot',
    'dashHat',
    'dashLarger',
    'dashPlus',
    'dashUnderscore',
    'deadNote',  # since 2.16
    'deadNotesOff',  # since 2.20
    'deadNotesOn',  # since 2.20
    'decr',
    'decresc',  # since 2.14 or earlier
    'default',
    'defaultNoteHeads',  # since 2.16, not a music function, found in ly/property-init.ly
    'defaultTimeSignature',
    'defineBarLine',  # since 2.18
    'deminutum',
    'denies',
    'descendens',
    'dim',
    'dimHairpin',
    'dimTextDecr',
    'dimTextDecresc',
    'dimTextDim',
    'discant',  # since 2.18
    'displayLilyMusic',
    'displayMusic',
    'displayScheme',  # since 2.20
    'divisioMaior',
    'divisioMaxima',
    'divisioMinima',
    'dotsDown',
    'dotsNeutral',
    'dotsUp',
    'dropNote',  # since 2.22
    'drummode',
    'drumPitchTable',  # not in music functions, it's a property, found in ly/performer-init.ly
    'drums',
    'dwn',  # since 2.20
    'dynamicDown',
    'dynamicNeutral',
    'dynamicUp',
    'easyHeadsOff',
    'easyHeadsOn',
    'endcr',
    'enablePolymeter',  # since 2.23
    'endcresc',  # not found in docs, found in ly/spanners-init.ly
    'endcr',  # since 2.20, synonym for endcresc?
    'enddecr',
    'enddim',  # not found in docs, found in ly/spanners-init.ly
    # not found: 'endincipit',
    'endSpanners',
    'episemFinis',
    'episemInitium',
    'escapedBiggerSymbol',
    'escapedExclamationSymbol',
    'escapedParenthesisCloseSymbol',
    'escapedParenthesisOpenSymbol',
    'escapedSmallerSymbol',
    'eventChords',  # since 2.16
    'expandEmptyMeasures',  # since 2.22
    'expandFullBarRests',  # renamed to expandEmptyMeasures since 2.22
    'f',
    'featherDurations',
    'fermataMarkup',  # gone since 2.22
    'ff',
    'fff',
    'ffff',
    'fffff',
    'figuremode',
    'figures',
    'finalis',
    'fingeringOrientations',
    'fixed',  # since 2.20
    'flexa',
    'footnote',  # since 2.18 or earlier
    'fp',
    'freeBass',  # since 2.18
    'frenchChords',
    'fullJazzExceptions',  # not found in docs or code
    'funkHeads',
    'funkHeadsMinor',
    'fz',  # not in docs, found in ly/dynamic-scripts-init.ly
    'germanChords',
    'glide',  # since 2.23
    'glissando',
    'glissandoMap',  # since 2.20
    'grace',
    'graceSettings',  # found in internals, shouldn't be directly manipulated, found in ly/engraver-init.ly
    'harmonic',
    'harmonicByFret',  # since 2.14 or earlier
    'harmonicByRatio',  # since 2.14 or earlier
    'harmonicNote',  # since 2.20
    'harmonicsOff',  # since 2.14 or before
    'harmonicsOn',  # since 2.14 or before
    'hideKeySignature',  # since 2.14 or before
    'hideNotes',
    'hideSplitTiedTabNotes',  # since 2.14 or before
    'hideStaffSwitch',
    'huge',
    'ignatzekExceptionMusic',
    'ignatzekExceptions',
    'if',  # since 2.23
    'iij',
    'IIJ',
    'ij',
    'IJ',
    'improvisationOff',
    'improvisationOn',
    'in',
    'incipit',  # since 2.20
    'inclinatum',
    'includePageLayoutFile',
    'indent',
    'inherit-acceptability',  # since 2.20
    'inStaffSegno',  # since 2.16
    'instrumentSwitch',
    'instrumentTransposition',  # not in docs, found in ly/engraver-init.ly
    # 'interscoreline',  # not found in docs or code
    'inversion',
    'invertChords',  # since 2.22
    'italianChords',
    'jump',  # since 2.23
    'keepWithTag',
    'key',
    'kievanOff',  # since 2.20
    'kievanOn',  # since 2.20
    'killCues',
    'label',
    'laissezVibrer',
    'languageRestore',  # since 2.20
    'languageSaveAndChange',  # since 2.20
    # 'large', # already in markup section
    'ligature',
    'linea',
    'longa',
    'lyricmode',
    'lyrics',
    'lyricsto',
    'magnifyMusic',  # since 2.20
    'magnifyStaff',  # since 2.20
    'maininput',
    'majorSevenSymbol',
    'makeClusters',
    'makeDefaultStringTuning',  # since 2.20
    'mark',
    'markLengthOff',  # since 2.18
    'markLengthOn',  # since 2.18
    'markup',
    'markuplines',  # deprecated, till 2.14
    'markuplist',  # from 2.16
    'markupMap',  # since 2.20
    'maxima',
    'melisma',
    'melismaEnd',
    'mergeDifferentlyDottedOff',
    'mergeDifferentlyDottedOn',
    'mergeDifferentlyHeadedOff',
    'mergeDifferentlyHeadedOn',
    'mf',
    'mm',
    'modalInversion',  # since 2.14 or earlier
    'modalTranspose',  # since 2.14 or earlier
    'mp',
    'multi-measure-rest-by-number',  # since 2.23
    'musicMap',
    'n',  # since 2.22
    'neumeDemoLayout',
    'new',
    'newSpacingSection',
    'noBeam',
    'noBreak',
    'noPageBreak',
    'noPageTurn',
    'normalsize',
    'notemode',
    'numericTimeSignature',
    'octaveCheck',
    'offset',  # since 2.22?
    'oldaddlyrics',
    'oneVoice',
    'oriscus',
    'ottava',
    'override',
    'overrideProperty',
    'overrideTimeSignatureSettings',  # since 2.16
    'p',
    'pageBreak',
    'pageTurn',
    'palmMute',  # since 2.16
    'palmMuteOn',  # since 2.16
    'parallelMusic',
    'parenthesisCloseSymbol',  # not in the docs, lilypond/python/convertrules.py changes this to ')'
    'parenthesisOpenSymbol',  # not in the docs, lilypond/python/convertrules.py changes this to '('
    'parenthesize',
    'partcombine',  # renamed since 2.22
    'partCombine',  # since 2.22
    'partCombineApart',  # since 2.22
    'partCombineAutomatic',  # since 2.22
    'partCombineChords',  # since 2.22
    'partCombineDown',  # since 2.22
    'partCombineForce',  # since 2.22
    'partCombineListener',  # not in docs, found in ly/declarations-init.ly
    'partCombineSoloI',  # since 2.22
    'partCombineSoloII',  # since 2.22
    'partCombineUnisono',  # since 2.22
    'partCombineUp',  # since 2.22
    'partial',
    'partialJazzExceptions',  # not found in docs or code
    'partialJazzMusic',  # not found in docs or code
    'pes',
    'phrasingSlurDashed',
    'phrasingSlurDashPattern',  # since 2.14 or earlier
    'phrasingSlurDotted',
    'phrasingSlurDown',
    'phrasingSlurHalfDashed',  # since 2.14 or earlier
    'phrasingSlurHalfSolid',  # since 2.14 or earlier
    'phrasingSlurNeutral',
    'phrasingSlurSolid',
    'phrasingSlurUp',
    'pipeSymbol',  # not in doc, lilypond/python/convertrules.py changes this to '|'
    'pitchedTrill',
    'pointAndClickOff',
    'pointAndClickOn',
    'pointAndClickTypes',  # since 2.20
    'pp',
    'ppp',
    'pppp',
    'ppppp',
    'preBend',  # since 2.23
    'preBendHold',  # since 2.32
    'predefinedFretboardsOff',
    'predefinedFretboardsOn',
    'propertyOverride',  # since 2.20
    'propertyRevert',  # since 2.20
    'propertySet',  # since 2.20
    'propertyTweak',  # since 2.20
    'propertyUnset',  # since 2.20
    'pt',
    'pushToTag',  # since 2.16
    'quilisma',
    'quoteDuring',
    'raiseNote',  # since 2.22
    'reduceChords',  # since 2.20
    'relative',
    'RemoveAllEmptyStaves',  # since 2.20
    'RemoveEmptyStaves',  # since 2.14 or earlier
    'RemoveEmptyRhythmicStaffContext',  # not in docs, found in ly/engraver-init.ly
    'RemoveEmptyStaffContext',
    'removeWithTag',
    'repeat',
    'repeatTie',
    'replace',  # since 2.16
    'resetRelativeOctave',
    'responsum',
    'rest',
    'rest-by-number',  # since 2.18
    'retrograde',  # since 2.14 or earlier
    'revert',
    'revertTimeSignatureSettings',  # since 2.14 or earlier
    'rfz',
    'rightHandFinger',
    'romanStringNumbers',  # since 2.20
    'sacredHarpHeads',
    'sacredHarpHeadsMinor',
    'scaleDurations',
    # 'scoreTweak',  # not found in docs or code
    'section',  # since 2.23
    'sectionLabel',  # since 2.23
    'segnoMark',  # since 2.23
    'semiGermanChords',
    'set',
    'settingsFrom',  # since 2.20
    'sf',
    'sff',
    'sfp',
    'sfz',
    'shape',  # since 2.16
    'shiftDurations',
    'shiftOff',
    'shiftOn',
    'shiftOnn',
    'shiftOnnn',
    'showKeySignature',  # since 2.14 or earlier
    'showStaffSwitch',
    'single',  # since 2.18
    'skip',
    'skipTypesetting',
    'slashedGrace',  # since 2.20
    'slurDashed',
    'slurDashPattern',  # since 2.14 or earlier
    'slurDotted',
    'slurDown',
    'slurHalfDashed',  # since 2.14 or earlier
    'slurHalfSolid',  # since 2.14 or earlier
    'slurNeutral',
    'slurSolid',
    'slurUp',
    'small',
    'sostenutoOff',
    'sostenutoOn',
    'sourcefileline',  # since 2.20
    'sourcefilename',  # since 2.20
    'southernHarmonyHeads',
    'southernHarmonyHeadsMinor',
    'sp',
    'spacingTweaks',  # dropped in 2.23
    'spp',
    'startAcciaccaturaMusic',
    'startAppoggiaturaMusic',
    'startGraceMusic',
    'startGroup',
    'startStaff',
    'startTextSpan',
    'startTrillSpan',
    'stemDown',
    'stemNeutral',
    'stemUp',
    'stopAcciaccaturaMusic',  # defined in ly/grace-init.ly, only redefine them, never "call" them (with backslash)
    'stopAppoggiaturaMusic',  # ditto
    'stopGraceMusic',  # ditto
    'stopGroup',
    'stopStaff',
    'stopTextSpan',
    'stopTrillSpan',
    'storePredefinedDiagram',  # since 2.14 or before
    'stringTuning',  # since 2.16
    'strokeFingerOrientations',  # property of New_fingering_engraver
    'stropha',
    'styledNoteHeads',  # since 2.14 or earlier
    'sustainOff',
    'sustainOn',
    'tabChordRepeats',  # since 2.16
    'tabChordRepetition',  # since 2.14 or earlier
    'tabFullNotation',
    'tag',
    'taor',  # since 2.14 or earlier
    'teeny',
    'tempo',
    'tempoWholesPerMinute',
    'textLengthOff',
    'textLengthOn',
    'textSpannerDown',
    'textSpannerNeutral',
    'textSpannerUp',
    'tieDashed',
    'tieDashPattern',  # since 2.14 or earlier
    'tieDotted',
    'tieDown',
    'tieHalfDashed',  # since 2.20
    'tieHalfSolid',  # since 2.20
    'tieNeutral',
    'tieSolid',
    'tieUp',
    'tildeSymbol',  # not in docs, converted to '~' in python/convertrules.py
    'time',
    'times',
    'timing',
    'tiny',
    'tocItem',  # since 2.14 or before
    'tocItemWithDotsMarkup',  # since 2.20
    'transpose',
    'transposedCueDuring',
    'transposition',
    'treCorde',
    'tripletFeel',  # since 2.22
    'tuplet',  # since 2.18
    'tupletDown',
    'tupletNeutral',
    'tupletSpan',  # since 2.18
    'tupletUp',
    'tweak',
    'unaCorda',
    'unfolded',  # since 2.23
    'unfoldRepeats',
    'unHideNotes',
    'unless',  # since 2.23
    'unit',  # scheme function?  not a music function or command
    'unset',
    'versus',
    'virga',
    'virgula',
    'voiceFour',
    'voiceFourStyle',
    'voiceNeutralStyle',
    'voiceOne',
    'voiceOneStyle',
    'voices',  # since 2.20
    'voiceThree',
    'voiceThreeStyle',
    'voiceTwo',
    'voiceTwoStyle',
    'void',  # since 2.16
    'vshape',  # since 2.23
    'vowelTransition',  # since 2.22
    'walkerHeads',
    'walkerHeadsMinor',
    'whiteTriangleMarkup',
    'withMusicProperty',
    'xNote',  # since 2.20
    'xNotesOff',  # since 2.20
    'xNotesOn',  # since 2.20
)

articulations = (
    'accent',
    'espressivo',
    'marcato',
    'portato',
    'staccatissimo',
    'staccato',
    'tenuto',
)

ornaments = (
    'prall',
    'mordent',
    'prallmordent',
    'turn',
    'upprall',
    'downprall',
    'upmordent',
    'downmordent',
    'lineprall',
    'prallprall',
    'pralldown',
    'prallup',
    'reverseturn',
    'trill',
    'slashturn',  # since 2.22
    'haydnturn',  # since 2.22
)

fermatas = (
    'shortfermata',
    'fermata',
    'longfermata',
    'verylongfermata',
    'veryshortfermata',  # since 2.22
    'henzeshortfermata',  # since 2.22
    'henzelongfermata',  # since 2.22
)

instrument_scripts = (
    'upbow',
    'downbow',
    'flageolet',
    'thumb',
    'snappizzicato',
    'open',
    'halfopen',
    'stopped',
    'lheel',
    'rheel',
    'ltoe',
    'rtoe',
)

repeat_scripts = (
    'segno',
    'coda',
    'varcoda',
    'fine',  # since 2.23
)

ancient_scripts = (
    'ictus',
    'accentus',
    'circulus',
    'semicirculus',
    'signumcongruentiae',
)

modes = (
    'major',
    'minor',
    'ionian',
    'dorian',
    'phrygian',
    'lydian',
    'mixolydian',
    'aeolian',
    'locrian',
)

markupcommands_nargs = (
    # no arguments
    (
        'doubleflat',
        'doublesharp',
        'draw-hline',  # since 2.14 or before
        'eyeglasses',
        'flat',
        'natural',
        'null',
        'semiflat',
        'semisharp',
        'sesquiflat',
        'sesquisharp',
        'sharp',
        'slashSeparator',  # since 2.20
        'strut',
        'table-of-contents'
    ),
    # one argument
    (
        'accidental',  # since 2.23
        'backslashed-digit',
        'bold',
        'box',
        'bracket',
        'caps',
        'center-align',
        'center-column',
        'char',
        'circle',
        'column',
        'compound-meter',  # since 2.20
        'concat',
        'dir-column',
        'draw-dashed-line',  # since 2.18
        'draw-dotted-line',  # since 2.18
        'draw-line',
        'dynamic',
        'ellipse',  # since 2.18
        'fill-line',
        'finger',
        'first-visible',  # since 2.20
        'fontCaps',
        'fret-diagram',
        'fret-diagram-terse',
        'fret-diagram-verbose',
        'fromproperty',
        'harp-pedal',
        'hbracket',
        'hspace',
        'huge',
        'italic',
        'justify',
        'justify-field',
        'justify-line',  # since 2.20
        'justify-string',
        'large',
        'larger',
        'left-align',
        'left-brace',
        'left-column',
        'line',
        'lookup',
        'markalphabet',
        'markletter',
        'medium',
        'musicglyph',
        'normalsize',
        'normal-size-sub',
        'normal-size-super',
        'normal-text',
        'number',
        'oval',  # since 2.18
        'overlay',  # since 2.20
        'overtie',  # since 2.20
        'polygon',  # since 2.23
        'postscript',
        'property-recursive',  # since 2.16
        'right-align',
        'right-brace',
        'right-column',
        'roman',
        'rounded-box',
        'sans',
        'score',
        'score-lines',  # since 2.20
        'simple',
        'slashed-digit',
        'small',
        'smallCaps',
        'smaller',
        'stdBass',  # since 2.18
        'stdBassIV',  # since 2.18
        'stdBassV',  # since 2.18
        'stdBassVI',  # since 2.18
        'stencil',
        'string-lines',  # since 2.23
        'sub',
        'super',
        'teeny',
        'text',
        'tie',  # since 2.20
        'tied-lyric',
        'tiny',
        'transparent',
        'triangle',
        'typewriter',
        'underline',
        'undertie',  # since 2.20
        'upright',
        'vcenter',
        'vspace',
        'verbatim-file',
        'whiteout',
        'with-true-dimensions',  # since 2.23
        'wordwrap',
        'wordwrap-field',
        'wordwrap-string',
    ),
    # two arguments
    (
        'abs-fontsize',
        'auto-footnote',  # since 2.16
        'combine',
        'customTabClef',
        'fontsize',
        'footnote',
        'fraction',
        'halign',
        'hcenter-in',
        'lower',
        'magnify',
        'map-commands', # since 2.23
        'markup-command',  # since 2.23
        'note',
        'on-the-fly',
        'override',
        'pad',  # since 2.23
        'pad-around',
        'pad-markup',
        'pad-x',
        'page-link',
        'path',  # added in LP 2.13.31
        'raise',
        'rotate',
        'scale',
        'table',  # since 2.20
        'translate',
        'translate-scaled',
        'with-color',
        'with-link',
        'with-outline',  # since 2.20
        'with-true-dimension',  # since 2.23
        'with-url',
        'woodwind-diagram',
        'with-dimensions-from',  # since 2.20
    ),
    # three arguments
    (
        'arrow-head',
        'beam',
        'draw-circle',
        'draw-squiggle-line',  # since 2.20
        'epsfile',
        'filled-box',
        'general-align',
        'note-by-number',
        'pad-to-box',
        'page-ref',
        'with-dimension',  # since 2.23
        'with-dimension-from',  # since 2.23
        'with-dimensions',
    ),
    # four arguments
    (
        'pattern',
        'put-adjacent',
    ),
    # five arguments,
    (
        'fill-with-pattern',
    ),
)

markupcommands = sum(markupcommands_nargs, ())

markuplistcommands = (
    'column-lines',
    'justified-lines',
    'override-lines',
    'wordwrap-internal',
    'wordwrap-lines',
    'wordwrap-string-internal',
)

contexts = (
    'ChoirStaff',
    'ChordNames',
    'CueVoice',
    'Devnull',
    'DrumStaff',
    'DrumVoice',
    'Dynamics',
    'FiguredBass',
    'FretBoards',
    'Global',
    'GrandStaff',
    'GregorianTranscriptionStaff',
    'GregorianTranscriptionVoice',
    'KievanStaff',  # since 2.16
    'KievanVoice',  # since 2.16
    'Lyrics',
    'MensuralStaff',
    'MensuralVoice',
    'NoteNames',
    'NullVoice',  # since 2.18
    'PetrucciStaff',  # since 2.16
    'PetrucciVoice',  # since 2.16
    'PianoStaff',
    'RhythmicStaff',
    'Score',
    'Staff',
    'StaffGroup',
    'TabStaff',
    'TabVoice',
    'Timing',
    'VaticanaStaff',
    'VaticanaVoice',
    'Voice',
)

midi_instruments = (
    # (1-8 piano)
    'acoustic grand',
    'bright acoustic',
    'electric grand',
    'honky-tonk',
    'electric piano 1',
    'electric piano 2',
    'harpsichord',
    'clav',
    # (9-16 chrom percussion)
    'celesta',
    'glockenspiel',
    'music box',
    'vibraphone',
    'marimba',
    'xylophone',
    'tubular bells',
    'dulcimer',
    # (17-24 organ)
    'drawbar organ',
    'percussive organ',
    'rock organ',
    'church organ',
    'reed organ',
    'accordion',
    'harmonica',
    'concertina',
    # (25-32 guitar)
    'acoustic guitar (nylon)',
    'acoustic guitar (steel)',
    'electric guitar (jazz)',
    'electric guitar (clean)',
    'electric guitar (muted)',
    'overdriven guitar',
    'distorted guitar',
    'guitar harmonics',
    # (33-40 bass)
    'acoustic bass',
    'electric bass (finger)',
    'electric bass (pick)',
    'fretless bass',
    'slap bass 1',
    'slap bass 2',
    'synth bass 1',
    'synth bass 2',
    # (41-48 strings)
    'violin',
    'viola',
    'cello',
    'contrabass',
    'tremolo strings',
    'pizzicato strings',
    'orchestral harp',  # till LilyPond 2.12 was this erroneously called: 'orchestral strings'
    'timpani',
    # (49-56 ensemble)
    'string ensemble 1',
    'string ensemble 2',
    'synthstrings 1',
    'synthstrings 2',
    'choir aahs',
    'voice oohs',
    'synth voice',
    'orchestra hit',
    # (57-64 brass)
    'trumpet',
    'trombone',
    'tuba',
    'muted trumpet',
    'french horn',
    'brass section',
    'synthbrass 1',
    'synthbrass 2',
    # (65-72 reed)
    'soprano sax',
    'alto sax',
    'tenor sax',
    'baritone sax',
    'oboe',
    'english horn',
    'bassoon',
    'clarinet',
    # (73-80 pipe)
    'piccolo',
    'flute',
    'recorder',
    'pan flute',
    'blown bottle',
    'shakuhachi',
    'whistle',
    'ocarina',
    # (81-88 synth lead)
    'lead 1 (square)',
    'lead 2 (sawtooth)',
    'lead 3 (calliope)',
    'lead 4 (chiff)',
    'lead 5 (charang)',
    'lead 6 (voice)',
    'lead 7 (fifths)',
    'lead 8 (bass+lead)',
    # (89-96 synth pad)
    'pad 1 (new age)',
    'pad 2 (warm)',
    'pad 3 (polysynth)',
    'pad 4 (choir)',
    'pad 5 (bowed)',
    'pad 6 (metallic)',
    'pad 7 (halo)',
    'pad 8 (sweep)',
    # (97-104 synth effects)
    'fx 1 (rain)',
    'fx 2 (soundtrack)',
    'fx 3 (crystal)',
    'fx 4 (atmosphere)',
    'fx 5 (brightness)',
    'fx 6 (goblins)',
    'fx 7 (echoes)',
    'fx 8 (sci-fi)',
    # (105-112 ethnic)
    'sitar',
    'banjo',
    'shamisen',
    'koto',
    'kalimba',
    'bagpipe',
    'fiddle',
    'shanai',
    # (113-120 percussive)
    'tinkle bell',
    'agogo',
    'steel drums',
    'woodblock',
    'taiko drum',
    'melodic tom',
    'synth drum',
    'reverse cymbal',
    # (121-128 sound effects)
    'guitar fret noise',
    'breath noise',
    'seashore',
    'bird tweet',
    'telephone ring',
    'helicopter',
    'applause',
    'gunshot',
    # (channel 10 drum-kits - subtract 32768 to get program no.)
    'standard kit',
    'standard drums',
    'drums',
    'room kit',
    'room drums',
    'power kit',
    'power drums',
    'rock drums',
    'electronic kit',
    'electronic drums',
    'tr-808 kit',
    'tr-808 drums',
    'jazz kit',
    'jazz drums',
    'brush kit',
    'brush drums',
    'orchestra kit',
    'orchestra drums',
    'classical drums',
    'sfx kit',
    'sfx drums',
    'mt-32 kit',
    'mt-32 drums',
    'cm-64 kit',
    'cm-64 drums',
)

# scheme_functions = (
#    'set-accidental-style',
#    'set-global-staff-size',
#    'set-octavation',
#    'set-paper-size',
#    'define-public',
#    'define-music-function',
#    'define-markup-command',
#    'empty-stencil',
#    'markup',
#    'number?',
#    'string?',
#    'pair?',
#    'ly:duration?',
#    'ly:grob?',
#    'ly:make-moment',
#    'ly:make-pitch',
#    'ly:music?',
#    'ly:moment?',
#    'ly:format',
#    'markup?',
#    'interpret-markup',
#    'make-line-markup',
#    'make-center-markup',
#    'make-column-markup',
#    'make-musicglyph-markup',
#    'color?',
#    'rgb-color',
#    'x11-color',
# )


scheme_values = (
    'UP',
    'DOWN',
    'LEFT',
    'RIGHT',
    'CENTER',
    'minimum-distance',
    'basic-distance',
    'padding',
    'stretchability',
)

headervariables = (
    'dedication',
    'title',
    'subtitle',
    'subsubtitle',
    'poet',
    'composer',
    'meter',
    'opus',
    'arranger',
    'instrument',
    'piece',
    'breakbefore',
    'copyright',
    'tagline',
    'mutopiatitle',
    'mutopiacomposer',
    'mutopiapoet',
    'mutopiaopus',
    'mutopiainstrument',
    'date',
    'enteredby',
    'source',
    'style',
    'maintainer',
    'maintainerEmail',
    'maintainerWeb',
    'moreInfo',
    'lastupdated',
    'texidoc',
    'footer',
)

papervariables = (
    # fixed vertical
    'paper-height',
    'top-margin',
    'bottom-margin',
    'ragged-bottom',
    'ragged-last-bottom',

    # horizontal
    'paper-width',
    'line-width',
    'left-margin',
    'right-margin',
    'check-consistency',
    'ragged-right',
    'ragged-last',
    'two-sided',
    'inner-margin',
    'outer-margin',
    'binding-offset',
    'horizontal-shift',
    'indent',
    'short-indent',

    # flex vertical
    'markup-system-spacing',  # the distance between a (title or top-level) markup and the system that follows it.
    'score-markup-spacing',
    # the distance between the last system of a score and the (title or top-level) markup that follows it.
    'score-system-spacing',
    # the distance between the last system of a score and the first system of the score that follows it, when no (title or top-level) markup exists between them.
    'system-system-spacing',  # the distance between two systems in the same score.
    'markup-markup-spacing',  # the distance between two (title or top-level) markups.
    'last-bottom-spacing',
    # the distance from the last system or top-level markup on a page to the bottom of the printable area (i.e. the top of the bottom margin).
    'top-system-spacing',
    # the distance from the top of the printable area (i.e. the bottom of the top margin) to the first system on a page, when there is no (title or top-level) markup between the two.
    'top-markup-spacing',
    # the distance from the top of the printable area (i.e. the bottom of the top margin) to the first (title or top-level) markup on a page, when there is no system between the two.

    # line breaking
    'max-systems-per-page',
    'min-systems-per-page',
    'system-count',
    'systems-per-page',

    # page breaking
    'blank-after-score-page-force',
    # The penalty for having a blank page after the end of one score and before the next. By default, this is smaller than blank-page-force, so that we prefer blank pages after scores to blank pages within a score.
    'blank-last-page-force',  # The penalty for ending the score on an odd-numbered page.
    'blank-page-force',
    # The penalty for having a blank page in the middle of a score. This is not used by ly:optimal-breaking since it will never consider blank pages in the middle of a score.
    'page-breaking',
    # The page-breaking algorithm to use. Choices are ly:minimal-breaking, ly:page-turn-breaking, and ly:optimal-breaking.
    'page-breaking-system-system-spacing',
    # Tricks the page breaker into thinking that system-system-spacing is set to something different than it really is. For example, if page-breaking-system-system-spacing #'padding is set to something substantially larger than system-system-spacing #'padding, then the page-breaker will put fewer systems on each page. Default: unset.
    'page-count',  # The number of pages to be used for a score, unset by default.

    # page numbering
    'auto-first-page-number',
    'first-page-number',
    'print-first-page-number',
    'print-page-number',
    'page-number-type',  # since 2.20

    # misc
    'page-spacing-weight',
    'print-all-headers',
    'system-separator-markup',
    'staff-space',  # since 2.20

    # debugging
    'annotate-spacing',

    # different markups
    'bookTitleMarkup',
    'evenFooterMarkup',
    'evenHeaderMarkup',
    'oddFooterMarkup',
    'oddHeaderMarkup',
    'scoreTitleMarkup',
    'tocItemMarkup',
    'tocTitleMarkup',

    # fonts
    'fonts',

    # undocumented?
    # 'blank-after-score-page-force',
    # 'force-assignment',
    # 'input-encoding',
    # 'output-scale',
)

layoutvariables = (
    'indent',
    'short-indent',
    'system-count',
    'line-width',
    'ragged-right',
    'ragged-last',
)

midivariables = (
)

repeat_types = (
    'unfold',
    'percent',
    'volta',
    'tremolo',
    'segno',  # since 2.23
)

accidentalstyles = (
    'default',
    'voice',
    'modern',
    'modern-cautionary',
    'modern-voice',
    'modern-voice-cautionary',
    'piano',
    'piano-cautionary',
    'choral',  # since 2.20
    'choral-cautionary',  # since 2.20
    'neo-modern',
    'neo-modern-cautionary',
    'neo-modern-voice',
    'neo-modern-voice-cautionary',
    'dodecaphonic',
    'teaching',
    'no-reset',
    'forget',
)

clefs_plain = (
    'alto',
    'baritone',
    'bass',
    'C',
    'F',
    'french',
    'G',
    'GG',  # since 2.19
    'mezzosoprano',
    'percussion',
    'soprano',
    'subbass',
    'tab',
    'tenor',
    'tenorG',  # since 2.19
    'treble',
    'varbaritone',
    'varC',  # since 2.19
    'varpercussion',  # since 2.19
    'violin',
)

clefs = clefs_plain + (
    'treble_8',
    'bass_8',
)

break_visibility = (
    'all-invisible',
    'begin-of-line-visible',
    'end-of-line-visible',
    'all-visible',
    'begin-of-line-invisible',
    'end-of-line-invisible',
    'center-invisible',
)

mark_formatters = (
    'format-mark-alphabet',
    'format-mark-barnumbers',
    'format-mark-letters',
    'format-mark-numbers',
    'format-mark-box-alphabet',
    'format-mark-box-barnumbers',
    'format-mark-box-letters',
    'format-mark-box-numbers',
    'format-mark-circle-alphabet',
    'format-mark-circle-barnumbers',
    'format-mark-circle-letters',
    'format-mark-circle-numbers',
)
