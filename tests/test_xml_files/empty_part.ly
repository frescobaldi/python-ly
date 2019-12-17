\version "2.18.2"

\language "english"

Stanza = \lyricmode {
  La di la
  di la di
  la di la.
}

keyTime = {
    \time 4/4
}

Soprano = \relative c'' {
  \keyTime
    c4 c c2
    c c4 c
    c c c2 \bar "|."
}

Alto = \relative c'' { }

\score
{
  <<
    \new Staff = "treble" \with {}
    <<
      \clef "treble"
      \new Voice = "SopranoVoice" \Soprano
      \new Voice = "AltoVoice" \Alto
      \lyricsto SopranoVoice \new Lyrics \Stanza
    >>
  >>
}
