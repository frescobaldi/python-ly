\version "2.18.2"

Stanza = \lyricmode {
  Font style
  \override LyricText #'font-shape = #'italic
  is su -- per cool
  \revert LyricText #'font-shape
  but not here
}

\language "english"

keyTime = {
    \time 4/4
    \key c \major
}

Soprano = \relative c'' {
  \keyTime
    c4 c c c
    c c c c
    c1 \bar "|."
}

\score
{
  <<
      \new Staff = "treble" \with {}
    <<
      \clef "treble"
      \new Voice = "SopranoVoice" \Soprano
      \lyricsto SopranoVoice \new Lyrics \Stanza
    >>
  >>
}