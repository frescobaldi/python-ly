"""A corpus of LilyPond snippets that must convert to valid MusicXML."""
import pytest


CORPUS = {
    'melody_relative': r"""\relative c'' { \clef treble \key g \major \time 3/4 g4 a b | c2 b4 | a2. \bar "|." }""",
    'piano_staff': r"""\score { \new PianoStaff << \new Staff = "up" \relative c'' { \clef treble c4 d e f | g1 } \new Staff = "down" { \clef bass c2 g, | c1 } >> }""",
    'choir_staff': r"""\score { \new ChoirStaff << \new Staff { \set Staff.instrumentName = "S" c''1 } \new Staff { \set Staff.instrumentName = "A" a'1 } >> }""",
    'staff_group': r"""\score { \new StaffGroup << \new Staff { c''1 } \new Staff { \clef bass c1 } >> }""",
    'header': r"""\header { title = "Title" composer = "Composer" copyright = "CC" } \score { { c'1 } }""",
    'header_markup': r"""\header { title = \markup { \bold "Title" } } { c'1 }""",
    'tuplets': r"""{ \tuplet 3/2 { c'8 d' e' } \times 2/3 { f'4 g' a' } \tuplet 3/2 4 { b'8 c'' d'' e'' f'' g'' } }""",
    'tuplet_span': r"""{ \tupletSpan 4 \tuplet 3/2 { c'8 d' e' f' g' a' } c''2 }""",
    'grace_types': r"""{ \grace c'16 d'4 \acciaccatura e'8 f'4 \appoggiatura g'8 a'4 \slashedGrace b'8 c''4 }""",
    'grace_chord': r"""{ \grace <c' e'>16 d'4 e' f' g' }""",
    'ties_slurs': r"""{ c'4~ c' d'( e') | f'\( g' a' b'\) | c''1 }""",
    'articulations': r"""{ c'4-. d'-- e'-> f'-^ | g'-_ a'-! b'\staccatissimo c''\fermata }""",
    'ornaments': r"""{ c''4\trill d''\turn e''\mordent f''\prall }""",
    'dynamics': r"""{ c'4\pp d'\< e' f'\! | g'\ff\> a' b' c''\p | c''1\sfz }""",
    'dynamics_text': r"""{ c'4\cresc d' e' f'\! | g'1 }""",
    'fingering': r"""{ c'4-1 d'-2 e'-3 f'-4 }""",
    'chord_repetition': r"""{ <c' e' g'>4 q q q | <d' f'>2 q }""",
    'isolated_durations': r"""{ c'4 4 8 8 4 }""",
    'drums': r"""\new DrumStaff \drummode { bd4 sn bd sn | hh8 hh hh hh hh hh hh hh }""",
    'multi_rest': r"""{ \compressMMRests R1*3 | c'1 }""",
    'skips': r"""{ s2 c'2 | s1 | d'1 }""",
    'clefs': r"""{ \clef treble c'4 \clef alto c' \clef tenor c' \clef bass c | \clef "treble_8" c1 }""",
    'keys_modes': r"""{ \key d \major d'1 | \key f \minor f'1 | \key e \dorian e'1 }""",
    'time_changes': r"""{ \time 2/4 c'2 | \time 6/8 c'4. c'4. | \time 3/2 c'1. }""",
    'numeric_time': r"""{ \numericTimeSignature \time 4/4 c'1 \time 2/2 c'1 }""",
    'partial_start': r"""{ \partial 8 g'8 | c''4 d'' e'' f'' | g''1 }""",
    'tempo': r"""{ \tempo "Allegro" 4 = 120 c'1 | \tempo 2 = 60 c'1 }""",
    'tempo_text': r"""{ \tempo "Andante" c'1 }""",
    'marks': r"""{ \mark \default c'1 | \mark \default c'1 | \mark #5 c'1 }""",
    'ottava': r"""{ \ottava #1 c'''4 d''' e''' f''' | \ottava #0 c''1 }""",
    'tremolo': r"""{ c'4:16 d'2:32 e'4 | \repeat tremolo 4 { c'16 e' } c'2 }""",
    'glissando': r"""{ c'2\glissando g'2 }""",
    'breaks': r"""{ c'1 \break d'1 \pageBreak e'1 }""",
    'breathe': r"""{ c'2 \breathe d'2 }""",
    'text_scripts': r"""{ c'4^"dolce" d'_"espr." e'^\markup { \italic rit. } f' }""",
    'voices_separator': r"""\new Staff { << { c''4 d'' e'' f'' } \\ { a'2 g' } >> }""",
    'explicit_voices': r"""\new Staff << \new Voice { \voiceOne c''1 } \new Voice { \voiceTwo a'1 } >>""",
    'voice_names_lyrics': r"""\score { << \new Staff \new Voice = "mel" { c'4 d' e' f' } \new Lyrics \lyricsto "mel" { one two three four } >> }""",
    'variables': r"""melody = \relative c' { c4 d e f } bass = { c1 } \score { << \new Staff \melody \new Staff { \clef bass \bass } >> }""",
    'overrides': r"""{ \override NoteHead.color = #red c'4 \revert NoteHead.color d' \once \override Stem.transparent = ##t e' \tweak color #blue f' }""",
    'set_unset': r"""{ \set Staff.instrumentName = "Vln" \unset Staff.instrumentName c'1 }""",
    'stems': r"""{ \stemUp c'4 d' \stemDown e' f' \stemNeutral g'1 }""",
    'accidentals': r"""{ cis'4 des' eisis' feses' | c'! c'? c'2 }""",
    'long_notes': r"""{ c'\breve c'1 }""",
    'dotted': r"""{ c'4. d'8 e'8. f'16 g'4 | a'2.. b'8 }""",
    'bar_types': r"""{ c'1 \bar "||" c'1 \bar ".|:" c'1 \bar ":|." c'1 \bar "|." }""",
    'figured_bass': r"""\score { << \new Staff { c'1 } \new FiguredBass \figuremode { <6 4>1 } >> }""",
    'layout_midi': r"""\score { { c'1 } \layout { } \midi { } }""",
    'book': r"""\book { \score { { c'1 } } }""",
    'with_block': r"""\new Staff \with { instrumentName = "Flute" shortInstrumentName = "Fl." } { c''1 }""",
    'transposed_instrument': r"""\new Staff { \transposition bes c''1 }""",
    'empty_chord': r"""{ <>\p c'4 d' e' f' }""",
    'header_full': r"""\header { title = "T" subtitle = "S" composer = "C" arranger = "A" poet = "P" lyricist = "L" opus = "Op. 1" dedication = "D" piece = "Piece" instrument = "Flute" meter = "Allegro" copyright = "CC" tagline = "tag" } { c'1 }""",
    'score_header': r"""\score { { c'1 } \header { piece = "Nr. 1" } }""",
    'book_header': r"""\book { \header { title = "B" composer = "C" } \score { { c'1 } } }""",
    'drums_voices': r"""\new DrumStaff << \drummode { \voiceOne hh8 hh hh hh hh hh hh hh } \\ \drummode { \voiceTwo bd4 sn bd sn } >>""",
    'drums_rhythms': r"""\new DrumStaff \drummode { bd4. sn8 \tuplet 3/2 { bd8 sn sn } r4 | cymc2~ cymc2 }""",
    'drums_chords': r"""\new DrumStaff \drummode { <bd hh>4 <sn hh>8 <sn hh> <bd hh>2 }""",
    'drums_grace_artic': r"""\drums { \grace sn16 bd4-> sn-. sn\p sn }""",
    'voices_in_staff_group': r"""\score { \new StaffGroup << \new Voice = "S" { \set Staff.instrumentName = #"Cantus" c''2 d'' } \addlyrics { Du tout } \new Voice = "B" { \set Staff.instrumentName = #"Bassus" c2 g, } \addlyrics { plon giet } >> }""",
}

# known bugs outside the planned improvements
KNOWN_INVALID = {
}


def corpus_params():
    """Return the corpus names as pytest parameters, known bugs marked xfail."""
    return [pytest.param(name, marks=pytest.mark.xfail(strict=True, reason=KNOWN_INVALID[name]))
            if name in KNOWN_INVALID else name
            for name in sorted(CORPUS)]
