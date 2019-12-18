\version "2.18.2"

\language "english"

keyTime = {
    \time 4/4
}

Stanza = \lyricmode {
  La di la.
}

Soprano = \relative c'' {
  \keyTime
    <e c a>4~ <e~ c a> <e c~ a> <e c a~>
    q~ q a, a \bar "|."
}

\score
{
  <<
    \new Staff = "treble" \with {}
    <<
      \clef "treble"
      \new Voice = "Soprano" \Soprano
      \lyricsto Soprano \new Lyrics \Stanza
    >>
  >>
}