\version "2.19.55"

\header {
  title = "merge voices with slurs"
}

sopranoOne = \relative c'' {
  % Music follows here.
  c1( | c) | 
  c( | c) |
  c( | c) |

  c2( d) |

  c4\( r2 d4( | e) r2 c4\) |
}

sopranoTwo = \relative c'' {
  % Music follows here.
  c1( | c) | 
  r2 c2( | c2) r2 |
  r2 c2( | r2 c2) |

  r4 e( f) r4 |

  r4 c4\( d( r4 | r4 d) c4\) r4 |
}

\score {
  \new ChoirStaff <<
    \new Staff <<
      \new Voice = "soprano1" { \voiceOne \sopranoOne }
      \new Voice = "soprano2" { \voiceTwo \sopranoTwo }
    >>
  >>
  \layout { }
}
