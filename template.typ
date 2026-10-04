// Gemeinsames Layout aller Vision Statements: Folie 1 = Titel, Bild, X; Folie 2 = Inhalt in drei Spalten.
#let vision(title: none, x: none, img: none, about: none, gameplay: none, strands: none, dna: none, anchors: ()) = {
  page[
    #heading(level: 1, title)
    #v(-0.4em)
    #text(size: 11pt, fill: gray)[Arbeitstitel]
    #v(0.6em)
    #align(center, img)
    #v(0.8em)
    #quote(block: true, x)
  ]
  page(grid(
    columns: (1fr, 1fr, 1fr),
    column-gutter: 0.9cm,
    [
      == Worum geht es?
      #about
      == Core Gameplay
      #gameplay
    ],
    [
      == Die DNA des Spiels
      #dna
    ],
    [
      == Drei Stränge, drei Figuren
      #strands
      == Dramaturgische Anker
      #set text(size: 0.9em)
      #table(
        columns: (auto, 1fr),
        stroke: 0.4pt + gray,
        inset: 3.5pt,
        ..anchors.map(((k, v)) => ([*#k*], v)).flatten(),
      )
    ],
  ))
}
