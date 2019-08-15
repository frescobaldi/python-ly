\version "2.18.2"

\language "english"

keyTime = {
    \time 5/4
    \partial 4
}

Soprano = \relative c'' {
  \voiceOne
  \keyTime
    c8 \bar "||" c8
    c4 c c \bar "||" c c
    c1 c4
    c1 c4
    c1 c4 \bar "|."
}

Alto = \relative c'' {
  \voiceTwo
  \keyTime
    s1*7/4
    a2. a4
    s1*5/4
    a4 s2 a2
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