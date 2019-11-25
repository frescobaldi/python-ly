\version "2.18.2"

\language "english"

keyTime = {
    \time 4/4
}

Soprano = \relative c'' {
  \voiceOne
  \keyTime
    g4 g \break \bar "" g g
  | g g g g \break \bar "||"
  | g g g g
  | g g g g
  \bar "|."
}

Alto = \relative c' {
  \voiceTwo
  \keyTime
    e4 e e e
  | e e e e
  | e e e e \bar "||" \break
  | e e e e
}

Tenor = \relative c {
  \voiceOne
  \keyTime
    c4 c c c
  | c c \bar "" \break c c
  | c c c c
  | c c c c
}

Bass = \relative c {
  \voiceTwo
  \keyTime
    a4 a a a \break
  | a a a a
  | a a a a
  | a a a a
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
