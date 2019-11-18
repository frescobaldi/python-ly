\version "2.18.2"

\language "english"

keyTime = {
    \time 4/4
}

Stanza = \lyricmode {
  La di la da!
}

Melody = \relative c'' {
  \voiceOne
  \keyTime
    g2 g
    g g
}

Right = \relative c'' {
  \keyTime
    <b g>2 q
    q q
}

Left = \relative c {
  \keyTime
  \clef bass
    <a c>2 q
    q q
  \bar "|."
}

\score
{
  <<
      \new Staff
      <<
        \new Voice = "M" \Melody
        \lyricsto M \new Lyrics \Stanza
      >>
      \new PianoStaff
      <<
        \new Staff = "Right" \Right
        \new Staff = "Left" \Left
      >>
  >>
}