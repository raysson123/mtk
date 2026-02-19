import pygame
from APP.UI.styles import colors
from APP.UI.styles.fonts import get_fonts
from APP.domain.models.card_model import CardModel

class CardUI:
    def __init__(self, card_model: CardModel, asset_manager, x: int, y: int, w: int = 70, h: int = 100):
        """
        Componente Visual da Carta. 
        Junta a regra de negócio (CardModel) com a renderização (Pygame).
        """
        self.card = card_model
        self.asset_manager = asset_manager
        self.rect = pygame.Rect(x, y, w, h)
        self.fontes = get_fonts()
        
        self.is_hovered = False
        
        # Cache visual próprio do componente
        self._img_surface = None

    def update_position(self, x: int, y: int):
        """Atualiza a posição da carta (Útil para animações ou reorganizar a mão)."""
        self.rect.x = x
        self.rect.y = y

    def update(self, mouse_pos):
        """Checa se o mouse está em cima da carta para dar aquele efeito visual."""
        self.is_hovered = self.rect.collidepoint(mouse_pos)

    def is_clicked(self, event):
        """Verifica se o botão esquerdo do mouse clicou nesta carta."""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            return self.is_hovered
        return False

    def _get_category(self):
        """Helper para a pasta de assets."""
        tipo = self.card.type_line or ""
        if "Creature" in tipo: return "Criaturas"
        if "Land" in tipo: return "Terrenos"
        if "Instant" in tipo: return "Instantes"
        if "Sorcery" in tipo: return "Feiticos"
        if "Enchantment" in tipo: return "Encantamentos"
        if "Artifact" in tipo: return "Artefatos"
        return "Outros"

    def draw(self, screen):
        """Renderiza a carta na tela com todas as firulas visuais."""
        # 1. Tenta carregar a imagem real
        if self._img_surface is None:
            categoria = self._get_category()
            img_bruta = self.asset_manager.get_card_image(self.card.name, category=categoria)
            if img_bruta:
                self._img_surface = pygame.transform.smoothscale(img_bruta, (self.rect.width, self.rect.height))

        # 2. Desenha a Imagem ou o Fallback
        if self._img_surface:
            screen.blit(self._img_surface, self.rect.topleft)
        else:
            # Arte não encontrada no HD
            cor_bg = (150, 200, 150) if self.card.is_land else (200, 200, 180)
            pygame.draw.rect(screen, cor_bg, self.rect, border_radius=4)
            
            txt_nome = self.fontes['status'].render(self.card.name[:8], True, (0, 0, 0))
            screen.blit(txt_nome, (self.rect.x + 2, self.rect.y + 2))

        # 3. Efeito de Carta Virada (Tapped)
        if self.card.is_tapped:
            overlay = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150)) # Escurece a carta
            screen.blit(overlay, self.rect.topleft)
            # Dica visual de que está virada
            txt_tap = self.fontes['status'].render("TAPPED", True, (255, 100, 100))
            screen.blit(txt_tap, (self.rect.centerx - txt_tap.get_width()//2, self.rect.centery))

        # 4. Bordas e Destaques (Hover e Terrenos)
        borda_cor = (0, 0, 0)
        borda_espessura = 1

        if self.is_hovered:
            borda_cor = colors.ACCENT # Brilha quando passa o mouse
            borda_espessura = 3
        elif self.card.is_land:
            borda_cor = (50, 200, 50) # Highlight permanente para terrenos na mão

        pygame.draw.rect(screen, borda_cor, self.rect, borda_espessura, border_radius=4)

        # 5. Marcadores (Counters)
        if self.card.counters:
            cy = self.rect.bottom - 15
            for tipo, qtd in self.card.counters.items():
                pygame.draw.circle(screen, (200, 50, 50), (self.rect.right - 15, cy), 10)
                txt_cnt = self.fontes['status'].render(str(qtd), True, (255, 255, 255))
                screen.blit(txt_cnt, (self.rect.right - 19, cy - 6))
                cy -= 22