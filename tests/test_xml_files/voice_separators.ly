\version "2.18.2"

\language "english"

keyTime = {
    \time 5/4
    \partial 4
}

Soprano = \relative c'' {
  \voiceOne
  \keyTime
    << { c4 } \\ { a4 } >>
    r4 r g g g
    << { c1 <c a>4 c1 \bar "||" <c a>4 } \\ { g1 <g e>4 g1 g8( g) } >>
    \bar "|."
}

Alto = \relative c' {
  \voiceTwo
  \keyTime
    s4
    s1*5/2
}

Tenor = \relative c {
  \voiceOne
  \keyTime
    c4
    c c c c c
    c c c c c
    c c c c c
}

Bass = \relative c {
  \voiceTwo
  \keyTime
    a4
    a a a a a
    a a a a a
    a a a a a
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
