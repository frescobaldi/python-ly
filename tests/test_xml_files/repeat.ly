\version "2.19.55"

\header {
  title = "repeat"
}

\score {
  \new ChoirStaff <<
    \new Staff {
      \relative c' {
        c1 |
        \repeat volta 2{ c1| }
        d1 |
        \repeat volta 3{ d1| }
      }
    }

    \new Staff
    <<
      \clef treble
      \new Voice {
        \voiceOne
        \relative c' {
          c1 |
          \repeat volta 2{ d1| }
          e1 |
          \repeat volta 3{ d1| }
        }
      }
      \new Voice  {
        \voiceTwo
        \relative c' {
          f4 f f f |
          \repeat volta 2{ g g g g| }
          a a a a |
          \repeat volta 3{ g2 g| }
        }
      }
    >>
  >>

  \layout {}
}
