\version "2.18.2"

switchSop = { \set associatedVoice = "SopranoVoice" }
switchOne = { \set associatedVoice = "1" }
switchThree = { \set associatedVoice = "3" }

StanzaOne = \lyricmode {
  La di la di
  \set associatedVoice = "AltoVoice" la di la di
  la \switchSop di la \switchOne di
  \switchThree laaa da da da \switchSop da.
  Err
}

\language "english"

keyTime = {
    \time 4/4
    \key c \major
}

Soprano = \relative c'' {
  \voiceOne
  \keyTime
    g4 g g g
    g1
    g2 g4 g
    << {b1 b b} \\ \\ {g2 g g g4 g g1} >>
}

Alto = \relative c' {
  \voiceTwo
  \keyTime
    e1
    e4 e e e
    e e2.
    e4 e e2
    e1 e
}

\score
{
  <<
		\new Staff = "treble" \with {
	}
    <<
		\clef "treble"
		\new Voice = "SopranoVoice" \Soprano
		\new Voice = "AltoVoice" \Alto
		\lyricsto SopranoVoice \new Lyrics \StanzaOne
	>>

  >>
  
}