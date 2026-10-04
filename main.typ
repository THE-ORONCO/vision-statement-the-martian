#set page(paper: "presentation-16-9", margin: (x: 1.5cm, y: 1.1cm))
#set text(lang: "de", size: 10pt)
#set par(justify: true, leading: 0.55em)
#show heading.where(level: 1): set text(size: 18pt)
#show heading.where(level: 2): set text(size: 12pt, fill: rgb("#4a6fa5"))
// "Das X" als blaue Box (Adam, Game Producer's Guide)
#show quote: it => block(
  fill: rgb("#6a95cc"), inset: 9pt, radius: 2pt, width: 100%,
  align(center, text(fill: white, weight: "bold", size: 13pt, it.body)),
)

#include "drafts/a-muenchhausen-mond.typ"
#pagebreak()
#include "drafts/c-aschenland-alchemistin.typ"
#pagebreak()
#include "drafts/c-aschenland-muenchhausen.typ"
