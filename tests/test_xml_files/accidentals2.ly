\version "2.18.2"

\language "english"

keyTime = {
    \time 4/4
    \key f \major
}

Soprano = \relative c'' {
  \keyTime
  \voiceOne
  b4 b b' e,
  e4 ef ef b
  \times 4/3 {af4 af' af}
}

Alto = \relative c'' {
  \keyTime
  \voiceTwo
  e4 ef ef b
  b4 b b e
  c4 c c c
}

Tenor = \relative c {
  \keyTime
  \voiceOne
  b4 b b e
  e4 ef ef b
  \times 4/3 {af4 af' af}
}

Bass = \relative c {
  \keyTime
  \voiceTwo
  e4 ef ef b
  b4 <b g> q e
  c4 c,, c c
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
