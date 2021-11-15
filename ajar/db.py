import os
import atexit

import sqlalchemy.ext.declarative, sqlalchemy.orm, sqlalchemy
import appdirs


# Create a sqlalchemy table as a class
# Columns:
#   id: int (primary key)
#   fen: string (FEN notation)
#   move: string (move in algebraic notation)
#   eval: double (evaluation of the move)
#   depth: int (depth of the analysis)
# (fen, move, depth) are unique together
class Move(sqlalchemy.ext.declarative.declarative_base()):
    __tablename__ = "moves"
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    fen = sqlalchemy.Column(sqlalchemy.String)
    move = sqlalchemy.Column(sqlalchemy.String)
    eval = sqlalchemy.Column(sqlalchemy.Float)
    depth = sqlalchemy.Column(sqlalchemy.Integer)
    __table_args__ = (sqlalchemy.UniqueConstraint('fen', 'move', 'depth'),)

    def __repr__(self):
        return f"Move(id={self.id}, fen='{self.fen}', move='{self.move}', eval={self.eval}, depth={self.depth})"

def save_move(fen, move, eval, depth):
    # Create a new move
    move = Move(fen=fen, move=move, eval=eval, depth=depth)

    # Save the move
    session.add(move)
    session.commit()

def get_all_moves(fen, depth, or_greater=True):
    # Get all moves for a given fen and depth
    # Order by eval
    if or_greater:
        # Find all moves with a depth greater than or equal to the given depth
        moves = session.query(Move).filter(Move.fen == fen).filter(Move.depth >= depth).order_by(Move.eval.desc()).all()
    else:
        # Find all moves with a depth exactly equal to the given depth
        moves = session.query(Move).filter(Move.fen == fen).filter(Move.depth == depth).order_by(Move.eval.desc()).all()

    return moves

def get_top_move(fen, depth):
    # Get the top move for a given fen and depth
    moves = get_all_moves(fen, depth)
    if len(moves) > 0:
        return moves[0]
    else:
        return None

def remove_moves_fen_depth(fen, depth):
    # Remove all moves for a given fen and depth
    session.query(Move).filter(Move.fen == fen).filter(Move.depth == depth).delete()
    session.commit()

def remove_moves_fen(fen):
    # Remove all moves for a given fen
    session.query(Move).filter(Move.fen == fen).delete()
    session.commit()


# Create appdirs object
app_dirs = appdirs.AppDirs('ajar', 'bannsec')

DBNAME = "moves.db"
DBFULLPATH = os.path.join(app_dirs.user_data_dir, DBNAME)

os.makedirs(app_dirs.user_data_dir, exist_ok=True)

# Create sqlalchemy engine
engine = sqlalchemy.create_engine("sqlite:///{}".format(DBFULLPATH))

# Create sqlalchemy session
session = sqlalchemy.orm.sessionmaker(bind=engine)()

# Create table if it doesn't exist
Move.metadata.create_all(engine)

# Register atexit to vacuum the database
@atexit.register
def vacuum_db():
    session.execute("VACUUM")
    session.commit()