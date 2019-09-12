\version "2.18.2"

Soprano = \relative c'' {
  \voiceOne
  \time 4/4
    g1 \bar "|."
}

Alto = \relative c' {
  \voiceTwo
  \time 4/4
    e1
}

\score
{
  <<
      \new PianoStaff
      <<
        \new Voice \Soprano
        \new Voice \Alto
      >>
  >>
}