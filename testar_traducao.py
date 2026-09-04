import requests

# 1. TOKENS E CREDENCIAIS
credenciais = {}
with open("credenciais.txt", "r") as arquivo:
    for linha in arquivo:
        if "=" in linha:
            chave, valor = linha.split("=", 1)
            credenciais[chave.strip()] = valor.strip()

URL_BASE = credenciais.get("URL_GLPI")
APP_TOKEN = credenciais.get("APP_TOKEN")
USER_TOKEN = credenciais.get("USER_TOKEN")

URL_TIFLUX = credenciais.get("URL_TIFLUX")
TOKEN_TIFLUX = credenciais.get("TOKEN_TIFLUX")

CLIENTE_TIFLUX_ID = 762707
ID_SOLICITANTE_PADRAO = 3758056  # Ju STII
PRIORITY_ID_PADRAO = 120549      # Prioridade padrão para todas as mesas

ID_TECNICO_LEO = 117180
ID_TECNICO_SANIA = 1019979

# Headers para buscas JSON na API do TiFlux
headers_tiflux_json = {
    "accept": "application/json",
    "Content-Type": "application/json",
    "Authorization": f"Bearer {TOKEN_TIFLUX}"
}

# FUNÇÃO PARA CADASTRAR SOLICITANTE NO TIFLUX CASO NÃO EXISTA
def cadastrar_solicitante_tiflux(nome, email):
    url_criar = f"{URL_TIFLUX}/clients/{CLIENTE_TIFLUX_ID}/users"
    payload = {
        "user": {
            "name": nome if nome != "Desconhecido" else "Solicitante Sem Nome",
            "email": email
        }
    }
    
    resp = requests.post(url_criar, json=payload, headers=headers_tiflux_json)
    if resp.status_code == 201:
        dados = resp.json().get("user", {})
        return dados.get("id"), f"{dados.get('name')} (Cadastrado Automaticamente via API)"
    
    return ID_SOLICITANTE_PADRAO, "Ju STII (Padrão - Falha ao Auto-Cadastrar no TiFlux)"

# BUSCAR SOLICITANTE POR E-MAIL OU AUTO-CADASTRAR
def obter_id_solicitante_tiflux(nome_glpi, email_glpi):
    if not email_glpi:
        return ID_SOLICITANTE_PADRAO, "Ju STII (Padrão - Sem E-mail no GLPI)"
    
    url_busca = f"{URL_TIFLUX}/clients/{CLIENTE_TIFLUX_ID}/requestors?email={email_glpi.strip()}"
    resposta = requests.get(url_busca, headers=headers_tiflux_json)
    
    if resposta.status_code == 200:
        dados = resposta.json()
        
        if isinstance(dados, list) and len(dados) > 0:
            dados_ordenados = sorted(dados, key=lambda x: x.get("id", 0), reverse=True)
            solicitante_mais_recente = dados_ordenados[0]
            return solicitante_mais_recente.get("id"), f"{solicitante_mais_recente.get('name')} (Existente - ID: {solicitante_mais_recente.get('id')})"
            
        elif isinstance(dados, dict) and dados.get("id"):
            return dados.get("id"), f"{dados.get('name')} (Existente via E-mail)"
            
    return cadastrar_solicitante_tiflux(nome_glpi, email_glpi)

# 2. AUTENTICAÇÃO NO GLPI
url_login = f"{URL_BASE}/initSession"
headers_glpi_login = {
    "App-Token": APP_TOKEN,
    "Authorization": f"user_token {USER_TOKEN}"
}

resposta = requests.get(url_login, headers=headers_glpi_login)

if resposta.status_code == 200:
    session_token = resposta.json().get("session_token")
    headers_glpi = {
        "App-Token": APP_TOKEN,
        "Session-Token": session_token
    }

    # 3. ID do chamado para teste
    ID_CHAMADO_TESTE = 27513
    
    print(f"Buscando informações do chamado #{ID_CHAMADO_TESTE} no GLPI...\n")
    resp_ticket = requests.get(f"{URL_BASE}/Ticket/{ID_CHAMADO_TESTE}", headers=headers_glpi)
    
    if resp_ticket.status_code in [200, 206]:
        ticket = resp_ticket.json()

        id_glpi = ticket.get("id")
        titulo_glpi = ticket.get("name")
        descricao_glpi = ticket.get("content")
        prioridade_glpi = ticket.get("priority")
        categoria_glpi = ticket.get("itilcategories_id")
        
        # Extraindo dados e e-mail do solicitante no GLPI
        id_usuario_glpi = ticket.get("users_id_recipient")
        nome_solicitante_glpi = "Desconhecido"
        email_solicitante_glpi = None
        
        if id_usuario_glpi:
            resp_usuario = requests.get(f"{URL_BASE}/User/{id_usuario_glpi}", headers=headers_glpi)
            if resp_usuario.status_code in [200, 206]:
                dados_usuario = resp_usuario.json()
                primeiro_nome = dados_usuario.get("firstname", "")
                sobrenome = dados_usuario.get("realname", "")
                login_usuario = dados_usuario.get("name", "")
                
                email_solicitante_glpi = dados_usuario.get("email")
                
                if primeiro_nome or sobrenome:
                    nome_solicitante_glpi = f"{primeiro_nome} {sobrenome}".strip()
                else:
                    nome_solicitante_glpi = f"Login: {login_usuario}"

        # Mapeamento de Categoria GLPI -> Mesa TiFlux
        def depara_categoria(cat_id):
            if cat_id in range(267, 272):
                return 37963  # ADMINISTRATIVO/RH
            if cat_id in range(272, 277):
                return 37964  # ARRECADAÇÃO
            if cat_id in range(277, 282):
                return 37965  # FINANÇAS
            if cat_id in range(282, 287):
                return 37966  # SUPRIMENTOS
            
            avulsos = {12: 38853, 53: 34260}
            return avulsos.get(cat_id, 34260)

        mesa_tiflux = depara_categoria(categoria_glpi)

        # Regra de Atribuição de Técnico
        def definir_tecnico(id_mesa):
            if id_mesa == 37964:  # ARRECADAÇÃO
                return ID_TECNICO_LEO, "Léo Alves"
            return ID_TECNICO_SANIA, "Sânia Almeida"

        id_tecnico_tiflux, nome_tecnico_tiflux = definir_tecnico(mesa_tiflux)

        # Resolução do Solicitante Final no TiFlux
        id_solicitante_tiflux, info_solicitante_tiflux = obter_id_solicitante_tiflux(
            nome_solicitante_glpi, 
            email_solicitante_glpi
        )

        # De/Para de Prioridades (Formatando texto para colocar dentro da descrição)
        mapa_prioridades = {1: "Baixa", 2: "Média", 3: "Normal", 4: "Alta", 5: "Urgente"}
        prioridade_glpi_texto = mapa_prioridades.get(prioridade_glpi, "Normal")
        
        titulo_tiflux = f"{titulo_glpi} ({id_glpi})"
        cabecalho_personalizado = f"Este chamado tem a prioridade: {prioridade_glpi_texto}<br><br>"
        descricao_tiflux = cabecalho_personalizado + descricao_glpi
        
        # EXIBIÇÃO DO PACOTE TRADUZIDO
        print("=" * 80)
        print(" 📦 PACOTE PRONTO PARA ENVIAR AO TIFLUX")
        print("=" * 80)
        print(f"• Cliente ID:         {CLIENTE_TIFLUX_ID}")
        print(f"• Mesa ID:            {mesa_tiflux}")
        print(f"• Técnico Ref:        {id_tecnico_tiflux} ({nome_tecnico_tiflux})")
        print(f"• Solicitante GLPI:   {nome_solicitante_glpi} <{email_solicitante_glpi}>")
        print(f"• Solicitante TiFlux: {id_solicitante_tiflux} ({info_solicitante_tiflux})")
        print(f"• Priority ID TiFlux: {PRIORITY_ID_PADRAO}")
        print(f"• Título Final:       {titulo_tiflux}")
        print("=" * 80)

        # 4. ENVIO REAL PARA A API DO TIFLUX (Usando Form Data / Multipart)
        headers_post_tiflux = {
            "accept": "application/json",
            "Authorization": f"Bearer {TOKEN_TIFLUX}"
        }

        form_data = {
            "title": titulo_tiflux,
            "description": descricao_tiflux,
            "client_id": str(CLIENTE_TIFLUX_ID),
            "desk_id": str(mesa_tiflux),
            "requestor_id": str(id_solicitante_tiflux),
            "priority_id": str(PRIORITY_ID_PADRAO)
        }

        print("\n🚀 Disparando criação do ticket no TiFlux...")
        url_tickets = f"{URL_TIFLUX}/tickets"
        
        # Enviando via data/files form multipart (compatível com a chamada cURL -F)
        resp_criacao = requests.post(url_tickets, data=form_data, headers=headers_post_tiflux)

        print(f"Status Code da Criação: {resp_criacao.status_code}")
        print("Resposta da API TiFlux:")
        print(resp_criacao.text)
        
    else:
        print(f"❌ Não foi possível encontrar o chamado #{ID_CHAMADO_TESTE}. Código: {resp_ticket.status_code}")
else:
    print("❌ Erro na autenticação com o GLPI.")