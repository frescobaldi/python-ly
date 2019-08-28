\version "2.18.2"

\language "english"

Soprano = \relative c'' {
  \time 4/4 \key c \major
  c2.:8 c4:16 c1:32 c:
  \repeat tremolo 6 c8
  \repeat tremolo 4 c16
  \repeat tremolo 32 c32
  \repeat tremolo 2 { c16 d8 c16} a2
  \repeat tremolo 6 { c16 d }
  \repeat tremolo 2 { c16 d }
  \repeat tremolo 4 { c16 d8 c16}
}

\score
{
  <<
      \new Staff = "treble" \with {}
    <<
      \clef "treble"
      \new Voice = "SopranoVoice" \Soprano
    >>
  >>
}
