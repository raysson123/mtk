from typing import List, Dict, Optional
from APP.domain.models.deck_model import DeckModel
from APP.domain.models.card_model import CardModel

class PlayerModel:
    def __init__(self, player_id: str, name: str, deck: DeckModel, starting_life: int = 40):
        """
        Representa um jogador sentado à mesa.
        Ele é dono de um Deck, tem uma Mão de cartas, Zonas separadas e Status de Vida.
        """
        self.player_id = player_id
        self.name = name
        self.deck = deck
        
        # =========================================================
        # 1. STATUS DO JOGADOR (Focado em Commander)
        # =========================================================
        self.life: int = starting_life
        self.poison_counters: int = 0
        self.commander_damage: Dict[str, int] = {} 
        self.mana_pool: Dict[str, int] = {"W": 0, "U": 0, "B": 0, "R": 0, "G": 0, "C": 0}
        self.is_alive: bool = True

        # =========================================================
        # 2. ZONAS DE JOGO (Separadas para facilitar o Pygame)
        # =========================================================
        self.hand: List[CardModel] = []
        
        self.battlefield_creatures: List[CardModel] = []
        self.battlefield_lands: List[CardModel] = []
        self.battlefield_other: List[CardModel] = [] # Artefatos, Encantamentos, Planeswalkers
        
        self.graveyard: List[CardModel] = []
        self.exile: List[CardModel] = []
        self.commander_zone: List[CardModel] = [] 

    # =========================================================
    # 3. AÇÕES COM CARTAS
    # =========================================================
    def draw_cards(self, amount: int = 1):
        """Puxa N cartas do grimório para a mão."""
        drawn_cards = []
        for _ in range(amount):
            card = self.deck.comprar_carta()
            if card:
                self.hand.append(card)
                drawn_cards.append(card)
            else:
                self.perder_jogo("Tentou comprar de um grimório vazio (Mill).")
                break
        return drawn_cards

    def discard_card(self, card_index: int):
        """Descarta uma carta da mão e a envia para o cemitério."""
        if 0 <= card_index < len(self.hand):
            card = self.hand.pop(card_index)
            self.graveyard.append(card)
            return card
        return None

    def play_land(self, card_index: int):
        """Desce um terreno da mão direto para a zona de terrenos."""
        if 0 <= card_index < len(self.hand):
            # NOVO: Verificação de segurança usando a propriedade da carta
            if self.hand[card_index].is_land:
                card = self.hand.pop(card_index)
                self.battlefield_lands.append(card)
                return card
            else:
                print(f"[AVISO] A carta não é um Terreno!")
        return None

    def cast_creature(self, card_index: int):
        """Desce uma criatura da mão para a linha de frente."""
        if 0 <= card_index < len(self.hand):
            # NOVO: Verificação de segurança
            if self.hand[card_index].is_creature:
                card = self.hand.pop(card_index)
                self.battlefield_creatures.append(card)
                return card
            else:
                 print(f"[AVISO] A carta não é uma Criatura!")
        return None

    def cast_other(self, card_index: int):
        """Desce artefatos/encantamentos da mão para a zona de suporte."""
        if 0 <= card_index < len(self.hand):
            card = self.hand.pop(card_index)
            self.battlefield_other.append(card)
            return card
        return None

    # =========================================================
    # 4. GESTÃO DE VIDA E COMBATE
    # =========================================================
    def take_damage(self, amount: int):
        """Reduz a vida do jogador e checa eliminação."""
        self.life -= amount
        if self.life <= 0:
            self.perder_jogo("Pontos de vida chegaram a zero.")

    def gain_life(self, amount: int):
        self.life += amount

    def take_commander_damage(self, opponent_id: str, amount: int):
        """Aplica dano de comandante. Se bater 21, é GG."""
        self.take_damage(amount) 
        
        current_cmd_dmg = self.commander_damage.get(opponent_id, 0) + amount
        self.commander_damage[opponent_id] = current_cmd_dmg
        
        if current_cmd_dmg >= 21:
            self.perder_jogo(f"Recebeu 21 pontos de dano do Comandante inimigo ({opponent_id}).")

    def add_poison(self, amount: int = 1):
        """Infectar. 10 = derrota."""
        self.poison_counters += amount
        if self.poison_counters >= 10:
            self.perder_jogo("Acumulou 10 contadores de veneno.")

    def reset_mana_pool(self):
        for color in self.mana_pool:
            self.mana_pool[color] = 0

    def perder_jogo(self, motivo: str):
        if self.is_alive:
            self.is_alive = False
            print(f"[MESA] O jogador {self.name} foi ELIMINADO! Motivo: {motivo}")