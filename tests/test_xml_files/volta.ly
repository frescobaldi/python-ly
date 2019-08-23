\version "2.18.2"

\language "english"

Soprano = \relative c'' {
  \time 4/4 \key c \major
  \voiceOne
  \repeat volta 15 { a1 a2}
  \alternative {
    {\tuplet 3/2 {a4 a a}}
    {b1}
    {\time 8/8 \key f \major c2 c}
    {d2}
    {e2}
    {f1 \bar "||"}
    {g2}
  }
  a,2 \bar ""
  \repeat volta 3 {a1 \bar ""}
  a1
  \repeat volta 3 {a1}
  \repeat volta 2 {a1}
  \alternative {{b1}} \bar ".|" c1
}

Alto = \relative c'' {
  \time 4/4 \key c \major
  \voiceTwo
  \repeat volta 15 { c1 c2}
  \alternative {
    {\tuplet 3/2 {c4 c c}}
    {d1}
    {\time 8/8 \key f \major e2 e}
    {f2}
    {g2}
    {a1 \bar "||"}
    {b2}
  }
  c,2 \bar ""
  \repeat volta 3 {c1 \bar ""}
  c1
  \repeat volta 3 {c1}
  \repeat volta 2 {c1}
  \alternative {{d1}} \bar ".|" e1
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
