\version "2.18.2"

\language "english"

keyTime = {
    \time 4/4
}

Soprano = \relative c'' {
  \voiceOne
  \keyTime
  c4 c \breathe c c \breathe
  c c c c
}

Alto = \relative c'' {
  \voiceTwo
  \keyTime
  a1 
  a2 \breathe a
}

Tenor = \relative c {
  \keyTime
  \clef "bass"
  a4 \breathe a <a c> \breathe a
  a1 \breathe \bar "|."
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