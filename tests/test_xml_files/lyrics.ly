\version "2.18.2"

slurOff = { \set ignoreMelismata = ##t }
slurOn = { \unset ignoreMelismata }

StanzaOne = \lyricmode {
  \set stanza = "1."  
  La _ di __ \slurOff la di \slurOn da
  Ba dum dun
  Li -- del -- li zap
}

StanzaTwo = \lyricmode {
  \set stanza = "2."
  \slurOn This is a __ song for 
  cool peo -- ple
  \slurOff Just a test for us \slurOn
}

StanzaThree = \lyricmode {
  \set stanza = "3."
  \slurOn This is a \slurOff tune for \slurOn
  some peo -- ple
  Just a test for us
}

\language "english"

keyTime = {
    \time 4/4
    \numericTimeSignature
    \key ef \major
}

Soprano = \relative c'' {
  \voiceOne
  \keyTime
    bf4 cs( d ef)
  | gf( af) b( c) 
  | g2 a
  | f8 g c a( c) b g f
}

Alto = \relative c' {
  \voiceTwo
  \keyTime
    g4 g ef ef
  | f d ef e 
  | g2 a
  | f8 g c a( c) b g f
}

Tenor = \relative c' {
  \voiceOne
  \keyTime
    af4 bf af bf
  | bf af bf af 
  | g2 a
  | f8 g c a( c) b g f
}

Bass = \relative c {
  \voiceTwo
  \keyTime
    cf4 g af8 gf gf gf
  | ds4 bf ds bf
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