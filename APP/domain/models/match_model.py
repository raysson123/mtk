from typing import Dict, List
from APP.domain.models.player import PlayerModel
from APP.domain.models.card import CardModel

class MatchModel:
    def __init__(self, player1: PlayerModel, player2: PlayerModel):
        """Guarda o estado global da partida e gerencia as regras e a Pilha."""
        
        # Dicionário de Players (Sua ideia original - Excelente para buscar por ID)
        self.players: Dict[str, PlayerModel] = {
            player1.player_id: player1,
            player2.player_id: player2
        }
        
        self.current_turn: int = 1
        self.active_player_id: str = player1.player_id
        
        # AS FASES DO SEU CÓDIGO (Oficiais do MTG)
        self.phases = ["UNTAP", "UPKEEP", "DRAW", "MAIN1", "COMBAT", "MAIN2", "END"]
        self.current_phase_index: int = 0
        
        # A PILHA DE MÁGICAS (Stack)
        self.stack: List[CardModel] = []
        
        self.match_is_over: bool = False

    @property
    def phase(self) -> str:
        """Retorna o nome da fase atual em texto (ex: 'MAIN1')."""
        return self.phases[self.current_phase_index]

    def get_active_player(self) -> PlayerModel:
        return self.players[self.active_player_id]

    def get_opponent(self) -> PlayerModel:
        for p_id, p in self.players.items():
            if p_id != self.active_player_id:
                return p
        return None

    def put_on_stack(self, card: CardModel):
        """Coloca uma mágica na pilha."""
        self.stack.append(card)
        print(f"[PILHA] {card.name} foi conjurada e aguarda resposta!")

    def resolve_top_of_stack(self):
        """Resolve a última mágica jogada (LIFO - Last In, First Out)."""
        if self.stack:
            resolved_card = self.stack.pop()
            print(f"[PILHA] Resolvendo: {resolved_card.name}")
            return resolved_card
        return None

    def next_phase(self):
        """Avança para a próxima fase. Se for o fim, passa o turno."""
        if self.match_is_over: return
        
        self.current_phase_index += 1
        
        if self.current_phase_index >= len(self.phases):
            self._pass_turn()

    def _pass_turn(self):
        """Lógica para virar o turno para o oponente."""
        self.current_phase_index = 0
        self.current_turn += 1
        self.stack.clear() # A pilha é limpa à força se algo sobrou
        
        # Inverte o jogador ativo
        self.active_player_id = self.get_opponent().player_id
        
        novo_jogador = self.get_active_player()
        print(f"\n[MESA] --- TURNO {self.current_turn} --- Jogador: {novo_jogador.name}")