import requests

# --- 1. LER CREDENCIAIS ---
credenciais = {}
with open("credenciais.txt", "r") as arquivo:
    for linha in arquivo:
        if "=" in linha:
            chave, valor = linha.split("=", 1)
            credenciais[chave.strip()] = valor.strip()

URL_GLPI = credenciais.get("URL_GLPI")
APP_TOKEN = credenciais.get("APP_TOKEN")
USER_TOKEN = credenciais.get("USER_TOKEN")
URL_TIFLUX = credenciais.get("URL_TIFLUX")
TOKEN_TIFLUX = credenciais.get("TOKEN_TIFLUX")

# --- 2. FUNÇÃO PARA CRIAR CHAMADO NO TIFLUX ---
def criar_chamado_tiflux(titulo, descricao):
    url_criar = f"{URL_TIFLUX}/tickets"
    
    headers_tiflux = {
        "Authorization": f"Bearer {TOKEN_TIFLUX}",
        "Content-Type": "application/json"
    }
    
    # Aqui é onde ocorre a 'tradução'. O formato abaixo depende da 
    # documentação oficial do TiFlux, mas geralmente segue esse padrão:
    dados_chamado = {
        "subject": titulo, # Assunto do chamado
        "description": descricao # Descrição rica (pode conter HTML)
        # Você precisará adicionar outros campos obrigatórios do TiFlux aqui (como client_id, sector_id)
    }
    
    print(f"Enviando '{titulo}' para o TiFlux...")
    resposta = requests.post(url_criar, headers=headers_tiflux, json=dados_chamado)
    
    if resposta.status_code == 201 or resposta.status_code == 200:
        print("✅ Chamado criado no TiFlux com sucesso!")
    else:
        print(f"❌ Erro ao criar no TiFlux: {resposta.status_code}")
        print(resposta.text)

# --- 3. FUNÇÃO PRINCIPAL (Lê GLPI e envia pro TiFlux) ---
def sincronizar_chamados():
    # Autenticação GLPI (como fizemos antes)
    url_login = f"{URL_GLPI}/initSession"
    headers_login = {"App-Token": APP_TOKEN, "Authorization": f"user_token {USER_TOKEN}"}
    
    print("Conectando ao GLPI...")
    resposta_login = requests.get(url_login, headers=headers_login)
    
    if resposta_login.status_code != 200:
        print("Erro no login do GLPI")
        return
        
    session_token = resposta_login.json().get("session_token")
    
    # Busca Tickets
    url_tickets = f"{URL_GLPI}/Ticket"
    headers_tickets = {"App-Token": APP_TOKEN, "Session-Token": session_token}
    
    print("Buscando chamados...")
    resposta_tickets = requests.get(url_tickets, headers=headers_tickets)
    
    if resposta_tickets.status_code == 200:
        chamados_glpi = resposta_tickets.json()
        
        # ATENÇÃO: Pegando só os 2 primeiros para teste! 
        for chamado in chamados_glpi[:2]:
            titulo = chamado.get("name")
            descricao = chamado.get("content")
            
            # Chama a função que envia para o TiFlux
            criar_chamado_tiflux(titulo, descricao)
    else:
        print("Erro ao buscar chamados no GLPI")

# Executa tudo
sincronizar_chamados()