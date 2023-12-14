# Description:
# This code updates an existing jsonl dataset produced by data_loader.py
# It resorts legal moves by engine accuracy

import chess
import chess.engine
import json
import re

def get_legal_moves(moves):
    board = chess.Board()
    
    for move in moves:
        try:
            board.push_san(move)
        except ValueError:
            # Handle invalid moves
            return []

    legal_moves = [board.san(move) for move in board.legal_moves]
    return legal_moves

def evaluate_moves(game_sequence, time_per_move=0.5):

    legal_moves = get_legal_moves(game_sequence)

    # Start the simple chess engine
    engine = chess.engine.SimpleEngine.popen_uci(r"D:\DDownloads\stockfish-windows-x86-64-modern\stockfish\stockfish-windows-x86-64-modern.exe")

    # Create the initial board state
    board = chess.Board()
    for sequence in game_sequence:
        try: 
            board.push_san(sequence)
        except:
            continue
    

    move_scores = {}
    for move in legal_moves:
        try:
            # Clone the board to avoid modifying the original
            cloned_board = board.copy()
            cloned_board.push_san(move)
            info = engine.analyse(cloned_board, chess.engine.Limit(time=time_per_move))
            score = info["score"].relative.score()
            if score == None:
                mate_score = info["score"].relative.mate()
                if mate_score != 0:
                    score = (mate_score/abs(mate_score))*3000
                else:
                    score = mate_score
                    
            move_scores[move] = score
        except chess.engine.EngineError:
            # print("EngineError occurred for move", move)
            continue

    # Shut down the chess engine
    engine.quit()

    # Determine if it's Black or White to move
    is_white_to_move = board.turn

    sorted_move_scores = sorted(move_scores.items(), key=lambda x: x[1])

    # Convert the sorted move-score pairs to a string list
    #move_score_strings = [f"{move}:{str(score)}" for move, score in sorted_move_scores]
    move_score_strings = [f"{move}" for move, score in sorted_move_scores]

    return ", ".join(move_score_strings)

def remove_quotes_and_whitespace(move):
    # Function to remove single quotes and leading/trailing whitespace from each move
    return move.strip(" '")

input_file = './Datasets/low_elo_4287_games_val.jsonl'
output_file = './Datasets/low_elo_4287_games_val_engine_nosco.jsonl'
counter = 1 

with open(input_file, 'r') as infile, open(output_file, 'w') as outfile:
    for line in infile:
        data = json.loads(line)
        input_text = data['input']
        output_text = data['output']

        # Extract the 'Game Sequence' section from the input text using a regex
        game_sequence_match = re.search(r"Game Sequence: \[([^\]]*)\]", input_text)
        if game_sequence_match:
            game_sequence_str = game_sequence_match.group(1)
            game_sequence = [remove_quotes_and_whitespace(move) for move in game_sequence_str.split(',')]

            # Extract the 'Legal Moves' section from the input text
            legal_moves_match = re.search(r'Legal Moves: \[.*\]', input_text)
            if legal_moves_match:
                legal_moves = legal_moves_match.group(0)

                # Process the 'Legal Moves' section using your custom function
                modified_legal_moves = evaluate_moves(game_sequence, .05)

                print(counter, ". ", modified_legal_moves)
                counter += 1

                # Replace the original 'Legal Moves' section with the modified one
                input_text = input_text.replace(legal_moves, f'Legal Moves: {modified_legal_moves}')

        # Write the updated entry to the output file
        updated_data = {'input': input_text, 'output': output_text}
        outfile.write(json.dumps(updated_data) + '\n')

print("Processing complete. Updated data saved to output.jsonl.")