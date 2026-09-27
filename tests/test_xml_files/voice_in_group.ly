\version "2.18.2"

\score {
  \new StaffGroup <<
    \new Voice = "S" { \set Staff.instrumentName = #"Cantus" c''2 d'' }
    \addlyrics { Du tout }
    \new Voice = "B" { \set Staff.instrumentName = #"Bassus" c2 g, }
    \addlyrics { plon giet }
  >>
}
