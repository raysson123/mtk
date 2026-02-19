import random
from typing import List, Optional
from APP.domain.models.card_model import CardModel

class DeckModel:
    def __init__(self):
        """
        Representa o Grimório (Library) ativo durante a partida.
        Agora ele lida APENAS com objetos CardModel, deixando a leitura
        de JSONs para o DeckBuilderService.
        """
        self.deck_id: Optional[int] = None
        self.name: str = ""
        self.commander_card: Optional[CardModel] = None
        
        # Zonas controladas pelo deck
        self.library: List[CardModel] = []
        self.graveyard: List[CardModel] = []
        self.exile: List[CardModel] = []
        
        self.total_cards_initial: int = 0

    def embaralhar(self):
        """Randomiza a ordem das cartas no grimório (Library)."""
        if self.library:
            random.shuffle(self.library)
            print(f"[MESA] O grimório '{self.name}' foi embaralhado.")

    def comprar_carta(self) -> Optional[CardModel]:
        """
        Puxa a carta do topo do grimório.
        No Python, o final da lista (pop) funciona como o topo do deck.
        """
        if self.library:
            return self.library.pop()
        
        print(f"[AVISO] O grimório de {self.name} está vazio!")
        return None

    def get_tamanho_grimorio(self) -> int:
        """Retorna quantas cartas ainda restam para comprar."""
        return len(self.library)

    def reset(self):
        """Limpa as zonas e recolhe as cartas para iniciar uma nova partida."""
        self.library.clear()
        self.graveyard.clear()
        self.exile.clear()
        self.commander_card = None
        self.name = ""
        self.total_cards_initial = 0