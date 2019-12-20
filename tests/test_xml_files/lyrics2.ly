\version "2.18.2"

StanzaOne = \lyricmode {
  La "di lo li" da doo loo
  "ta da" this \markup \tiny {\musicglyph #"rests.2"} is rest
}

\language "english"

keyTime = {
    \time 4/4
    \key c \major
}

Soprano = \relative c' {
  \keyTime
    b4 c( d e)
  | g( a) b( c) 
  | g2 a
  | f4 a c b
}

\score
{
  <<
      \new Staff = "treble" \with {}
    <<
      \clef "treble"
      \new Voice = "SopranoVoice" \Soprano
      \lyricsto SopranoVoice \new Lyrics \StanzaOne
    >>
  >>
  
}