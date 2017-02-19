\version "2.19.55"

\header {
  title = "lyrics simple lyricsto"
}

verse = \lyricmode {
 \set stanza = "1"
 Do -- re -- mi fa
 Hel -- lo __ the -- re 
}

chorus = \lyricmode {
 \set stanza = "chor"
 This is the cho -- rus, la __ di -- da
}

\score {
    \new Staff {
      <<
      \new Voice = "main" {
        \voiceOne
        \clef treble
        \relative c' {
          c4 d e f |
          g16 a4( f8.) b4 c4 |
        }
      }
      \new Voice = "mainTwo" {
        \voiceTwo
        \clef treble
        \relative c' {
          c2 c | g' g |
        }
      }
      \new Lyrics \lyricsto "main" \verse
      \new Lyrics \lyricsto "main" \chorus
      >>
    }
  \layout { }
}
\voiceTwo