\version "2.18.2"

keyTime = {
    \time 3/4
    \numericTimeSignature
    \key c \major
}

Soprano = \relative c'' {
  \voiceOne
  \keyTime
  g8 \noBeam g g \noBeam g g g
  g8[ g g] g [g] g
  g16 g[ <g e f>8 g] g g <g e f>
  g8 g16 g g g g[ g g g g] g
  \time 4/4 \set Timing.baseMoment = #(ly:make-moment 1 4) \set Timing.beatStructure = #'(1 3)
  g8 g g g g g g g
  g16 g g g g g g g g g g g g g g g
  \set Timing.beamExceptions = #'() 
  g8 g g g g4 g8 g
  g16 g g g g g s g g[ g] \noBeam g g r g g g \noBeam
  g16 g \autoBeamOff g g g g[ g] g g g[ \autoBeamOn g] g g8 g
  \set Timing.baseMoment = #(ly:make-moment 1 1) \set Timing.beatStructure = #'(1)
  g8 \autoBeamOff g r g g g g g \autoBeamOn
  \set Timing.baseMoment = #(ly:make-moment 1 4) \set Timing.beatStructure = #'(2 3)
  g8 g g g g g g g
  \set Timing.beatStructure = #'(2 1)
  g8 g g g g g g g
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
