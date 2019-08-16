\version "2.18.2"

\language "english"

keyTime = {
    \time 4/4
}

Soprano = \relative c'' {
  \voiceOne
  \keyTime
    r4 r <g e> g
  | g g g g
  \bar "|."
}

Alto = \relative c' {
  \voiceTwo
  \keyTime
    r1
  | e4 e e e
}

\score
{
  <<
      \new PianoStaff
      <<
        \new Staff = "SopranoVoice" \Soprano
        \new Staff = "AltoVoice" \Alto
      >>
  >>
}