\version "2.24.0"

% Test chord duration counting for bar boundaries (issue #171)
% Both explicit chords and duration shorthand must count toward measure duration

\score {
  <<
    % Explicit chord notation: 3 measures
    \new Staff { c''1 | <d'' f'' a''>1 | e''1 }

    % Duration shorthand after chord: 3 measures
    \new Staff { \time 3/4 <e' f'>4 4 4 | 4 4 8 r8 | r4 a' g' }
  >>
  \layout { }
}
