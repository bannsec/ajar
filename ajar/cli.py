#!/usr/bin/env python3 -u

import argparse
import multiprocessing
from traitlets.config import get_config
import requests
import json
from time import sleep

import IPython
from chess import pgn
import chess

BASE_FEN = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'
DEFAULT_DEPTH = 24
DEFAULT_MINIMUM_GAMES = 100
LICHESS_BACKOFF = 10
LICHESS_PERCENT = 0.7 # 0.6 would mean only look at top 40% played moves
DEFAULT_OUTFILE = "{fen}_p{percent}_d{depth}.pgn"

LICHESS_STATS_PARAMETERS = {
    "variant": "standard",
    "moves": "12",
    "topGames": "4",
    "recentGames": "4",
    "speeds[]": ["classical", "rapid", "blitz"],
    "ratings[]": ["1600", "1800", "2000", "2200", "2500"],
}

STOCKFISH_PATH = "/home/user/stockfish_14_linux_x64_avx2/stockfish_14_x64_avx2"

def get_lichess_stats(fen):
    LICHESS_STATS_PARAMETERS["fen"] = fen
    r = requests.get("https://explorer.lichess.ovh/lichess", LICHESS_STATS_PARAMETERS)
    if not r.ok:
        if r.status_code == 429:
            print(f"Too many lichess requests.. pausing for {LICHESS_BACKOFF} seconds.")
            sleep(LICHESS_BACKOFF)
            return get_lichess_stats(fen)

        import ipdb
        ipdb.set_trace()
    
    return json.loads(r.content)

def parse_args():
    global LICHESS_STATS_PARAMETERS
    cores = multiprocessing.cpu_count()
    parser = argparse.ArgumentParser(description="Auto generate a chess opening.")
    parser.add_argument("-cores", type=int, default=cores,
            help=f"Number of cores to use. (default {cores})")
    parser.add_argument("-depth", type=int, default=DEFAULT_DEPTH,
            help=f"Depth to search. (default {DEFAULT_DEPTH})")
    parser.add_argument("-fen", type=str, default=BASE_FEN,
            help=f"Set starting FEN position. (default base chess setup)")
    parser.add_argument("-percent", type=float, default=LICHESS_PERCENT,
            help=f"Top percent of seen moves to use. Values closer to 1 will give you wider results. (default {LICHESS_PERCENT})")
    parser.add_argument("-outfile", type=str, default=DEFAULT_OUTFILE,
            help=f"What file to write the output to. (default {DEFAULT_OUTFILE})")
    parser.add_argument("--min-games", type=int, default=DEFAULT_MINIMUM_GAMES,
            help=f"Minimum number of games to consider for inclusion. (default {DEFAULT_MINIMUM_GAMES})")
    parser.add_argument("--my-turn", default=False, action='store_true',
            help="Is it my turn? Default to false.")
    parser.add_argument("-ratings", default=None, nargs="*",
            help=f"""List of ratings to search. Default searches all of {LICHESS_STATS_PARAMETERS["ratings[]"]}""")
    parser.add_argument("-i", default=False, action='store_true',
            help=f"Start ipython session.")
    args = parser.parse_args()

    if args.ratings:
        if any(x not in ["1600", "1800", "2000", "2200", "2500"] for x in args.ratings):
            raise Exception("Invalid rating selected")
        LICHESS_STATS_PARAMETERS["ratings[]"] = args.ratings

    return args

def run(game, stockfish, my_turn, previous_score=None):

    # Tell stockfish where we are
    #stockfish.set_fen_position(game.board().fen())
    # chess.svg.board(game.board(), size=400)
    #print(stockfish.get_board_visual())
    print(f"---------------\n{game.board()}")

    # If not my turn, look at common moves
    if not my_turn:
        print("---------------\n")
        stats = get_lichess_stats(game.board().fen())
        if stats["moves"] != []:
            cutoff = (stats["moves"][0]["white"] + stats["moves"][0]["draws"] + stats["moves"][0]["black"]) * (1 - args.percent)
            for move in stats["moves"]:
                total_played = move["white"] + move["draws"] + move["black"]
                # If this move is played enough, let's look at it
                if total_played >= args.min_games and total_played > cutoff:
                    run(game.add_variation(chess.Move.from_uci(move["uci"])), stockfish, not my_turn, previous_score=previous_score)

    else:
        # Ask stockfish
        eval = stockfish.analyse(game.board(), chess.engine.Limit(depth=args.depth))
        print("evalulating ... ", flush=True, end="")
        print(eval['score'].relative.score(mate_score=100000) / 100)
        print("---------------\n")
        game.set_eval(eval['score'], args.depth)

        if game.parent and previous_score:
            if eval['score'].relative.score(mate_score=100000) - previous_score.relative.score(mate_score=100000) > 200:
                game.comment = "Blunder"
            elif eval['score'].relative.score(mate_score=100000) - previous_score.relative.score(mate_score=100000) > 100:
                game.comment = "Inaccurate"

        #run(game.add_variation(chess.Move.from_uci(stockfish.get_best_move())), stockfish, not my_turn)
        run(game.add_variation(eval['pv'][0]), stockfish, not my_turn, previous_score=eval['score'])

    return game

def main():
    global args
    args = parse_args()
    #stockfish = Stockfish("/home/user/stockfish_14_linux_x64_avx2/stockfish_14_x64_avx2", parameters={"Threads": args.cores})
    #stockfish.set_depth(args.depth)
    stockfish = chess.engine.SimpleEngine.popen_uci(STOCKFISH_PATH)
    stockfish.configure({"Threads": args.cores})

    game = pgn.Game()
    game.setup(args.fen)
    # game.add_variation(chess.Move.from_uci("e2e3"))

    if args.i:
        c = get_config()
        c.InteractiveShellEmbed.colors = "Linux"
        IPython.embed(config=c)

    else:
        game = run(game, stockfish, my_turn=args.my_turn)
        outfile = args.outfile.format(percent=args.percent, depth=args.depth, fen=args.fen.replace("/","_"))
        with open(outfile, "w") as f:
            f.write(str(game))
        print(f"pgn written to: {outfile}")
        stockfish.close()


if __name__ == "__main__":
    main()
