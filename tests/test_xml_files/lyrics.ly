\version "2.18.2"

slurOff = { \set ignoreMelismata = ##t }
slurOn = { \unset ignoreMelismata }

StanzaOne = \lyricmode {
  La _ di __ \slurOff la di \slurOn da
  Ba dum dun
  Li -- del -- li zap
}

StanzaTwo = \lyricmode {
  \slurOn This is a __ song for 
  cool peo -- ple
  \slurOff Just a test for us \slurOn
}

StanzaThree = \lyricmode {
  \slurOn This is a \slurOff tune for \slurOn
  some peo -- ple
  Just a test for us
}

\language "english"

keyTime = {
    \time 4/4
    \numericTimeSignature
    \key c \major
}

Soprano = \relative c'' {
  \voiceOne
  \keyTime
    b4 c( d e)
  | g( a) b( c) 
  | g2 a
  | f8 g c a( c) b g f
}

Alto = \relative c' {
  \voiceTwo
  \keyTime
    g4 g e e
  | f d e e 
  | g2 a
  | f8 g c a( c) b g f
}

Tenor = \relative c' {
  \voiceOne
  \keyTime
    a4 b a b
  | b a b a 
  | g2 a
  | f8 g c a( c) b g f
}

Bass = \relative c {
  \voiceTwo
  \keyTime
    c4 g a8 g g g
  | d4 b d b
  | g2 a
  | f8 g c a( c) b g f
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
		\lyricsto SopranoVoice \new Lyrics \StanzaOne
		\lyricsto SopranoVoice \new Lyrics \StanzaTwo
		\lyricsto SopranoVoice \new Lyrics \StanzaThree
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