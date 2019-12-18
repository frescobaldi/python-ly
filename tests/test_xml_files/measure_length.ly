\version "2.18.2"

\language "english"

keyTime = {
    \time 4/4
}

Soprano = \relative c'' {
  \voiceOne
  \keyTime
    c2 c
    c c c
    c c c
    \set Timing.measureLength = #(ly:make-moment 2 4)
    c
    \set Timing.measureLength = #(ly:make-moment 3 8)
    c4.
    c
    \set Timing.measureLength = #(ly:make-moment 2 4)
    a8 a a a
    \time 2/4
    a a a a
    \bar "|."
}

Alto = \relative c'' {
  \voiceTwo
  \keyTime
    a2 a
    a a a
    a a a
    a
    a4.
    a
    s2
    s
}

Tenor = \relative c {
  \voiceOne
  \keyTime
    e2 e
    e e e
    e e e
    e
    e4.
    e
    c8 c c c
    c c c c
}

Bass = \relative c {
  \voiceTwo
  \keyTime
    g2 g
    \set Timing.measureLength = #(ly:make-moment 6 4)
    g g g
    g g g
    g
    \set Timing.measureLength = #(ly:make-moment 3 8)
    g4.
    g
    s2
    s
}

\score
{
  <<
    \new Staff = "treble" \with {}
    <<
      \clef "treble"
      \new Voice = "Soprano" \Soprano
      \new Voice = "Alto" \Alto
    >>
    \new Staff = "bass" \with {}
    <<
      \clef "bass"
      \new Voice = "Tenor" \Tenor
      \new Voice = "Bass" \Bass
    >>
  >>
}