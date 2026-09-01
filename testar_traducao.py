import requests

# 1. Lendo credenciais
credenciais = {}
with open("credenciais.txt", "r") as arquivo:
    for linha in arquivo:
        if "=" in linha:
            chave, valor = linha.split("=", 1)
            credenciais[chave.strip()] = valor.strip()

URL_BASE = credenciais.get("URL_GLPI")
APP_TOKEN = credenciais.get("APP_TOKEN")
USER_TOKEN = credenciais.get("USER_TOKEN")

# 2. Autenticação no GLPI
url_login = f"{URL_BASE}/initSession"
headers = {
    "App-Token": APP_TOKEN,
    "Authorization": f"user_token {USER_TOKEN}"
}

resposta = requests.get(url_login, headers=headers)

if resposta.status_code == 200:
    session_token = resposta.json().get("session_token")
    headers_ticket = {
        "App-Token": APP_TOKEN,
        "Session-Token": session_token
    }

    # 3. Defina aqui o ID do chamado específico que você quer testar
    ID_CHAMADO_TESTE = 27513  # <--- TROQUE PELO ID DO SEU CHAMADO DE TESTE
    
    print(f"Buscando informações do chamado #{ID_CHAMADO_TESTE} no GLPI...\n")
    
    # Buscando o chamado específico
    resp_ticket = requests.get(f"{URL_BASE}/Ticket/{ID_CHAMADO_TESTE}", headers=headers_ticket)
    
    if resp_ticket.status_code in [200, 206]:
        ticket = resp_ticket.json()

        # Extraindo os dados crus do GLPI
        id_glpi = ticket.get("id")
        titulo_glpi = ticket.get("name")
        descricao_glpi = ticket.get("content")
        prioridade_glpi = ticket.get("priority") # Geralmente um número de 1 a 5
        categoria_glpi = ticket.get("itilcategories_id") # ID da categoria
        
        # Buscando o nome do solicitante diretamente pelo ID do recebedor no ticket
        id_usuario_glpi = ticket.get("users_id_recipient")
        solicitante = "Desconhecido"
        
        if id_usuario_glpi:
            resp_detalhes_usuario = requests.get(f"{URL_BASE}/User/{id_usuario_glpi}", headers=headers_ticket)
            if resp_detalhes_usuario.status_code in [200, 206]:
                dados_usuario = resp_detalhes_usuario.json()
                
                # No GLPI, o nome completo costuma vir em 'firstname' (Nome) e 'realname' (Sobrenome)
                primeiro_nome = dados_usuario.get("firstname", "")
                sobrenome = dados_usuario.get("realname", "")
                login_usuario = dados_usuario.get("name", "")
                
                if primeiro_nome or sobrenome:
                    solicitante = f"{primeiro_nome} {sobrenome}"
                else:
                    solicitante = f"Login: {login_usuario} (ID: {id_usuario_glpi})"
        
        # Cliente Fixo conforme sua regra
        cliente_tiflux = "SP-CARAGUATATUBA-PM"
        
        #Mapeando Categorias
        def traduzir_categoria(cat_id):
            if cat_id in range(267, 272):
                return "Administrativo / RH / Transparência"
            
            if cat_id in range(272,277):
                            return "Arrecadação"            

            if cat_id in range(277, 282):
                            return "Finanças"
            
            if cat_id in range(282, 287):
                            return "Suprimentos"
            
            # Dicionário de exceções/avulsos caso precise
            avulsos = {
                12: "Infraestrutura",
                53: "Impressoras"
            }
            return avulsos.get(cat_id, "Suporte Geral")

        mesa_tiflux = traduzir_categoria(categoria_glpi)
        
        # De/Para de Prioridade do GLPI para o TiFlux
        mapa_prioridades = {
            1: "Baixa",
            2: "Média",
            3: "Normal",
            4: "Alta",
            5: "Urgente"
        }
        prioridade_tiflux = mapa_prioridades.get(prioridade_glpi, "Normal")
        
        # Regra do Título: Obrigatoriamente contendo o ID do GLPI
        titulo_tiflux = f"{titulo_glpi} ({id_glpi})"

        # Criando o cabeçalho personalizado com a prioridade
        cabecalho_personalizado = f"Este chamado tem a prioridade: {prioridade_tiflux}<br><br>"
        
        # Juntando o cabeçalho com a descrição original do GLPI
        descricao_tiflux = cabecalho_personalizado + descricao_glpi
        
        # --- 5. IMPRIMINDO O PACOTE PRONTO NO CONSOLE ---
        print("=" * 80)
        print(" 📦 PACOTE PRONTO PARA SER ENVIADO AO TIFLUX (SIMULAÇÃO)")
        print("=" * 80)
        print(f"• Cliente:       {cliente_tiflux}")
        print(f"• Mesa/Serviço:  {mesa_tiflux}")
        print(f"• Solicitante:   {solicitante}")
        print(f"• Prioridade:    {prioridade_tiflux}")
        print(f"• Título Final:  {titulo_tiflux}")
        print(f"• Descrição:     {cabecalho_personalizado}{descricao_glpi}")
        print("=" * 80)
        
    else:
        print(f"❌ Não foi possível encontrar o chamado #{ID_CHAMADO_TESTE}. Código: {resp_ticket.status_code}")
else:
    print("❌ Erro na autenticação com o GLPI.")