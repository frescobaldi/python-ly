\version "2.18.2"

\score {
  \relative {
    a'2-\markup intenso
    a2_\markup intenso |
    a2^\markup { poco più forte }
    r2 |
    r1 -\markup neutral _\markup below ^\markup above
  }
}