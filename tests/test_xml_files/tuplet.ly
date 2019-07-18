\version "2.18.2"

StanzaOne = \lyricmode {
  La di la di la
  la di la di la di la di la di
  la di la di la di la.
}

\language "english"

keyTime = {
    \time 4/4
    \numericTimeSignature
    \key c \major
}

Soprano = \relative c'' {
  \voiceOne
  \keyTime
    \tuplet 3/2 { bf4 bs a } a4 a
    \tuplet 5/4 { a8 a a a a } \tuplet 5/2 { a4 a a a a }
    \tuplet 7/4 { a4 a a a a a a }
}

Alto = \relative c' {
  \voiceTwo
  \keyTime
    e1
    e1
    e1
}

\score
{
  <<
    \new Staff = "treble"
      <<
        \clef "treble"
        \new Voice = "SopranoVoice" \Soprano
        \new Voice = "AltoVoice" \Alto
        \lyricsto SopranoVoice \new Lyrics \StanzaOne
      >>
  >>
}
