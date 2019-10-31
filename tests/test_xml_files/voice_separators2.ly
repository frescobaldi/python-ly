\version "2.18.2"

\language "english"

keyTime = {
    \time 4/4
}

Soprano = \relative c'' {
  \voiceOne
  \keyTime
    d4 d << \\ {\voiceThree d2} \\ \\ {a4 a} >>
    d d d d \bar "|."
}

Alto = \relative c'' {
  \voiceTwo
  \keyTime
    a4 a s2
    a4 a a a \bar "|."
}

switchTwo = {
 \set associatedVoice = "2"
}
switchFour = {
 \set associatedVoice = "4"
}
switchSop = { 
 \set associatedVoice = "SopranoVoice"
}

StanzaOne = \lyricmode {
  La \switchTwo di \switchSop laaa
  la di la di!
}

StanzaTwo = \lyricmode {
  Ba \switchFour dum ba \switchSop dum ba dum ba dum!
}

\score
{
  <<
    \new Staff = "treble" \with {}
    <<
      \clef "treble"
      \new Voice = "SopranoVoice" \Soprano
      \new Voice = "AltoVoice" \Alto
      \lyricsto SopranoVoice \new Lyrics \StanzaOne
      \lyricsto SopranoVoice \new Lyrics \StanzaTwo
    >>
  >>
}