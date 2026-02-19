from APP.domain.models.match_model import MatchModel
from APP.domain.models.player_model import PlayerModel
from APP.domain.services.deck_builder import DeckBuilderService

class MatchController:
    def __init__(self):
        """
        Orquestrador da Partida.
        Recebe os inputs da View (cliques) e repassa as ordens para os Modelos (Regras).
        """
        self.match_model = None
        self.total_players = 2

    def setup_game(self, human_deck_data: dict, nickname: str = "Conjurador"):
        """
        Inicializa a partida usando a fábrica de decks e os modelos de domínio.
        """
        print(f"[CONTROLLER] Preparando mesa para {nickname}...")

        # 1. Fábrica de Decks: Transforma o JSON bruto em objetos CardModel embaralhados
        deck_p1 = DeckBuilderService.build_from_json(human_deck_data)
        
        # Cria o Jogador Humano
        player_1 = PlayerModel(player_id="P1", name=nickname, deck=deck_p1)
        
        # 2. Prepara o Oponente (Bot)
        # Para testes, estamos clonando os dados do deck do humano para o bot
        deck_p2 = DeckBuilderService.build_from_json(human_deck_data)
        player_2 = PlayerModel(player_id="P2", name="Oponente 1", deck=deck_p2)

        # 3. Cria a Mesa de Jogo (MatchModel)
        self.match_model = MatchModel(player1=player_1, player2=player_2)

        # 4. Saque Inicial (Regra do Jogo)
        print("[CONTROLLER] Comprando mãos iniciais (7 cartas)...")
        player_1.draw_cards(7)
        player_2.draw_cards(7)
        
        # Para testes: vamos simular que o bot desceu alguns terrenos e criaturas do nada
        # Só para a sua interface já mostrar coisas do lado dele!
        self._simular_mesa_bot(player_2)

        print(f"[OK] Partida Commander iniciada! Comandante P1: {deck_p1.commander_card.name if deck_p1.commander_card else 'Nenhum'}")

    # =========================================================
    # AÇÕES DO JOGADOR (Gatilhos vindos da MatchView)
    # =========================================================
    def draw_card(self, player_id: str, amount: int = 1):
        """Orquestra a compra de carta."""
        player = self.match_model.players.get(player_id)
        if player:
            player.draw_cards(amount)
            print(f"[AÇÃO] {player.name} comprou {amount} carta(s).")

    def play_land(self, player_id: str, hand_index: int):
        """Orquestra a descida de um terreno."""
        player = self.match_model.players.get(player_id)
        if player:
            card = player.play_land(hand_index)
            if card:
                print(f"[AÇÃO] {player.name} desceu o terreno: {card.name}")

    def cast_creature(self, player_id: str, hand_index: int):
        """Orquestra a conjuração de uma criatura."""
        player = self.match_model.players.get(player_id)
        if player:
            # Futuro: Aqui a gente jogaria a carta na Pilha (Stack) primeiro!
            card = player.cast_creature(hand_index)
            if card:
                print(f"[AÇÃO] {player.name} conjurou a criatura: {card.name}")

    def cast_other(self, player_id: str, hand_index: int):
        """Orquestra a conjuração de artefatos/encantamentos."""
        player = self.match_model.players.get(player_id)
        if player:
            card = player.cast_other(hand_index)
            if card:
                print(f"[AÇÃO] {player.name} conjurou: {card.name}")

    def mudar_vida(self, player_id: str, quantidade: int):
        """Altera a vida de um jogador."""
        player = self.match_model.players.get(player_id)
        if player:
            if quantidade > 0:
                player.gain_life(quantidade)
            else:
                player.take_damage(abs(quantidade))
            print(f"[STATUS] {player.name} agora tem {player.life} PV.")

    # =========================================================
    # FUNÇÃO TEMPORÁRIA DE DEBUG / TESTE VISUAL
    # =========================================================
    def _simular_mesa_bot(self, bot: PlayerModel):
        """Puxa algumas cartas da mão do bot para a mesa só para testar a renderização da View."""
        if len(bot.hand) >= 3:
            bot.battlefield_lands.append(bot.hand.pop())
            bot.battlefield_lands.append(bot.hand.pop())
            bot.battlefield_creatures.append(bot.hand.pop())