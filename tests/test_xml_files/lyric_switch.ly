\version "2.18.2"

switchSop = { \set associatedVoice = "SopranoVoice" }
switchAlto = { \set associatedVoice = "AltoVoice" }

StanzaOne = \lyricmode {
  \set stanza = "1." 
  La di la di
  \switchAlto la di la di
  la \switchSop di la di
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
    g4 g g g
    g1
    g2 g4 g
}

Alto = \relative c' {
  \voiceTwo
  \keyTime
    e1
    e4 e e e
    e e2.
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