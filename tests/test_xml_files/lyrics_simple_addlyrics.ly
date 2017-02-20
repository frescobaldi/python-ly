\version "2.19.55"

\header {
  title = "lyrics simple addlyrics"
}

verseOne = \lyricmode {
 \set stanza = "v1"
 My long sing song for voice one
}
verseTwo = \lyricmode {
 \set stanza = "v2"
 This is verse two, the last verse
}

\score {
  \new Staff {
    \relative c' {
      \clef treble
      c'32 c c16 c8 c4 c2 |
      c1 |
    }
  }
  \addlyrics \verseOne
  \addlyrics \verseTwo
  \layout { }
}