\version "2.18.2"

\language "english"

Soprano = \relative c'' {
  \time 4/4 \key c \major
  \voiceOne
  \repeat unfold 5 {a2}
  \alternative {{b2 b1 \bar ""} {b2 c1} {d2 d1}} \bar "|."
}

Alto = \relative c'' {
  \time 4/4 \key c \major
  \voiceTwo
  \repeat unfold 5 {cs2}
  \alternative {{cs2 d1} {e2 e1} {f2 f1}}
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
