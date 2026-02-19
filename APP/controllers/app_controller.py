import pygame
import sys

# Importação de Controladores e Infraestrutura
from APP.controllers.profile_controller import ProfileController
from APP.controllers.deck_controller import DeckController
from APP.controllers.deck_register_controller import DeckRegisterController 

from APP.infrastructure.storage.deck_repository import DeckRepository
from APP.infrastructure.storage.profile_repository import ProfileRepository
from APP.infrastructure.services.scryfall_service import ScryfallService
from APP.infrastructure.services.image_downloader import ImageDownloader
from APP.domain.models.deck_model import DeckModel

# Importação das Views base
from APP.UI.screens.welcome_ui import WelcomeView
from APP.UI.screens.main_menu_ui import MainMenu
from APP.UI.screens.deck_manager_ui import DeckManagerView

class AppController:
    def __init__(self, screen, profile_repo):
        self.screen = screen
        self.profile_repo = profile_repo
        self.clock = pygame.time.Clock()
        self.running = True

        # 1. Injeção de dependências (Infraestrutura)
        self.deck_repo = DeckRepository()
        self.scryfall = ScryfallService()
        self.downloader = ImageDownloader() # Instância criada aqui
        self.deck_model = DeckModel()

        # 2. Inicialização dos Controladores
        self.profile_ctrl = ProfileController(self.profile_repo)
        
        # Controlador Geral de Decks (Usado no Gerenciador)
        self.deck_ctrl = DeckController(
            self.deck_model, 
            self.deck_repo, 
            self.profile_repo, 
            self.scryfall, 
            self.downloader
        )
        
        # Controlador Especializado em Registro (Rápido via RAM e Batch)
        # CORREÇÃO: Passando o downloader para estruturação offline do deck
        self.deck_register_ctrl = DeckRegisterController(
            self.scryfall, 
            self.deck_repo, 
            self.profile_repo,
            self.downloader # Dependência injetada!
        )

        # Estado inicial
        self.state = "INIT"
        self._definir_tela_inicial()

    def _definir_tela_inicial(self):
        """Define a tela de entrada do 'Machete'."""
        if not self.profile_ctrl.verificar_primeiro_acesso():
            self.state = "WELCOME"
            self.current_screen = WelcomeView(self.screen, self, self.profile_ctrl)
        else:
            self.state = "MENU"
            self.current_screen = MainMenu(self.screen, self.profile_ctrl)

    def run(self):
        """Loop principal - Orquestra o simulador."""
        while self.running:
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    self.running = False

            # Captura a ação da tela atual
            next_action = self.current_screen.handle_events(events)
            
            # Só processa se houver uma ação
            if next_action:
                self._handle_transitions(next_action)

            # Renderização
            self.current_screen.draw()
            pygame.display.flip()
            self.clock.tick(60)

        pygame.quit()
        sys.exit()

    def _handle_transitions(self, action):
        """Gerencia as trocas de tela baseadas em eventos."""
        
        # 1. Voltar ao Menu
        if action == "MENU":
            self.state = "MENU"
            self.current_screen = MainMenu(self.screen, self.profile_ctrl)
        
        # 2. Galeria de Decks (Gerenciador)
        elif action == "DECK_MANAGER" or action == "REGISTER_SUCCESS":
            # Força o recarregamento do profiler.json para atualizar a lista
            if hasattr(self.deck_ctrl, 'reload_data'):
                self.deck_ctrl.reload_data()
            self.state = "DECK_MANAGER"
            # Passa o controlador geral
            self.current_screen = DeckManagerView(self.screen, self, self.deck_ctrl)

        # 3. Cadastro de Decks (Registro)
        elif action == "DECK_REGISTER":
            from APP.UI.screens.deck_register_ui import DeckRegisterView
            
            # Reseta o estado para garantir que os botões apareçam
            self.deck_register_ctrl.estado = "INICIAL"
            self.deck_register_ctrl.progresso = 0
            self.deck_register_ctrl.mensagem_erro = ""
            
            self.state = "DECK_REGISTER"
            # Passa o controlador especializado em registro
            self.current_screen = DeckRegisterView(self.screen, self, self.deck_register_ctrl)

        # 4. Saída segura
        elif action == "QUIT":
            self.running = False