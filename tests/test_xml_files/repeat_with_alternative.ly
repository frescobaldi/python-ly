\version "2.19.55"

\header {
  title = "repeat with alternative"
}

\score {
  \relative c'{
	% Simple repeat with a simple alternative
    c1 |
    \repeat volta 2{ c1| }
    \alternative {
      { d1 | }
      { d1 | e1 |}
    }

	% Simple repeat with more repeats than alternatives
    c1 |
    \repeat volta 3{ c1| }
    \alternative {
      { d1 | }
      { d1 | e1 |}
    }

	% Simple repeat with many endings
    c1 |
    \repeat volta 5{ c1| }
    \alternative {
      { d1 | e1 |}
      { d1 | f1 |}
      { d1 |}
    }
  }
  \layout {}
}
