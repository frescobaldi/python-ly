\score {
 \relative c' {
  c4\sustainOn d e\sustainOff f |
  c8\sustainOn c d d\sustainOff\sustainOn e e f f \sustainOff |

  \set Staff.pedalSustainStyle = #'mixed
  c4\sustainOn d e\sustainOff f |
  c8\sustainOn c d d\sustainOff\sustainOn e e f f\sustainOff |

  \set Staff.pedalSustainStyle = #'bracket
  c4\sustainOn d e\sustainOff f |
  c8\sustainOn c d d\sustainOff\sustainOn e e f f\sustainOff |

  \set Staff.pedalSustainStyle = #'text
  c4\sustainOn d e\sustainOff f |
  c8\sustainOn c d d\sustainOff\sustainOn e e f f\sustainOff |
 }
 \layout{}
}
