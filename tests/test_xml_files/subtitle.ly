\version "2.18.2"

\language "english"

\header{
   title = "Title"
   subtitle = "Subtitle"
}

keyTime = {
    \time 4/4
}

Soprano = \relative c'' {
  \keyTime
    c4 c c2
    c c4 c \bar "|."
}

Alto = \relative c'' { }

\score
{
  <<
    \new Staff \Soprano
  >>
}