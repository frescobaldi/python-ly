\version "2.18.2"

\language "english"

keyTime = {
    \time 4/4
}

Soprano = \relative c'' {
  \voiceOne
  \keyTime
    c4 \grace {g8 a} c4 \acciaccatura g8 c4 \bar "" \slashedGrace g8 c4 \bar "||"
    c4 \acciaccatura {g8 a} c4 \appoggiatura g8 c4 c \bar "|."
}

Alto = \relative c'' {
  \voiceTwo
  \keyTime
    a4 a a a
    a a a a
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