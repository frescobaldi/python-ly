\version "2.18.2"

\language "english"

keyTime = {
    \time 4/4
}

Soprano = \relative c'' {
  \voiceOne
  \keyTime
    gf4 gf \bar "||" gf g
  | gss gss g gf~
  | gf~ gf gf gf
  | \key a \major gs gss g gf
  | \key c \minor af aff a as
  | af?2 af!
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
