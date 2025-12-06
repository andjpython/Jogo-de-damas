"""
========================================
JOGO DE DAMA PROFISSIONAL - BACKEND
Desenvolvido com Flask
========================================
"""

from flask import Flask, jsonify, request, render_template
import random
import os

app = Flask(__name__)

# Constantes
EMPTY = 0
P1 = 1
P2 = 2
P1_KING = 3
P2_KING = 4

class CheckersGame:
    def __init__(self):
        self.board = []
        self.turn = P1
        self.winner = None
        self.player1_name = "Jogador 1"
        self.player2_name = "Jogador 2"
        self.mode = "pvp"  # pvp ou pvc
        self.move_history = []
        self.player1_times = []
        self.player2_times = []
        self.player1_warnings = 0
        self.player2_warnings = 0
        self.game_started = False
        self.initialize_board()

    def initialize_board(self):
        """Inicializa o tabuleiro."""
        self.board = [[EMPTY for _ in range(8)] for _ in range(8)]
        self.turn = P1
        self.winner = None
        self.move_history = []
        self.player1_times = []
        self.player2_times = []
        self.player1_warnings = 0
        self.player2_warnings = 0
        
        for row in range(8):
            for col in range(8):
                if (row + col) % 2 == 1:
                    if row < 3:
                        self.board[row][col] = P2
                    elif row > 4:
                        self.board[row][col] = P1

    def configure_game(self, p1_name, p2_name, mode="pvp"):
        """Configura nomes e modo de jogo."""
        self.player1_name = p1_name if p1_name else "Jogador 1"
        self.player2_name = p2_name if p2_name else ("Romano" if mode == "pvc" else "Jogador 2")
        self.mode = mode
        self.game_started = True

    def get_piece_count(self):
        """Conta peças de cada jogador."""
        p1_count = sum(1 for row in self.board for piece in row if piece in [P1, P1_KING])
        p2_count = sum(1 for row in self.board for piece in row if piece in [P2, P2_KING])
        return p1_count, p2_count

    def get_average_time(self, player):
        """Calcula tempo médio de jogadas."""
        times = self.player1_times if player == P1 else self.player2_times
        return sum(times) / len(times) if times else 0

    def analyze_time_comparison(self, move_time):
        """Analisa tempo comparativo e aplica regras."""
        if self.turn == P1:
            self.player1_times.append(move_time)
        else:
            self.player2_times.append(move_time)

        if len(self.player1_times) < 3 or len(self.player2_times) < 3:
            return None

        avg1 = self.get_average_time(P1)
        avg2 = self.get_average_time(P2)
        
        message = None
        penalty = False

        if avg1 > 0 and avg2 > 0:
            if avg1 > avg2 * 1.5 and self.turn == P1:
                self.player1_warnings += 1
                if self.player1_warnings >= 3:
                    message = f"⚠️ {self.player1_name} está demorando MUITO! Penalidade aplicada!"
                    penalty = True
                    self.player1_warnings = 0
                else:
                    message = f"⚠️ {self.player1_name}, você está demorando mais que {self.player2_name}! Agilize!"
            
            elif avg2 > avg1 * 1.5 and self.turn == P2:
                self.player2_warnings += 1
                if self.player2_warnings >= 3:
                    message = f"⚠️ {self.player2_name} está demorando MUITO! Penalidade aplicada!"
                    penalty = True
                    self.player2_warnings = 0
                else:
                    message = f"⚠️ {self.player2_name}, você está demorando mais que {self.player1_name}! Agilize!"

        return {"message": message, "penalty": penalty}

    def apply_time_penalty(self):
        """Remove uma peça aleatória como penalidade."""
        player_pieces = []
        target = P1 if self.turn == P1 else P2
        
        for row in range(8):
            for col in range(8):
                if self.board[row][col] in [target, target + 2]:
                    player_pieces.append((row, col))
        
        if player_pieces:
            row, col = random.choice(player_pieces)
            self.board[row][col] = EMPTY
            return True
        return False

    def is_piece_of_player(self, piece, player):
        """Verifica se peça pertence ao jogador."""
        if player == P1:
            return piece in [P1, P1_KING]
        return piece in [P2, P2_KING]

    def promote_to_king(self, row, col):
        """Promove peça a dama."""
        piece = self.board[row][col]
        if piece == P1 and row == 0:
            self.board[row][col] = P1_KING
            return True
        elif piece == P2 and row == 7:
            self.board[row][col] = P2_KING
            return True
        return False

    def get_captures(self, row, col):
        """Retorna capturas possíveis."""
        piece = self.board[row][col]
        if piece == EMPTY:
            return []
        
        captures = []
        directions = []
        
        if piece == P1:
            directions = [(-2, -2), (-2, 2)]
        elif piece == P2:
            directions = [(2, -2), (2, 2)]
        else:
            directions = [(-2, -2), (-2, 2), (2, -2), (2, 2)]
        
        for dr, dc in directions:
            new_row, new_col = row + dr, col + dc
            mid_row, mid_col = row + dr // 2, col + dc // 2
            
            if 0 <= new_row < 8 and 0 <= new_col < 8:
                mid_piece = self.board[mid_row][mid_col]
                if (mid_piece != EMPTY and 
                    not self.is_piece_of_player(mid_piece, self.turn) and
                    self.board[new_row][new_col] == EMPTY):
                    captures.append((new_row, new_col, mid_row, mid_col))
        
        return captures

    def get_all_captures_for_player(self):
        """Retorna todas capturas possíveis."""
        all_captures = []
        for row in range(8):
            for col in range(8):
                piece = self.board[row][col]
                if self.is_piece_of_player(piece, self.turn):
                    captures = self.get_captures(row, col)
                    if captures:
                        all_captures.append((row, col, captures))
        return all_captures

    def get_simple_moves(self, row, col):
        """Retorna movimentos simples."""
        piece = self.board[row][col]
        if piece == EMPTY:
            return []
        
        moves = []
        directions = []
        
        if piece == P1:
            directions = [(-1, -1), (-1, 1)]
        elif piece == P2:
            directions = [(1, -1), (1, 1)]
        else:
            directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
        
        for dr, dc in directions:
            new_row, new_col = row + dr, col + dc
            if (0 <= new_row < 8 and 0 <= new_col < 8 and
                self.board[new_row][new_col] == EMPTY):
                moves.append((new_row, new_col))
        
        return moves

    def is_valid_move(self, start_r, start_c, end_r, end_c):
        """Valida movimento."""
        if not (0 <= start_r < 8 and 0 <= start_c < 8 and 
                0 <= end_r < 8 and 0 <= end_c < 8):
            return False, "Posição fora do tabuleiro."

        piece = self.board[start_r][start_c]
        
        if piece == EMPTY:
            return False, "Não há peça na origem."
        
        if not self.is_piece_of_player(piece, self.turn):
            return False, "Esta peça não pertence ao jogador atual."

        if self.board[end_r][end_c] != EMPTY:
            return False, "A casa de destino não está vazia."

        all_captures = self.get_all_captures_for_player()
        row_diff = abs(end_r - start_r)
        col_diff = abs(end_c - start_c)
        
        if row_diff == 2 and col_diff == 2:
            captures = self.get_captures(start_r, start_c)
            for cap_r, cap_c, _, _ in captures:
                if cap_r == end_r and cap_c == end_c:
                    return True, "Captura válida."
            return False, "Captura inválida."
        
        elif row_diff == 1 and col_diff == 1:
            if all_captures:
                return False, "Você deve capturar quando possível!"
            
            simple_moves = self.get_simple_moves(start_r, start_c)
            for move_r, move_c in simple_moves:
                if move_r == end_r and move_c == end_c:
                    return True, "Movimento válido."
            return False, "Movimento inválido."
        
        return False, "Movimento inválido."

    def check_winner(self):
        """Verifica vencedor."""
        p1_pieces = 0
        p2_pieces = 0
        p1_can_move = False
        p2_can_move = False
        
        for row in range(8):
            for col in range(8):
                piece = self.board[row][col]
                if piece in [P1, P1_KING]:
                    p1_pieces += 1
                    if not p1_can_move:
                        if self.get_captures(row, col) or self.get_simple_moves(row, col):
                            p1_can_move = True
                elif piece in [P2, P2_KING]:
                    p2_pieces += 1
                    if not p2_can_move:
                        if self.get_captures(row, col) or self.get_simple_moves(row, col):
                            p2_can_move = True
        
        if p1_pieces == 0 or (self.turn == P1 and not p1_can_move):
            self.winner = self.player2_name
            return True
        elif p2_pieces == 0 or (self.turn == P2 and not p2_can_move):
            self.winner = self.player1_name
            return True
        
        return False

    def move_piece(self, start_r, start_c, end_r, end_c, move_time=0):
        """Executa movimento."""
        valid, message = self.is_valid_move(start_r, start_c, end_r, end_c)
        
        if not valid:
            return False, message, None

        piece = self.board[start_r][start_c]
        self.board[end_r][end_c] = piece
        self.board[start_r][start_c] = EMPTY
        
        row_diff = abs(end_r - start_r)
        captured = False
        if row_diff == 2:
            mid_row = (start_r + end_r) // 2
            mid_col = (start_c + end_c) // 2
            self.board[mid_row][mid_col] = EMPTY
            captured = True
        
        promoted = self.promote_to_king(end_r, end_c)
        
        time_analysis = None
        if move_time > 0:
            time_analysis = self.analyze_time_comparison(move_time)
            if time_analysis and time_analysis["penalty"]:
                self.apply_time_penalty()
        
        can_capture_again = False
        if captured and not promoted:
            next_captures = self.get_captures(end_r, end_c)
            if next_captures:
                can_capture_again = True
        
        if not can_capture_again:
            self.turn = P2 if self.turn == P1 else P1
            self.check_winner()
        
        return True, "Movimento realizado!", time_analysis

    def get_ai_move(self):
        """IA Romano escolhe jogada."""
        all_captures = self.get_all_captures_for_player()
        if all_captures:
            start_r, start_c, captures = random.choice(all_captures)
            end_r, end_c, _, _ = random.choice(captures)
            return start_r, start_c, end_r, end_c
        
        for row in range(8):
            for col in range(8):
                if self.is_piece_of_player(self.board[row][col], self.turn):
                    moves = self.get_simple_moves(row, col)
                    for end_r, end_c in moves:
                        if end_r == 7:
                            return row, col, end_r, end_c
        
        all_moves = []
        for row in range(8):
            for col in range(8):
                if self.is_piece_of_player(self.board[row][col], self.turn):
                    moves = self.get_simple_moves(row, col)
                    for end_r, end_c in moves:
                        all_moves.append((row, col, end_r, end_c))
        
        if all_moves:
            return random.choice(all_moves)
        
        return None

    def surrender(self, player):
        """Jogador desiste."""
        if player == P1:
            self.winner = self.player2_name
        else:
            self.winner = self.player1_name
        return True

    def get_state(self):
        """Retorna estado do jogo."""
        p1_count, p2_count = self.get_piece_count()
        avg1 = self.get_average_time(P1)
        avg2 = self.get_average_time(P2)
        
        return {
            "board": self.board,
            "turn": self.turn,
            "player1_name": self.player1_name,
            "player2_name": self.player2_name,
            "turn_name": self.player1_name if self.turn == P1 else self.player2_name,
            "winner": self.winner,
            "mode": self.mode,
            "p1_pieces": p1_count,
            "p2_pieces": p2_count,
            "p1_avg_time": round(avg1, 1),
            "p2_avg_time": round(avg2, 1),
            "game_started": self.game_started
        }

# Instância global do jogo
game = CheckersGame()

# ========================================
# ROTAS
# ========================================

@app.route('/')
def home():
    """Página principal do jogo."""
    return render_template('index.html')

@app.route('/configure', methods=['POST'])
def configure():
    """Configura o jogo."""
    data = request.get_json()
    game.configure_game(
        data.get('player1_name', 'Jogador 1'),
        data.get('player2_name', 'Jogador 2'),
        data.get('mode', 'pvp')
    )
    return jsonify({"status": "success"})

@app.route('/game-state', methods=['GET'])
def get_game_state():
    """Retorna estado do jogo."""
    return jsonify(game.get_state())

@app.route('/move', methods=['POST'])
def move():
    """Executa um movimento."""
    data = request.get_json()
    
    if not data or not all(k in data for k in ("start_row", "start_col", "end_row", "end_col")):
        return jsonify({"error": "Parâmetros inválidos."}), 400

    try:
        start_r = int(data['start_row'])
        start_c = int(data['start_col'])
        end_r = int(data['end_row'])
        end_c = int(data['end_col'])
        move_time = float(data.get('move_time', 0))
    except ValueError:
        return jsonify({"error": "Os valores devem ser válidos."}), 400

    success, message, time_analysis = game.move_piece(start_r, start_c, end_r, end_c, move_time)

    if success:
        return jsonify({
            "status": "success", 
            "message": message, 
            "game_state": game.get_state(),
            "time_analysis": time_analysis
        }), 200
    else:
        return jsonify({"status": "error", "message": message}), 400

@app.route('/ai-move', methods=['POST'])
def ai_move():
    """IA faz um movimento."""
    if game.mode != 'pvc' or game.turn != P2:
        return jsonify({"error": "Não é a vez da IA."}), 400
    
    ai_move = game.get_ai_move()
    if ai_move:
        start_r, start_c, end_r, end_c = ai_move
        success, message, time_analysis = game.move_piece(start_r, start_c, end_r, end_c, random.uniform(3, 8))
        
        if success:
            return jsonify({"status": "success", "game_state": game.get_state()}), 200
    
    return jsonify({"error": "IA não encontrou movimento válido."}), 400

@app.route('/timeout', methods=['POST'])
def timeout():
    """Passa a vez quando o tempo acaba."""
    game.turn = P2 if game.turn == P1 else P1
    game.check_winner()
    return jsonify({"status": "success", "game_state": game.get_state()})

@app.route('/surrender', methods=['POST'])
def surrender():
    """Jogador desiste."""
    game.surrender(game.turn)
    return jsonify({"status": "success", "game_state": game.get_state()})

@app.route('/reset', methods=['POST'])
def reset_game():
    """Reinicia o jogo."""
    p1_name = game.player1_name
    p2_name = game.player2_name
    mode = game.mode
    
    game.initialize_board()
    game.configure_game(p1_name, p2_name, mode)
    
    return jsonify({"status": "success", "game_state": game.get_state()})

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') == 'development'
    
    print("🎮 Servidor iniciando...")
    print("📁 Estrutura do projeto:")
    print("   ├── app.py (Backend)")
    print("   ├── templates/")
    print("   │   └── index.html")
    print("   └── static/")
    print("       ├── css/style.css")
    print("       ├── js/game.js")
    print("       └── imagens/")
    print("           ├── peça_black_dama.jpg")
    print("           └── peças_red_dama.jpg")
    print(f"\n🚀 Servidor rodando na porta: {port}")
    print("=" * 50)
    
    app.run(debug=debug, host='0.0.0.0', port=port)
