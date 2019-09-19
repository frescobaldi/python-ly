\version "2.18.2"

\language "english"

\header {
  title = "Headers Test"
  composer = "John Doe"
}

\header {
  poet = "Jane Doe"
}

Soprano = \relative c'' {
  \voiceOne
  \time 4/4 \key c \major
  c1 \bar "|."
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