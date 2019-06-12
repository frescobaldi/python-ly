\version "2.18.2"

\language "english"

keyTime = {
    \time 4/4
    \numericTimeSignature
}

Soprano = \relative {
  \voiceOne
  \keyTime
    g4 g \bar "'" g g \bar "||"
  | g g \bar "" g g \bar "!"
  | g g \bar "|" g g \bar "."
  | g g \bar ".|" g g \bar ".."
  | g g \bar ";" g g
  \bar "|."
}

Alto = \relative {
  \voiceTwo
  \keyTime
    e4 e e e
  | e e e e
  | e e e e
  | e e e e
  | e e e e
}

Tenor = \relative {
  \voiceOne
  \keyTime
    c4 c c c
  | c c c c
  | c c c c
  | c c c c
  | c c c c
}

Bass = \relative {
  \voiceTwo
  \keyTime
    a4 a a a
  | a a a a
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