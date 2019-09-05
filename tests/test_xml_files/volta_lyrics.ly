\version "2.18.2"

Stanza = \lyricmode {
  \repeat volta 2 { Hi, you }
  \alternative {{ are } { my best friend Joe! }}
}

Soprano = \relative c'' {
  \time 4/4
  \repeat volta 2 {g2 g}
  \alternative {{g1} {g4 g g g}} \bar "|."
}

\score
{
  <<
      \new Staff = "treble"
      <<
        \clef "treble"
        \new Voice = "SopranoVoice" \Soprano
        \lyricsto SopranoVoice \new Lyrics \Stanza
      >>
  >>
}