\version "2.18.2"

\language "english"

keyTime = {
    \time 4/4
}

Soprano = \relative c'' {
  \voiceOne
  \keyTime
    c4 c c c
    c c c c
    c c c c c
    c c c c
    c c c c
    c c c c
    c c c
    c c c
}

Alto = \relative c'' {
  \voiceTwo
  \keyTime
    a4 s <a b> q
    a a a \bar "|." a
    \time 5/4 a8 a a a a a a a a a \bar ""
    \time 4/4 a a a a a a a a \bar "|."
    a1
    a1
    a2.
    a2.
}

Tenor = \relative c {
  \voiceOne
  \keyTime
  \clef "bass"
    a4 a \bar "||" a a
    a a a a
    a8 a a a a a a a a a
    \time 8/8 a a a a a a a a \bar "||"
    \time 4/4 \times 1/2 {a2 a} \tuplet 2/1 {a2 a} \bar "||"
    << {c1 \time 3/4 c2. c2. \bar "|."} \\ {a1 \bar "" a2. a2.} >>
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
