## Turing-compleet omdat:
De definitie van Turing Compleetheid van Wikipedia is: "An imperative language is Turing-complete if it has conditional branching, and the ability to tchange an arbitrary amount of memory."<br>
Om te bewijzen of een programmeertaal Turing-compleet is, vergelijkt men graag de programmeertaal met de meest basic programmeertaal die bewezen Turing compleet is. In dit geval, Brainfuck. Deze programmeertaal wordt vaak gebruikt om Turing compleetheid aan te geven vanwege de simpelheid van haar instructies. <br> 
Brainfuck heeft namelijk maar 8 instructies:<br>

| **Command**   | **Description**                     |
|:-------------:|:-----------------------------------:|
| `>`             | Move memory pointer to the right    |
| `<`             | Move memory pointer to the left     |
| `+`             | Increment memory cell at the pointer| 
| `-`             | Decrement memory cell at the pointer|
| `.`             | Output the character signified by the cell at the pointer |
| `,`             | Input a character and store it in the cell at the pointer |
| `[`             | Jump past the matching `]` if the cell at the pointer is 0 |
| `]`             | Jump back to the matching `[` if the cell at the pointer is nonzero |

Om te bewijzen dat mijn interpreter Turing compleet is, moet ik dus bewijzen dat mijn taal in ieder geval de bovenstaande functionaliteit bevat. <br>
De `+`, `-`, `<` en `>` worden gebruikt om waardes in memory te zetten. In mijn programmeertaal wordt dezelfde functionaliteit geleverd door middel van de volgende operators. `operator+` `operator-` en `operator=` <br>
De `.` wordt gebruikt om de waarde in memory uit te printen. In mijn programmeertaal wordt dezelfde functionaliteit geleverd door middel van `showme` <br>
De `[` en `]` worden gebruikt voor loops en if statements. In mijn programmeertaal wordt dezelfde functionaliteit geleverd door middel van `if` en `while`


## Code is geschreven in functionele stijl.

## Taal ondersteunt:
Loops? Voorbeeld: [parsertest.use] - [regel 21]

## Bevat: 
Classes met inheritance: bijvoorbeeld [myparser.py] - [regel 7]
Object-printing voor elke class: [ja]
Decorator: functiedefinitie op [myparser.py] - [regel 6], toegepast op [myparser.py] - [regel 90]
Type-annotatie: Haskell-stijl in comments: [nee]; Python-stijl in functiedefinities: [ja]
Minstens drie toepassingen van hogere-orde functies:
1. [interpret.py] - [regel 138]
2. [lexer.py] - [regel 121]
3. [myparser.py] - [regel 198]

## Interpreter-functionaliteit Must-have:
Functies: [meer per file]
Functie-parameters kunnen aan de interpreter meegegeven worden door: parameters tussen de haakjes toe te voegen
Functies kunnen andere functies aanroepen: zie voorbeeld [parsertest.py] - [regel 6]
Functie resultaat wordt op de volgende manier weergegeven: Door middel van de return van de functie te printen

## Interpreter-functionaliteit (should/could-have):
[Gekozen functionaliteit] geïmplementeerd door middel van de volgende functies: a) [functie] in [file] op regel [regel]
### Eigen gekozen taal
### Error handling


## Compiler-functionaliteit Must-have:
De gecompilede code kan geupload worden dankzij platformio met commando `pio run --target upload`

Unit tests geschreven in 'ATP_DUE/test/test.cpp'
Te runnen door in de ATP_DUE folder het commando `pio test` te runnen


## Overige gemaakte keuzes:
Compiler heeft GEEN error checking