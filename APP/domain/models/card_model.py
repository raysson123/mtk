from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Dict

class CardModel(BaseModel):
    """
    Representa uma única carta física na mesa de jogo.
    Mistura os dados imutáveis do banco de dados com o estado mutável da partida.
    """
    
    # CORREÇÃO CRÍTICA: Ignora campos extras do JSON (Ex: artist, layout, id)
    # Evita que o Pydantic quebre o jogo se a Scryfall mandar dados a mais.
    model_config = ConfigDict(extra='ignore')

    # =========================================================
    # 1. DADOS ESTÁTICOS (Vindos do seu JSON local / Scryfall)
    # =========================================================
    name: str
    mana_cost: Optional[str] = ""
    cmc: float = 0.0  
    type_line: Optional[str] = "" # Alterado para Optional para evitar crash em tokens
    oracle_text: Optional[str] = ""
    
    colors: List[str] = Field(default_factory=list)
    color_identity: List[str] = Field(default_factory=list)
    
    power: Optional[str] = None
    toughness: Optional[str] = None
    loyalty: Optional[str] = None
    
    local_image_path: Optional[str] = None

    # =========================================================
    # 2. ESTADO DA PARTIDA (Gameplay Dinâmico)
    # =========================================================
    is_tapped: bool = False
    is_face_down: bool = False
    
    counters: Dict[str, int] = Field(default_factory=dict) 

    # =========================================================
    # 3. MÉTODOS DE AÇÃO (O que a carta sabe fazer na mesa)
    # =========================================================
    def tap(self):
        """Vira a carta (geralmente para atacar ou gerar mana)."""
        if not self.is_tapped:
            self.is_tapped = True
            return True
        return False

    def untap(self):
        """Desvira a carta (geralmente na fase de desvirar)."""
        if self.is_tapped:
            self.is_tapped = False
            return True
        return False

    def add_counter(self, counter_type: str, amount: int = 1):
        """Adiciona marcadores específicos à carta."""
        if counter_type in self.counters:
            self.counters[counter_type] += amount
        else:
            self.counters[counter_type] = amount
            
        # Limpa o marcador se ele zerar ou ficar negativo
        if self.counters[counter_type] <= 0:
            del self.counters[counter_type]

    def remove_all_counters(self):
        """Limpa a carta ao mudar de zona (ex: ir para o cemitério)."""
        self.counters.clear()

    # =========================================================
    # 4. HELPERS INTELIGENTES PARA A INTERFACE (Pygame)
    # =========================================================
    @property
    def is_land(self) -> bool:
        """Verifica se a carta é um terreno. Útil para o PlayerModel separar a zona."""
        return "Land" in (self.type_line or "")

    @property
    def is_creature(self) -> bool:
        """Verifica se a carta é uma criatura."""
        return "Creature" in (self.type_line or "")