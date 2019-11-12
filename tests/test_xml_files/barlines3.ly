\version "2.18.2"

\language "english"

keyTime = {
    \time 4/4
}

Soprano = \relative c'' {
  \voiceOne
  \keyTime
    c1
    c2 \bar "||" c
    c4 c \bar "||" c c
}

Alto = \relative c'' {
  \voiceTwo
  \keyTime
    a2 \bar "||" a
    a1
    a4 a a a \bar "|."
}

Tenor = \relative c {
  \voiceOne
  \keyTime
  \clef "bass"
    a2 a
    a a
    a a
}

\score
{
  <<
    \new Staff = "treble" \with {}
    <<
      \clef "treble"
      \new Voice = "SopranoVoice" \Soprano
      \new Voice = "AltoVoice" \Alto
    >>
    \new Staff \Tenor
  >>
}
