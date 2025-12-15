"""
========================================
JOGO DE DAMA PROFISSIONAL - BACKEND
Desenvolvido com Flask
========================================
"""

from flask import Flask, jsonify, request, render_template
from flask_socketio import SocketIO, emit, join_room, leave_room
import random
import os
from game_manager import GameManager

app = Flask(__name__)
app.config['SECRET_KEY'] = 'dama-multiplayer-secret-key-2024'
# Configuração SocketIO com ping/pong para manter conexões vivas
socketio = SocketIO(
    app, 
    cors_allowed_origins="*", 
    async_mode='eventlet',
    ping_timeout=60,
    ping_interval=25,
    logger=True,
    engineio_logger=False
)

# Gerenciador de salas multiplayer
game_manager = GameManager()

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
        """
        Inicializa o tabuleiro seguindo as REGRAS BRASILEIRAS OFICIAIS.
        
        Regras de inicialização:
        - Tabuleiro 8x8
        - Peças só ficam em casas escuras (row + col) % 2 == 1
        - P2 (vermelhas/pretas): linhas 0, 1, 2 (3 primeiras linhas)
        - P1 (brancas/vermelhas): linhas 5, 6, 7 (3 últimas linhas)
        - Linhas 3 e 4 ficam vazias (área neutra)
        """
        self.board = [[EMPTY for _ in range(8)] for _ in range(8)]
        self.turn = P1
        self.winner = None
        self.move_history = []
        self.player1_times = []
        self.player2_times = []
        self.player1_warnings = 0
        self.player2_warnings = 0
        
        # Colocar peças nas casas escuras das 3 primeiras e 3 últimas linhas
        for row in range(8):
            for col in range(8):
                if (row + col) % 2 == 1:  # Casa escura
                    if row < 3:
                        self.board[row][col] = P2  # Peças do jogador 2 (topo)
                    elif row > 4:
                        self.board[row][col] = P1  # Peças do jogador 1 (base)

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
        """Analisa tempo comparativo (apenas avisos, sem penalidade)."""
        if self.turn == P1:
            self.player1_times.append(move_time)
        else:
            self.player2_times.append(move_time)

        if len(self.player1_times) < 3 or len(self.player2_times) < 3:
            return None

        avg1 = self.get_average_time(P1)
        avg2 = self.get_average_time(P2)
        
        message = None

        # Apenas avisos informativos, SEM remover peças
        if avg1 > 0 and avg2 > 0:
            if avg1 > avg2 * 1.5 and self.turn == P1:
                self.player1_warnings += 1
                if self.player1_warnings >= 3:
                    message = f"⚠️ {self.player1_name}, você está demorando muito! Agilize!"
                    self.player1_warnings = 0
                else:
                    message = f"💡 {self.player1_name}, tente jogar mais rápido!"
            
            elif avg2 > avg1 * 1.5 and self.turn == P2:
                self.player2_warnings += 1
                if self.player2_warnings >= 3:
                    message = f"⚠️ {self.player2_name}, você está demorando muito! Agilize!"
                    self.player2_warnings = 0
                else:
                    message = f"💡 {self.player2_name}, tente jogar mais rápido!"

        return {"message": message}

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
        """
        Retorna capturas possíveis, incluindo movimento longo de Dama.

        Regras implementadas:
        - Peças normais capturam pulando 2 casas na diagonal (como antes).
        - Damas (P1_KING, P2_KING) podem capturar em QUALQUER distância na mesma
          diagonal, desde que:
            * Haja exatamente 1 peça inimiga no caminho.
            * Todas as casas após o inimigo até o destino estejam vazias.
            * Não haja peça própria bloqueando o caminho.
        """
        piece = self.board[row][col]
        if piece == EMPTY:
            return []

        captures = []

        # Peças normais (não-damas): mesma lógica antiga (2 casas)
        if piece in (P1, P2):
            directions = [(-2, -2), (-2, 2)] if piece == P1 else [(2, -2), (2, 2)]
            for dr, dc in directions:
                new_row, new_col = row + dr, col + dc
                mid_row, mid_col = row + dr // 2, col + dc // 2

                # Verificar limites E casa escura
                if (
                    0 <= new_row < 8 
                    and 0 <= new_col < 8
                    and (new_row + new_col) % 2 == 1  # Casa escura
                ):
                    mid_piece = self.board[mid_row][mid_col]
                    if (
                        mid_piece != EMPTY
                        and not self.is_piece_of_player(mid_piece, self.turn)
                        and self.board[new_row][new_col] == EMPTY
                    ):
                        captures.append((new_row, new_col, mid_row, mid_col))

            return captures

        # DAMAS: podem capturar em qualquer distância na diagonal
        directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]

        for dr, dc in directions:
            r = row + dr
            c = col + dc
            seen_enemy = False
            enemy_pos = None

            while 0 <= r < 8 and 0 <= c < 8:
                # Verificar se é casa escura (peças só podem estar em casas escuras)
                if (r + c) % 2 != 1:
                    # Casa clara - pular (peças não podem estar aqui)
                    r += dr
                    c += dc
                    continue
                
                current_piece = self.board[r][c]

                if current_piece == EMPTY:
                    # Se já vimos exatamente um inimigo antes, qualquer casa vazia ESCURA
                    # depois dele é um destino válido de captura.
                    if seen_enemy and enemy_pos is not None:
                        captures.append((r, c, enemy_pos[0], enemy_pos[1]))
                else:
                    # Encontrou uma peça (em casa escura)
                    if self.is_piece_of_player(current_piece, self.turn):
                        # Peça própria bloqueia o caminho → parar nesta direção
                        break

                    # Peça inimiga
                    if not seen_enemy:
                        seen_enemy = True
                        enemy_pos = (r, c)
                    else:
                        # Já havia inimigo no caminho → duas peças inimigas bloqueiam
                        break

                # Avançar na diagonal (pula casas claras automaticamente)
                r += dr
                c += dc

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
        """
        Retorna movimentos simples (sem captura).

        Regras:
        - Peça normal: 1 casa na diagonal, apenas para frente.
        - Dama: qualquer número de casas na diagonal (frente ou trás),
          até encontrar uma peça ou a borda do tabuleiro.
        - Todas as peças só podem estar em casas escuras (row + col) % 2 == 1
        """
        piece = self.board[row][col]
        if piece == EMPTY:
            return []

        moves = []

        # Peças normais: 1 passo na direção correta
        if piece in (P1, P2):
            if piece == P1:
                directions = [(-1, -1), (-1, 1)]
            else:
                directions = [(1, -1), (1, 1)]

            for dr, dc in directions:
                new_row, new_col = row + dr, col + dc
                # Verificar limites, casa vazia E casa escura
                if (
                    0 <= new_row < 8
                    and 0 <= new_col < 8
                    and (new_row + new_col) % 2 == 1  # Casa escura
                    and self.board[new_row][new_col] == EMPTY
                ):
                    moves.append((new_row, new_col))

            return moves

        # DAMAS: podem andar várias casas na diagonal
        directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]

        for dr, dc in directions:
            r = row + dr
            c = col + dc
            while 0 <= r < 8 and 0 <= c < 8:
                # Verificar se é casa escura (peças só podem estar em casas escuras)
                if (r + c) % 2 == 1:
                    if self.board[r][c] == EMPTY:
                        moves.append((r, c))
                    else:
                        # Qualquer peça (própria ou inimiga) bloqueia a continuidade
                        break
                # Se for casa clara, pular (peças não podem estar aqui)
                # Avançar na diagonal
                r += dr
                c += dc

        return moves

    def is_valid_move(self, start_r, start_c, end_r, end_c):
        """
        Valida movimento seguindo as REGRAS BRASILEIRAS OFICIAIS de damas.
        
        Regras:
        1. Peças só podem estar em casas escuras (row + col) % 2 == 1
        2. Peça normal: move 1 casa na diagonal para frente
        3. Dama: move qualquer número de casas na diagonal (frente ou trás)
        4. Captura é OBRIGATÓRIA se possível
        5. Captura múltipla é obrigatória (deve continuar capturando)
        """
        # Validações básicas
        if not (0 <= start_r < 8 and 0 <= start_c < 8 and 
                0 <= end_r < 8 and 0 <= end_c < 8):
            return False, "Posição fora do tabuleiro."

        # Verificar se destino é casa escura (obrigatório)
        if (end_r + end_c) % 2 != 1:
            return False, "Peças só podem estar em casas escuras."

        piece = self.board[start_r][start_c]
        
        if piece == EMPTY:
            return False, "Não há peça na origem."
        
        if not self.is_piece_of_player(piece, self.turn):
            return False, "Esta peça não pertence ao jogador atual."

        if self.board[end_r][end_c] != EMPTY:
            return False, "A casa de destino não está vazia."

        # Verificar capturas possíveis desta peça específica
        captures_from_piece = self.get_captures(start_r, start_c)
        
        # 1) Verificar se este movimento é uma captura válida desta peça
        for cap_r, cap_c, _, _ in captures_from_piece:
            if cap_r == end_r and cap_c == end_c:
                return True, "Captura válida."

        # 2) REGRA BRASILEIRA: Se esta peça PODE capturar, mas o jogador tentou movimento simples
        # então é inválido (captura obrigatória para esta peça)
        if captures_from_piece:
            return False, "Captura obrigatória! Esta peça deve capturar."

        # 3) Verificar se há capturas possíveis com OUTRAS peças do jogador
        # REGRA BRASILEIRA: Se qualquer peça pode capturar, o jogador DEVE capturar
        all_captures = self.get_all_captures_for_player()
        if all_captures:
            # Se há capturas possíveis, mas esta peça não pode capturar,
            # o jogador deve escolher uma peça que pode capturar
            return False, "Captura obrigatória! Escolha uma peça que pode capturar."

        # 4) Caso não haja capturas obrigatórias, verificar movimento simples
        simple_moves = self.get_simple_moves(start_r, start_c)
        for move_r, move_c in simple_moves:
            if move_r == end_r and move_c == end_c:
                return True, "Movimento válido."

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
            return False, message, None, None

        piece = self.board[start_r][start_c]
        
        # Verificar se é uma captura (antes de mover a peça)
        captured = False
        captured_pos = None
        
        # Buscar nas capturas possíveis para encontrar a posição da peça capturada
        captures = self.get_captures(start_r, start_c)
        for cap_end_r, cap_end_c, enemy_r, enemy_c in captures:
            if cap_end_r == end_r and cap_end_c == end_c:
                captured = True
                captured_pos = (enemy_r, enemy_c)
                break
        
        # Mover a peça
        self.board[end_r][end_c] = piece
        self.board[start_r][start_c] = EMPTY
        
        # Remover a peça capturada (funciona para peças normais E damas)
        if captured and captured_pos:
            enemy_r, enemy_c = captured_pos
            self.board[enemy_r][enemy_c] = EMPTY
        
        # Promover a dama se chegou no final
        promoted = self.promote_to_king(end_r, end_c)
        
        # Análise de tempo (SEM PENALIDADE DE PERDER PEÇA)
        time_analysis = None
        if move_time > 0:
            time_analysis = self.analyze_time_comparison(move_time)
            # REMOVIDO: apply_time_penalty() - era confuso e bugado
        
        # REGRA BRASILEIRA: Verificar se pode capturar novamente (captura múltipla obrigatória)
        can_capture_again = False
        if captured and not promoted:
            next_captures = self.get_captures(end_r, end_c)
            if next_captures:
                can_capture_again = True
                # Não muda o turno - jogador DEVE continuar capturando
                return True, "Captura realizada! Você DEVE continuar capturando.", time_analysis, captured_pos
        
        # Só muda o turno se não houver captura múltipla obrigatória
        if not can_capture_again:
            self.turn = P2 if self.turn == P1 else P1
            self.check_winner()
        
        return True, "Movimento realizado!", time_analysis, captured_pos

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

# Instância global do jogo (para modo local/PvC)
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

    result = game.move_piece(start_r, start_c, end_r, end_c, move_time)
    success = result[0]
    message = result[1]
    time_analysis = result[2]
    captured_pos = result[3] if len(result) > 3 else None

    if success:
        response_data = {
            "status": "success", 
            "message": message, 
            "game_state": game.get_state(),
            "time_analysis": time_analysis
        }
        # Adicionar posição da peça capturada se houver
        if captured_pos:
            response_data["captured_pos"] = {"row": captured_pos[0], "col": captured_pos[1]}
        return jsonify(response_data), 200
    else:
        # Debug: log do erro para identificar problema
        print(f"❌ Movimento inválido: ({start_r},{start_c}) -> ({end_r},{end_c}) | Turno: {game.turn} | Erro: {message}")
        print(f"   Peça na origem: {game.board[start_r][start_c]}")
        print(f"   Capturas possíveis desta peça: {game.get_captures(start_r, start_c)}")
        print(f"   Movimentos simples possíveis: {game.get_simple_moves(start_r, start_c)}")
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

# ========================================
# ROTAS MULTIPLAYER
# ========================================

@app.route('/rooms', methods=['GET'])
def get_rooms():
    """Retorna lista de salas disponíveis."""
    rooms = game_manager.get_available_rooms()
    return jsonify({"rooms": rooms})

# ========================================
# WEBSOCKET EVENTS - MULTIPLAYER
# ========================================

@socketio.on('connect')
def handle_connect():
    """Quando um cliente se conecta."""
    try:
        print(f"✅ Cliente conectado: {request.sid}")
        emit('connected', {'message': 'Conectado ao servidor!'})
    except Exception as e:
        print(f"❌ Erro ao conectar cliente {request.sid}: {str(e)}")

@socketio.on('ping')
def handle_ping():
    """Responde a ping para manter conexão viva."""
    emit('pong')

@socketio.on('disconnect')
def handle_disconnect():
    """Quando um cliente se desconecta."""
    try:
        print(f"❌ Cliente desconectado: {request.sid}")
        result = game_manager.leave_room(request.sid)
        if result:
            room_id, player_type = result
            if player_type == "host":
                # Notificar guest que o host saiu
                room = game_manager.get_room(room_id)
                if room and room.guest_sid:
                    socketio.emit('host_left', {'message': 'O host saiu da sala'}, room=room.guest_sid)
            else:
                # Notificar host que o guest saiu
                room = game_manager.get_room(room_id)
                if room and room.host_sid:
                    socketio.emit('guest_left', {'message': 'O adversário saiu da sala'}, room=room.host_sid)
                    room.status = "waiting"
                    room.guest_name = None
                    room.guest_sid = None
    except Exception as e:
        print(f"❌ Erro ao desconectar cliente {request.sid}: {str(e)}")

@socketio.on('create_room')
def handle_create_room(data):
    """Cria uma nova sala de jogo."""
    try:
        player_name = data.get('player_name', 'Jogador')
        
        if not player_name or len(player_name.strip()) < 2:
            emit('create_room_error', {
                'message': 'Nome inválido! Deve ter pelo menos 2 caracteres.'
            })
            return
        
        # Verificar se o jogador já está em uma sala
        existing_room = game_manager.get_room_by_socket(request.sid)
        if existing_room:
            emit('create_room_error', {
                'message': 'Você já está em uma sala!'
            })
            return
        
        room_id = game_manager.create_room(player_name.strip(), request.sid)
        
        room = game_manager.get_room(room_id)
        if not room:
            emit('create_room_error', {
                'message': 'Erro ao criar sala. Tente novamente.'
            })
            return
        
        room.game = CheckersGame()
        room.game.configure_game(room.host_name, "Aguardando...", "multiplayer")
        
        join_room(room_id)
        emit('room_created', {
            'room_id': room_id,
            'message': f'Sala {room_id} criada com sucesso!'
        })
        
        # Enviar estado inicial
        emit('game_state', room.game.get_state())
        
        print(f"✅ Sala {room_id} criada por {player_name} (SID: {request.sid})")
        
    except Exception as e:
        print(f"❌ Erro ao criar sala: {str(e)}")
        emit('create_room_error', {
            'message': f'Erro ao criar sala: {str(e)}'
        })

@socketio.on('join_room')
def handle_join_room(data):
    """Entra em uma sala existente."""
    room_id = data.get('room_id', '').upper()
    player_name = data.get('player_name', 'Jogador')
    
    success, message = game_manager.join_room(room_id, player_name, request.sid)
    
    if success:
        room = game_manager.get_room(room_id)
        join_room(room_id)
        
        # Configurar o jogo com os nomes dos jogadores
        room.game = CheckersGame()
        room.game.configure_game(room.host_name, room.guest_name, "multiplayer")
        
        # Atribuir lados aos jogadores
        p1_sid, p2_sid = game_manager.assign_player_sides(room)
        
        # Notificar ambos os jogadores
        emit('room_joined', {
            'room_id': room_id,
            'player1_name': room.host_name,
            'player2_name': room.guest_name,
            'your_sid': request.sid,
            'is_player1': request.sid == p1_sid
        })
        
        # Enviar estado do jogo para ambos
        socketio.emit('game_state', room.game.get_state(), room=room_id)
        socketio.emit('game_started', {'message': 'Jogo iniciado!'}, room=room_id)
    else:
        emit('join_error', {'message': message})

@socketio.on('get_rooms')
def handle_get_rooms():
    """Retorna lista de salas disponíveis."""
    rooms = game_manager.get_available_rooms()
    emit('rooms_list', {'rooms': rooms})

@socketio.on('make_move')
def handle_make_move(data):
    """Processa um movimento no jogo multiplayer."""
    room = game_manager.get_room_by_socket(request.sid)
    
    if not room or not room.game:
        emit('move_error', {'message': 'Você não está em uma sala!'})
        return
    
    # Verificar se é a vez do jogador
    is_player1 = request.sid == room.player1_sid
    current_turn = room.game.turn
    
    if (is_player1 and current_turn != P1) or (not is_player1 and current_turn != P2):
        emit('move_error', {'message': 'Não é sua vez!'})
        return
    
    try:
        start_r = int(data['start_row'])
        start_c = int(data['start_col'])
        end_r = int(data['end_row'])
        end_c = int(data['end_col'])
        move_time = float(data.get('move_time', 0))
    except (ValueError, KeyError):
        emit('move_error', {'message': 'Parâmetros inválidos!'})
        return
    
    # Executar movimento
    result = room.game.move_piece(start_r, start_c, end_r, end_c, move_time)
    success = result[0]
    message = result[1]
    time_analysis = result[2]
    captured_pos = result[3] if len(result) > 3 else None
    
    if success:
        response_data = {
            "status": "success",
            "message": message,
            "game_state": room.game.get_state(),
            "time_analysis": time_analysis
        }
        
        if captured_pos:
            response_data["captured_pos"] = {"row": captured_pos[0], "col": captured_pos[1]}
        
        # Enviar para todos na sala
        socketio.emit('move_result', response_data, room=room.room_id)
        
        # Verificar se há vencedor
        if room.game.winner:
            socketio.emit('game_over', {
                'winner': room.game.winner,
                'game_state': room.game.get_state()
            }, room=room.room_id)
            room.status = "finished"
    else:
        emit('move_error', {'message': message})

@socketio.on('surrender')
def handle_surrender():
    """Jogador desiste."""
    room = game_manager.get_room_by_socket(request.sid)
    
    if not room or not room.game:
        emit('error', {'message': 'Você não está em uma sala!'})
        return
    
    is_player1 = request.sid == room.player1_sid
    room.game.surrender(P1 if is_player1 else P2)
    
    socketio.emit('game_over', {
        'winner': room.game.winner,
        'game_state': room.game.get_state()
    }, room=room.room_id)
    
    room.status = "finished"

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') == 'development'
    
    print("🎮 Servidor MULTIPLAYER iniciando...")
    print("📁 Estrutura do projeto:")
    print("   ├── app.py (Backend + WebSocket)")
    print("   ├── game_manager.py (Gerenciador de Salas)")
    print("   ├── templates/")
    print("   │   └── index.html")
    print("   └── static/")
    print("       ├── css/style.css")
    print("       ├── js/game.js")
    print("       └── imagens/")
    print("           ├── peça_black_dama.jpg")
    print("           └── peças_red_dama.jpg")
    print(f"\n🚀 Servidor rodando na porta: {port}")
    print("🌐 Modo MULTIPLAYER ativado!")
    print("=" * 50)
    
    socketio.run(app, debug=debug, host='0.0.0.0', port=port, allow_unsafe_werkzeug=True)
