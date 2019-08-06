\version "2.18.2"

\language "english"

keyTime = {
    \time 5/4
    \numericTimeSignature
    \partial 4
    \key f \minor
}

Soprano = \transpose f gs { \relative c'' {
    \voiceOne
    \keyTime
    e4
    e ef es e
    \bar "|."
  }
}

Alto = \transpose f gs { \relative c' {
    \voiceTwo
    \keyTime
    d4
    d d d d
  }
}

Tenor = \transpose f gs { \relative c {
    \voiceOne
    \keyTime
    c4
    c c c c
  }
}

Bass = \transpose f gs { \relative c {
    \voiceTwo
    \keyTime
    a4
    a a a a 
  }
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
    \new Staff = "bass" \with {}
    <<
      \clef "bass"
      \new Voice = "TenorVoice" \Tenor
      \new Voice = "BassVoice" \Bass
    >>
  >>
}
