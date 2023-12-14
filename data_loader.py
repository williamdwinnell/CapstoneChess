# Description:
# This file loads from the massive Lichess dataset, 
# samples a certain number of train and test games, 
# and produces a jsonl file of trainable chess position data

import chess
import chess.pgn
import random
import os
import io
import json

def load_games_from_pgn(pgn_file, total_games=10):
    games = []
    with open(pgn_file) as f:
        while len(games) < total_games:
            game = chess.pgn.read_game(f)
            if game is None:
                print("nullio")
                break
            games.append(game)
    return games

def extract_random_game_from_pgn(pgn_file, chunk_size=1024):
    # Check if the file exists
    if not os.path.isfile(pgn_file):
        return None

    # Open the PGN file
    with open(pgn_file, "r") as pgn:
        # Get the file size
        file_size = os.path.getsize(pgn_file)

        # Choose a random starting position within the file
        start_position = random.randint(0, file_size - chunk_size)

        # Move to the chosen starting position
        pgn.seek(start_position)

        # Read a chunk of data from the file
        chunk = pgn.read(chunk_size)

        # Find the closest "[Event" string from the end of the chunk
        event_index = chunk.rfind("[Event")

        if event_index == -1:
            # If no "[Event" string is found in the chunk, try again recursively
            return extract_random_game_from_pgn(pgn_file)

        # Extract the game data from the chunk starting from the "[Event" string
        game_data = chunk[event_index:]

        # Continue reading and accumulating data until the next "[Event" string is found
        while True:
            chunk = pgn.read(chunk_size)
            next_event_index = chunk.find("[Event")
            if next_event_index != -1:
                game_data += chunk[:next_event_index]
                break
            else:
                game_data += chunk

        # Create a PGN game object from the extracted data using StringIO
        game_stream = io.StringIO(game_data)
        pgn_game = chess.pgn.read_game(game_stream)

        return pgn_game

def extract_random_games_from_pgn(pgn_file, num_games, chunk_size=1024):

    # Check if the file exists
    if not os.path.isfile(pgn_file):
        return None

    random_games = []

    # Open the PGN file
    with open(pgn_file, "r") as pgn:
        # Get the file size
        file_size = os.path.getsize(pgn_file)

        for _ in range(num_games):
            # Choose a random starting position within the file
            start_position = random.randint(0, file_size - chunk_size)

            # Move to the chosen starting position
            pgn.seek(start_position)

            # Read a chunk of data from the file
            chunk = pgn.read(chunk_size)

            # Find the closest "[Event" string from the end of the chunk
            event_index = chunk.rfind("[Event")

            if event_index == -1:
                # If no "[Event" string is found in the chunk, try again
                continue

            # Extract the game data from the chunk starting from the "[Event" string
            game_data = chunk[event_index:]

            # Continue reading and accumulating data until the next "[Event" string is found
            while True:
                chunk = pgn.read(chunk_size)
                next_event_index = chunk.find("[Event")
                if next_event_index != -1:
                    game_data += chunk[:next_event_index]
                    break
                else:
                    game_data += chunk

            # Create a PGN game object from the extracted data using StringIO
            game_stream = io.StringIO(game_data)
            pgn_game = chess.pgn.read_game(game_stream)

            if pgn_game:
                random_games.append(pgn_game)

    return random_games

def extract_game_info(pgn):

    # Extract player Elo ratings
    white_elo = int(pgn.headers.get("WhiteElo", "0"))
    black_elo = int(pgn.headers.get("BlackElo", "0"))

    # Initialize an empty list to store the move sequence
    move_sequence = []

    # Iterate through the moves and append them to the move sequence
    board = pgn.board()
    for move in pgn.mainline_moves():
        move_sequence.append(board.san(move))
        board.push(move)

    # Calculate the average Elo rating of the two players
    avg_elo = (white_elo + black_elo) / 2

    # Return a dictionary containing the extracted information
    game_info = {
        "AverageElo": avg_elo,
        "MoveSequence": move_sequence,
    }

    return game_info

def filter_entries_by_elo(entries, min_elo, max_elo):
    filtered_entries = [entry for entry in entries if min_elo <= entry.get('AverageElo', 0) <= max_elo]
    return filtered_entries

def fen_to_piece_description(fen):
    board = chess.Board(fen)
    piece_description = ""

    for color in [chess.WHITE, chess.BLACK]:
        for piece_type in [chess.PAWN, chess.KNIGHT, chess.BISHOP, chess.ROOK, chess.QUEEN, chess.KING]:
            pieces = list(board.pieces(piece_type, color))
            if pieces:
                piece_names = [chess.square_name(piece) for piece in pieces]
                piece_description += f"{chess.COLOR_NAMES[color]} has {len(pieces)} {chess.PIECE_NAMES[piece_type]}{'s' if len(pieces) > 1 else ''} on: {','.join(piece_names)}\n"
            else:
                piece_description += f"{chess.COLOR_NAMES[color]} has no {chess.PIECE_NAMES[piece_type]}\n"

    return piece_description

def generate_legal_moves(game_data, n):
    # Create a chess board from the MoveSequence
    board = chess.Board()
    move_sequence = game_data['MoveSequence']
    positions = []
    legal_moves_with_sequence = []

    # Include the starting position with White to move and all legal moves
    initial_moves = list(board.legal_moves)
    side_to_move = "White"
    legal_moves_with_sequence.append({'move_sequence': [],
                                      'side_to_move': side_to_move,
                                      'board_state': fen_to_piece_description(board.fen()),
                                      'legal_moves': [board.san(move) for move in initial_moves],
                                      'next_move': move_sequence[0] if move_sequence else None})

    for move in move_sequence:
        board.push_san(move)
        legal_moves = list(board.legal_moves)
        positions.append(board.fen())
        side_to_move = "White" if board.turn == chess.WHITE else "Black"
        next_move = move_sequence[move_sequence.index(move) + 1] if move_sequence.index(move) + 1 < len(move_sequence) else None
        legal_moves_with_sequence.append({'move_sequence': move_sequence[:len(positions)],
                                          'board_state': fen_to_piece_description(board.fen()),
                                          'side_to_move': side_to_move,
                                          'legal_moves': [board.san(move) for move in legal_moves],
                                          'next_move': next_move})

    for _ in range(n):
        if not legal_moves:
            break
        random_move = random.choice(legal_moves)
        move_sequence = move_sequence + [board.san(random_move)]
        board.push(random_move)

        # Append the FEN (Forsyth-Edwards Notation) of the new position
        positions.append(board.fen())
        legal_moves = list(board.legal_moves)
        side_to_move = "White" if board.turn == chess.WHITE else "Black"
        next_move = move_sequence[move_sequence.index(random_move) + 1] if move_sequence.index(random_move) + 1 < len(move_sequence) else None
        legal_moves_with_sequence.append({'move_sequence': move_sequence[:len(positions)],
                                          'board_state': fen_to_piece_description(board.fen()),#board.fen(),
                                          'side_to_move': side_to_move,
                                          'legal_moves': [board.san(move) for move in legal_moves],
                                          'next_move': next_move})
        
    return legal_moves_with_sequence

def generate_data_moves(game_data, n):

    # Create a chess board from the MoveSequence
    board = chess.Board()
    move_sequence = game_data['MoveSequence']
    positions = []
    legal_moves_with_sequence = []

    # Include the starting position with White to move and all legal moves
    initial_moves = list(board.legal_moves)
    side_to_move = "White"
    legal_moves_with_sequence.append({
        'side_to_move': side_to_move,
        'board_state': fen_to_piece_description(board.fen()),
        'legal_moves': [board.san(move) for move in initial_moves],
        'next_move': move_sequence[0] if move_sequence else None
    })

    for move in move_sequence:
        board.push_san(move)
        legal_moves = list(board.legal_moves)
        positions.append(board.fen())
        side_to_move = "White" if board.turn == chess.WHITE else "Black"
        next_move = move_sequence[move_sequence.index(move) + 1] if move_sequence.index(move) + 1 < len(move_sequence) else None
        legal_moves_with_sequence.append({
            'board_state': fen_to_piece_description(board.fen()),
            'side_to_move': side_to_move,
            'legal_moves': [board.san(move) for move in legal_moves],
            'next_move': next_move
        })

    for _ in range(n):
        if not legal_moves:
            break
        random_move = random.choice(legal_moves)
        move_sequence = move_sequence + [board.san(random_move)]
        board.push(random_move)

        # Append the FEN (Forsyth-Edwards Notation) of the new position
        positions.append(board.fen())
        legal_moves = list(board.legal_moves)
        side_to_move = "White" if board.turn == chess.WHITE else "Black"
        next_move = move_sequence[move_sequence.index(random_move) + 1] if move_sequence.index(random_move) + 1 < len(move_sequence) else None
        legal_moves_with_sequence.append({
            'board_state': fen_to_piece_description(board.fen()),
            'side_to_move': side_to_move,
            'legal_moves': [board.san(move) for move in legal_moves],
            'next_move': next_move
        })

    return legal_moves_with_sequence

def sample_to_readable(sample):
    samp = {"input":"", "output":""}
    samp["input"] += "Game Sequence: " + str(sample["move_sequence"])  + "\nCurrent Position: " + str(sample["board_state"]) + "\n" + sample["side_to_move"] + " to move.\n" + "Legal Moves: " + str(sample['legal_moves'])
    next_move = sample["next_move"]
    if next_move == None:
        next_move = "Game Over."
    samp["output"] += next_move
    return samp

def games_to_readables(cleaned_games):

    # Store all the samples
    samples = []

    for game in cleaned_games:
        # Get all the meta data + legal moves for each position including the actual move played
        game_samples = generate_legal_moves(game, 0)

        in_n_outs = []

        # Convert the samples to (input, output) format with formatting
        for sample in game_samples:
            in_n_outs.append(sample_to_readable(sample))

        # Add all of the samples to the main list
        samples.extend(in_n_outs)

    return samples

def export_data_to_jsonl(data, filename):
    # Export the data to a JSONL file
    with open(filename + ".jsonl", "w") as jsonl_file:
        for item in data:
            jsonl_file.write(json.dumps(item) + '\n')


if __name__ == "__main__":
    # Has about 22,000,000 games
    pgn_file_path = "lichess_db_standard_rated_2018.pgn"
    
    try:
        games = load_games_from_pgn(pgn_file_path, total_games=500)
        random.shuffle(games)

        cleaned_games = [extract_game_info(game) for game in games]

        low_elo = filter_entries_by_elo(cleaned_games, 1300, 1650)
        med_elo = filter_entries_by_elo(cleaned_games, 1551, 1800)
        high_elo = filter_entries_by_elo(cleaned_games, 1801, 3000)

        #print("Low Elo Samples: ", len(low_elo))
        #print("Medium Elo Samples: ", len(med_elo))
        #print("High Elo Samples: ", len(high_elo))

        # Number of games for the validation set
        validation_games = 20

        # Train / Test Split for low elo games
        low_elo_train = low_elo[:len(low_elo)-validation_games]
        low_elo_val = low_elo[len(low_elo)-validation_games:]
        
        # Convert to a format for training a model (input, output)
        readable_train = games_to_readables(low_elo_train)
        readable_val = games_to_readables(low_elo_val)

        # Randomize the samples
        random.shuffle(readable_train)
        random.shuffle(readable_val)

        # Only want so many training datapoints from the games
        if len(readable_train) > 10000:
            readable_train = readable_train[:10000]

        # Only want so many validation datapoints from the games
        if len(readable_val) > 300:
            readable_val = readable_val[:300]

        print("n Training Samples:", len(readable_train))
        print("k Validation Samples:", len(readable_val))
        print(readable_train[0]["input"])
        

        filename_train = "low_elo_" + str(len(low_elo)) + "_games_training"
        filename_val = "low_elo_" + str(len(low_elo)) + "_games_val"

        export_data_to_jsonl(readable_train, filename_train)
        export_data_to_jsonl(readable_val, filename_val)
        
    except FileNotFoundError:
        print(f"File '{pgn_file_path}' not found.")
    except Exception as e:
        print(f"An error occurred: {e}")