\version "2.18.2"

keyTime = {
    \time 4/4
    \partial 4
}

Soprano = \relative c'' {
  \voiceOne
  \keyTime
    g4
  | g2. \bar "|."
}

Alto = \relative c' {
  \voiceTwo
  \keyTime
    g4
  | g2.
}

Tenor = \relative c' {
  \voiceOne
  \keyTime
    g4
  | g2.
}

Bass = \relative c {
  \voiceTwo
  \keyTime
    g4
  | g2.
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