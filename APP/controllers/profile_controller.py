# APP/application/controllers/profile_controller.py

class ProfileController:
    def __init__(self, profile_repo):
        """
        Gerencia a lógica de negócio do perfil do usuário.
        :param profile_repo: Instância da infraestrutura (ProfileRepository).
        """
        self.repo = profile_repo
        # Estado interno sincronizado com o repositório
        self.perfil_atual = self.repo.carregar_perfil()

    def carregar_perfil(self):
        """
        Método ponte solicitado pela UI para evitar erro de AttributeError.
        Retorna os dados brutos ou processados do repositório.
        """
        return self.repo.carregar_perfil()

    def verificar_primeiro_acesso(self):
        """
        Verifica se existe um nickname válido configurado no profiler.json.
        """
        # Busca o nickname no perfil carregado
        nickname = self.perfil_atual.get("player_info", {}).get("nickname", "")
        return len(nickname.strip()) >= 3

    def cadastrar_nickname(self, nickname):
        """
        Valida o nome e inicializa o arquivo de perfil físico.
        """
        nome_limpo = nickname.strip()
        
        # Regra de negócio: Mínimo de 3 caracteres para o nome do Conjurador
        if len(nome_limpo) < 3:
            return False, "O nome deve ter pelo menos 3 caracteres."
        
        # Persiste os dados através do repositório
        self.repo.inicializar_perfil_usuario(nome_limpo)
        
        # Recarrega o estado interno para garantir sincronia
        self.perfil_atual = self.repo.carregar_perfil()
        return True, "Perfil criado com sucesso!"

    def obter_nickname(self):
        """Retorna o nickname atualizado para exibição na UI."""
        # Se não houver nome, retorna o padrão do sistema
        return self.perfil_atual.get("player_info", {}).get("nickname", "Conjurador")

    def obter_estatisticas(self):
        """Compila dados de progresso do jogador."""
        info = self.perfil_atual.get("player_info", {})
        # Busca a lista de decks referenciada no índice global
        decks = self.perfil_atual.get("decks_info", {}).get("decks", [])
        
        return {
            "vitorias": info.get("vitorias", 0),
            "total_decks": len(decks),
            "data_criacao": info.get("created_at", "N/A")
        }