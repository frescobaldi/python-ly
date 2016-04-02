\version "2.12.3"

\header {
  title = "Somebody to love"
}

partone = \relative c'' {
  \key aes \major
  aes4 bes c c
}

parttwo = \relative c' {
  \key aes \major
  aes4 g aes aes
}

staffone = \new ChoirStaff {
  \new Staff {
    \partone
  }
}

stafftwo = \new ChoirStaff {
  \new Staff {
    \parttwo
  }
}

\score {
  <<
    \staffone
    \stafftwo
  >>
  \layout {}
}
