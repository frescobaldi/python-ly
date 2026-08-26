\version "2.18.2"

% Markup not attached to a note (here \mark) belongs to the bar it is written in
% Note: emitting both <rehearsal> and <words> for one \mark is a known defect (#121)

\score {
  \relative {
    a'1^\markup intenso |
    \mark \markup Coda
    a1 |
    a1
  }
}
