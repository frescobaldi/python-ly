\version "2.18.2"

StanzaOne = \lyricmode {  
  La di la~ah di~aa~ah
}

\language "english"

Soprano = \relative c'' {
  \voiceOne
    g2 g
  | g2 g
}

\score
{
  <<
		\new Staff = "treble" \with {
	}
    <<
		\clef "treble"
		\new Voice = "SopranoVoice" \Soprano
		\lyricsto SopranoVoice \new Lyrics \StanzaOne
	>>
  >>
  
}