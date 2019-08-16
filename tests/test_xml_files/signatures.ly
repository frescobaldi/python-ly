\version "2.18.2"

\language "english"

Soprano = \relative c'' {
  \defaultTimeSignature
  \time 4/4 \key a \major \numericTimeSignature a1
  \defaultTimeSignature \key ef \minor a1
  \time 2/2 \key gs \dorian a1 \numericTimeSignature
  \time 4/4 a1
  \time 2/2 \defaultTimeSignature a1
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
