"""
Gerenciador de Salas de Jogo Multiplayer
Gerencia múltiplas partidas simultâneas
"""

import random
import string
from datetime import datetime

# Importar CheckersGame do app.py
# Será importado dinamicamente para evitar dependência circular

class GameRoom:
    """Representa uma sala de jogo."""
    
    def __init__(self, room_id, host_name, host_sid):
        self.room_id = room_id
        self.host_name = host_name
        self.host_sid = host_sid  # Socket ID do host
        self.guest_name = None
        self.guest_sid = None
        self.game = None  # Instância do CheckersGame
        self.created_at = datetime.now()
        self.status = "waiting"  # waiting, playing, finished
        self.player1_sid = None
        self.player2_sid = None

class GameManager:
    """Gerencia todas as salas de jogo."""
    
    def __init__(self):
        self.rooms = {}  # {room_id: GameRoom}
        self.player_rooms = {}  # {socket_id: room_id} - mapeia jogador para sala
    
    def generate_room_id(self):
        """Gera um ID único para a sala."""
        while True:
            room_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
            if room_id not in self.rooms:
                return room_id
    
    def create_room(self, host_name, host_sid):
        """Cria uma nova sala de jogo."""
        room_id = self.generate_room_id()
        room = GameRoom(room_id, host_name, host_sid)
        self.rooms[room_id] = room
        self.player_rooms[host_sid] = room_id
        return room_id
    
    def join_room(self, room_id, guest_name, guest_sid):
        """Adiciona um jogador a uma sala existente."""
        if room_id not in self.rooms:
            return False, "Sala não encontrada!"
        
        room = self.rooms[room_id]
        
        if room.status != "waiting":
            return False, "Sala já está em jogo!"
        
        if room.guest_name:
            return False, "Sala já está cheia!"
        
        room.guest_name = guest_name
        room.guest_sid = guest_sid
        self.player_rooms[guest_sid] = room_id
        room.status = "playing"
        
        return True, "Entrou na sala com sucesso!"
    
    def leave_room(self, socket_id):
        """Remove um jogador de uma sala."""
        if socket_id not in self.player_rooms:
            return None
        
        room_id = self.player_rooms[socket_id]
        if room_id not in self.rooms:
            return None
        
        room = self.rooms[room_id]
        
        # Se o host sair, deleta a sala
        if socket_id == room.host_sid:
            del self.rooms[room_id]
            if room.guest_sid:
                del self.player_rooms[room.guest_sid]
            del self.player_rooms[socket_id]
            return room_id, "host"
        
        # Se o guest sair, apenas remove ele
        elif socket_id == room.guest_sid:
            room.guest_name = None
            room.guest_sid = None
            room.status = "waiting"
            del self.player_rooms[socket_id]
            return room_id, "guest"
        
        return None
    
    def get_room(self, room_id):
        """Retorna uma sala pelo ID."""
        return self.rooms.get(room_id)
    
    def get_room_by_socket(self, socket_id):
        """Retorna a sala de um jogador pelo socket ID."""
        if socket_id not in self.player_rooms:
            return None
        room_id = self.player_rooms[socket_id]
        return self.rooms.get(room_id)
    
    def get_available_rooms(self):
        """Retorna lista de salas disponíveis."""
        available = []
        for room_id, room in self.rooms.items():
            if room.status == "waiting" and not room.guest_name:
                available.append({
                    "room_id": room_id,
                    "host_name": room.host_name,
                    "created_at": room.created_at.isoformat()
                })
        return available
    
    def cleanup_empty_rooms(self):
        """Remove salas vazias antigas (mais de 1 hora)."""
        now = datetime.now()
        to_remove = []
        
        for room_id, room in self.rooms.items():
            if room.status == "waiting" and not room.guest_name:
                delta = now - room.created_at
                if delta.total_seconds() > 3600:  # 1 hora
                    to_remove.append(room_id)
        
        for room_id in to_remove:
            room = self.rooms[room_id]
            if room.host_sid in self.player_rooms:
                del self.player_rooms[room.host_sid]
            del self.rooms[room_id]
    
    def assign_player_sides(self, room):
        """Atribui lados aos jogadores (P1 ou P2)."""
        # Host sempre é P1, Guest sempre é P2
        room.player1_sid = room.host_sid
        room.player2_sid = room.guest_sid
        return room.host_sid, room.guest_sid

