\version "2.22.2"

% \rest converts the note it follows where that note stands, even when the note
% completed the bar (issue #147)

\score {
  \relative b' {
    \time 2/4
    b4. b8 \rest |
    b8 \rest b8 b4
  }
}
