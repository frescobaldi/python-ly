\version "2.18.2"

keyTime = {
    \time 4/4
    \numericTimeSignature
    \partial 4
}

Soprano = \relative c'' {
  \voiceOne
  \keyTime
    g4
  | g g g g
}

Alto = \relative c' {
  \voiceTwo
  \keyTime
    g4
  | g g g g
}

Tenor = \relative c' {
  \voiceOne
  \keyTime
    g4
  | g g g g
}

Bass = \relative c {
  \voiceTwo
  \keyTime
    g4
  | g g g g
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
	>>

		\new Staff = "bass" \with {
	}
    <<
		\clef "bass"
		\new Voice = "TenorVoice" \Tenor
		\new Voice = "BassVoice" \Bass
	>>

  >>
  
}