import requests

credenciais = {}
with open("credenciais.txt", "r") as arquivo:
    for linha in arquivo:
        if "=" in linha:
            chave, valor = linha.split("=", 1)
            credenciais[chave.strip()] = valor.strip()

URL_TIFLUX = credenciais.get("URL_TIFLUX")
TOKEN_TIFLUX = credenciais.get("TOKEN_TIFLUX")

headers = {
    "accept": "application/json",
    "Authorization": f"Bearer {TOKEN_TIFLUX}"
}

print("Buscando a Sania na API do TiFlux...\n")

# 1. Tentativa por busca direta via query
url_busca = f"{URL_TIFLUX}/users?name=Sania&limit=50&offset=1"
resposta = requests.get(url_busca, headers=headers)

if resposta.status_code == 200 and len(resposta.json()) > 0:
    for user in resposta.json():
        print(f"🎯 Encontrada! ID: {user.get('id')} | Nome: {user.get('name')} | Email: {user.get('email')}")
else:
    print("Busca por parâmetro não retornou. Varrendo página 2 da listagem geral...")
    # 2. Fallback: buscando a página 2 da listagem
    url_pagina2 = f"{URL_TIFLUX}/users?limit=100&offset=2"
    resp_p2 = requests.get(url_pagina2, headers=headers)
    
    if resp_p2.status_code == 200:
        for user in resp_p2.json():
            if "SANIA" in user.get("name", "").upper() or "SANIA" in user.get("email", "").upper():
                print(f"🎯 Encontrada na Pág 2! ID: {user.get('id')} | Nome: {user.get('name')} | Email: {user.get('email')}")
    else:
        print(f"❌ Erro na consulta: {resp_p2.status_code}")