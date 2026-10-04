#set page(paper: "presentation-16-9", margin: (x: 1.5cm, y: 1.1cm))
#set text(lang: "de", font: "Fira Sans", size: 12.75pt)
#set par(leading: 0.55em)
#set list(spacing: 0.6em, indent: 0pt)
#show heading: set text(font: "Libertinus Serif")
#show heading.where(level: 1): set text(size: 24pt)
#show heading.where(level: 2): set text(size: 17pt, fill: rgb("#4a6fa5"))
#show heading.where(level: 2): set block(above: 1em, below: 0.6em)
// "Das X" als blaue Box (Adam, Game Producer's Guide)
#show quote: it => block(
  fill: rgb("#6a95cc"), inset: 9pt, radius: 2pt, width: 100%,
  align(center, text(fill: white, weight: "bold", size: 17pt, it.body)),
)

// KI-generierte Bilder müssen rot umrandet sein (Vorgabe Prüfer)
#show image: it => box(stroke: 10pt + red, it)

#include "drafts/a-muenchhausen-selenothek.typ"
#include "drafts/c-aschenland-alchemistin.typ"
