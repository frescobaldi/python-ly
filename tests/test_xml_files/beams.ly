\version "2.18.2"

keyTime = {
    \time 4/4
}

Soprano = \relative c'' {
  \voiceOne
  \keyTime
  g16[ g8. g8] g g[ g] g4
}

\score
{
  <<
		\new Staff = "treble" \with {
	}
    <<
		\clef "treble"
		\new Voice = "SopranoVoice" \Soprano
	>>
  >>  
}