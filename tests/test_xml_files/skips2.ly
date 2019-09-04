\version "2.18.2"

\language "english"

keyTime = {
    \time 5/4
    \partial 4
}

Soprano = \relative c'' {
  \voiceOne
  \keyTime
    c8 c
    c1 \bar "||" c4
    c1 c4
    c1 \bar "||" c4
    c1 c4
}

Alto = \relative c'' {
  \voiceTwo
  \keyTime
    a8 s8*12
    a8 s4*10
    a2. a4
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
  >>
}
