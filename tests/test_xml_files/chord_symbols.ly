\version "2.18.2"

\language "english"

keyTime = {
   \time 4/4
   \numericTimeSignature
   \key c \major
}

Soprano = \relative c'' {
 \voiceOne
 \keyTime

  c1
| c4 c4 c4 c4
| c4 c4 c4 c4
| c4 c4 c4 c4
| c4 c4 c4 c4
| c4 c4 c4 c4
| c4 c4 c4 c4
| c4 c4 c4 c4

}

Alto = \relative c'' {
 \voiceTwo
 \keyTime

  a1
| a1
| a1
| a1
| a1
| a1
| a1
| a1

}

Tenor = \relative c {
 \voiceOne
 \keyTime

  c1
| c1
| c1
| c1
| c1
| c1
| c1
| c1

}

Bass = \relative c {
 \voiceTwo
 \keyTime

  a1
| a1
| a1
| a1
| a1
| a1
| a1
| a1

}

Chords = \relative c' {
 \chordmode {

a1
b4 s cs2
s1
df/es
f:maj7/g
g:m6
a:sus4
b:maj9

   }
}

\score
{
  <<
	<<
	\new ChordNames {\Chords}
	>>

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