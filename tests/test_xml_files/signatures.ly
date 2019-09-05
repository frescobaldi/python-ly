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

Alto = \relative c'' {
  \defaultTimeSignature \key a \major
  c1 \key ef \minor
  c1 \key gs \dorian
  c1
  \time 4/4 c1
  c1
}

\score
{
  <<
      \new Staff = "treble" \with {}
    <<
      \clef "treble"
      \new Voice = "SopranoVoice1" \Soprano
    >>
      \new Staff = "treble2" \with {}
    <<
      \clef "treble"
      \new Voice = "SopranoVoice2" \Soprano
      \new Voice = "AltoVoice1" \Alto
    >>
      \new Staff = "treble3" \with {}
    <<
      \clef "treble"
      \new Voice = "AltoVoice2" \Alto
    >>
  >>
}
