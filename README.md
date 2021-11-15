
# About
`ajar` is a python package that attempts to automate the generation of opening PGNs. It does this by allowing the user to specify a starting position (in FEN notation), as well as parameters such as depth, percent, etc. It then utilizes lichess's database to identify likely responses to moves, and uses Stockfish to generate computer approved moves.

The output pgn can be used in places like lichess/chesstempo/etc for studying. Remember that Stockfish cannot explain it's ideas behind moves, and so your opening PGNs may not always have human moves. If you're looking for explanations of opening systems, it's still better to find a master's course or free opening lessons on lichess.

# Installation
```bash
pip install ajar
```

# Help
```
usage: ajar [-h] [-cores CORES] [-depth DEPTH] [-fen FEN] [-percent PERCENT] [-outfile OUTFILE] [--min-games MIN_GAMES] [--my-turn] [-ratings [RATINGS [RATINGS ...]]] [-i]

Auto generate a chess opening.

optional arguments:
  -h, --help            show this help message and exit
  -cores CORES          Number of cores to use. (default 8)
  -depth DEPTH          Depth to search. (default 24)
  -fen FEN              Set starting FEN position. (default base chess setup)
  -percent PERCENT      Top percent of seen moves to use. Values closer to 1 will give you wider results. (default 0.7)
  -outfile OUTFILE      What file to write the output to. (default {fen}_p{percent}_d{depth}.pgn)
  --min-games MIN_GAMES
                        Minimum number of games to consider for inclusion. (default 100)
  --my-turn             Is it my turn? Default to false.
  -ratings [RATINGS [RATINGS ...]]
                        List of ratings to search. Default searches all of ['1600', '1800', '2000', '2200', '2500']
  -i                    Start ipython session.
```

# Example
Example pgn files are in the `examples` directory.

```bash
# Auto generate a chess opening playing as white the advance french defense.
# Let's assume we're lower rated (1600/1800) and only want to know the basics of this opening
# Dial down the percent to 0.4 to only look at the most common responses at this level
# Drop min-games since we're dropping percent
ajar -fen 'rnbqkbnr/ppp2ppp/4p3/3pP3/3P4/8/PPP2PPP/RNBQKBNR b KQkq - 0 3' -percent 0.4 -ratings 1600 1800 --min-games 50
```