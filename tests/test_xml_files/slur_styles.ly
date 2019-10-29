\version "2.18.2"

\language "english"

keyTime = {
    \time 4/4
}

Soprano = \relative c'' {
  \keyTime
  \voiceOne
  c4~ c \tieDashed c~ c
  \tieDotted c~ c << {d~ d} \\ {\tieDashed c~ c} >>
  s2 c4~ c
}

Alto = \relative c'' {
  \keyTime
  \voiceTwo
  g4( a) \slurDashed g( a)
  \slurDotted g( a) s2
  << {a4( b)} \\ {\slurDashed f( g)} >>
}

Tenor = \relative c {
  \keyTime
  \voiceOne
  f4\( g\) \phrasingSlurDashed f\( g\)
  \phrasingSlurDotted f4\( g\) \phrasingSlurSolid f\( g\)
  f4\( g\) f\( g\)
}

Bass = \relative c {
  \keyTime
  \voiceTwo
  c4\( d\) c\( d\)
  c4\( d\) c\( d\)
  c4\( d\) c\( d\) \bar "|."
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