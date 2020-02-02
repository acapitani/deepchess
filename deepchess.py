
import sys
import chess
import chess.pgn
from sys import maxsize as infinity

# ------------------------------------------------------------------------
class DeepMove():
    'Node class used for minimax'
    def __init__(self, board):
        self.material_values = {
            chess.KING: 50000,
            chess.QUEEN: 5000,
            chess.ROOK: 900,
            chess.KNIGHT: 500,
            chess.BISHOP: 500,
            chess.PAWN: 10
        }
        self.board = board
        self.turns = int(self.board.fen().split()[5])
        self.children = []

        if self.turns > 15:
            self.create_children(15)
        else:
            self.create_children(100)

        if self.children == []:
            self.value = 0
        else:
            self.value = self.children[0][1]

    def create_children(self, n):
        #self.best_moves = self.get_best_moves(*self.predict_moves())
        self.best_moves = self.get_moves()
        self.children.extend(self.best_moves[:n])

    def predict_moves(self):
        pass
        
    def get_material_scores(self, moves):
        '''Generates material scores found by projecting the outcome
        if a move is made. If a capture is made, the material value goes
        up by the piece captured. If checkmate, the material value goes up
        by the value of the king. If stalemate, the material value goes down
        by 100000.'''
        material_scores = []
        for move in moves:
            material_score = 0
            if self.board.is_capture(move):
                if self.board.is_en_passant(move):
                    captured_piece = chess.PAWN
                else:
                    moved_to = getattr(chess, str(move)[2:4].upper())
                    captured_piece = self.board.piece_at(moved_to).piece_type
                material_score += self.material_values[captured_piece]

            self.board.push(move)
            if self.board.is_checkmate():
                material_score += self.material_values[chess.KING]
            elif self.board.is_stalemate():
                material_score -= 100000
            else:
                material_score += 0
            self.board.pop()
            material_scores.append(material_score)
        return material_scores

    def get_moves(self):
        #legal_moves = [str(legal) for legal in list(self.board.legal_moves)]
        legal_moves = [legal for legal in list(self.board.legal_moves)]
        '''
        legal_moves_numbered = [squares_to_numbers(move)
                                for move in list(self.board.legal_moves)]
        moves_ordered = [chess.Move.from_uci(move) for _, move in
                         sorted(zip(total_uncertainties, legal_moves),
                         key=lambda x: x[0])]

        prediction_scores = [(400-uncertainty) for uncertainty in
                             sorted(total_uncertainties)]
        '''
        #material_scores = self.get_material_scores(moves_ordered)
        material_scores = self.get_material_scores(legal_moves)
        total_scores = [m_score for m_score in material_scores]

        return ([[move, score] for score, move in
                sorted(zip(total_scores, legal_moves),
                       key=lambda x: x[0], reverse=True)])


# ------------------------------------------------------------------------
class DeepChess():
    def __init__(self, computer_color):
        ''' Chess engine.
        move recieved in uci form (i.e. a1b1)
        computer colour as 'w' or 'b'
        '''
        self.side = computer_color
        self.board = chess.Board()
            
    def _minimax(self, node, depth, player, alpha, beta):
        if depth == 0 or node.children == []:
            return [player*node.value]
        if node.children[0] is not None:
            predicted_child = node.children[0][0]

        favourite_child = None
        best_advantage = -1*player*infinity
        for child, current_value in node.children:
            node.board.push(child)
            result = self._minimax(DeepMove(node.board), depth-1, -1*player, alpha, beta)

            opposition_value = result[0]
            advantage_score = player*current_value + opposition_value
            if player == 1:
                if advantage_score > best_advantage:
                    best_advantage = advantage_score
                    favourite_child = child
                    alpha = max(alpha, best_advantage)
                    if beta <= alpha:
                        node.board.pop()
                        break
            elif player == -1:
                if advantage_score < best_advantage:
                    best_advantage = advantage_score
                    favourite_child = child
                    beta = min(beta, best_advantage)
                    if beta <= alpha:
                        node.board.pop()
                        break
            node.board.pop()

        return [best_advantage, favourite_child, predicted_child]

    def evaluate(self):
        '''Takes the result from minimax and returns a dict
        minimax uses depth 1 prior to 15 turns. After 15 turns,
        search depth increases to 3 to allow for checkmating.'''
        self.last_turn = self.board.fen().split()[1]
        self.turns = int(self.board.fen().split()[5])
        
        if self.turns > 15:
            sdepth = 3
        else:
            sdepth = 1

        player = 1
        if self.side == 'b':
            player = -1

        result = self._minimax(DeepMove(board=self.board), depth=sdepth, player=player, alpha=-1*infinity, beta=infinity)
        if len(result)>0:
            self.uci_move = result[1]
            #pick_from = str(self.uci_move)[0:2].upper()
            #pick_to = str(self.uci_move)[2:4].upper()
            #self.move_from_square = int(getattr(chess, pick_from))
            #self.move_to_square = int(getattr(chess, pick_to))

            #output_data['move_from'] = self.move_from_square
            #output_data['move_to'] = self.move_to_square
            self.board.push(self.uci_move)

            print('-----------------------------')
            #print('Output Data: ', output_data)
            print('Best score: ', result[0])
            #print('NN prediction: ', result[2])
            print('-----------------------------')
        else:
            print('parita finita')

# ------------------------------------------------------------------------

def check_game_over(position):
    # todo!!!
    return False

def evaluation(position):
    # todo!!! sommatoria punteggio white - sommatoria punteggio black
    return 0

# initial call
# minimax(current_position, 3, -infinity, infinity, True)
def minimax(position, depth, alpha, beta, maximizing_player):
    if depth==0 or check_game_over(position):
        return evaluation(position)
    if maximizing_player:
        max_eval = -sys.maxsize-1
        for child in position.children:
            eval = minimax(child, depth-1, alpha, beta, False)
            max_eval = max(max_eval, eval)
            alpha = max(alpha, eval)
            if beta<=alpha:
                break
        return max_eval
    else:
        min_eval = sys.maxsize
        for child in position.children:
            eval = minimax(child, depth-1, alpha, beta, True)
            min_eval = min(min_eval, eval)
            beta = min(beta, eval)
            if beta<=alpha:
                break
        return min_eval

def main():
    with open("data/games_1/games_1.pgn") as pgn:
        game_num = 1
        move_tot = 0
        while True:
            g = chess.pgn.read_game(pgn)
            if g==None:
                break
            move_num = 1
            print(g.headers["Event"])
            board = g.board()
            for move in g.mainline_moves():
                board.push(move)
                print("game: {} move: {}".format(game_num, move_num))
                print(board)
                print("\n") 
                move_num += 1
            move_tot += move_num
            game_num += 1
        print("total moves: {}".format(move_tot))
    
if __name__=="__main__":
    main()
