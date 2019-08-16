\version "2.18.2"

\language "english"

Soprano = \relative c'' {
  \time 4/4 \key c \major
  <a c>2 q
  <as cf e>2 q4 q
  \tuplet 3/2 { q4 <a! c?> q } q2
  <a c>8 q q q q q q q
  q8. q q16 q( q q[ q q]) q q q q
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
