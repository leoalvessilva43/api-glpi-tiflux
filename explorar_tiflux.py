import requests

# 1. Lendo credenciais do arquivo txt
credenciais = {}
with open("credenciais.txt", "r") as arquivo:
    for linha in arquivo:
        if "=" in linha:
            chave, valor = linha.split("=", 1)
            credenciais[chave.strip()] = valor.strip()

URL_TIFLUX = credenciais.get("URL_TIFLUX")
TOKEN_TIFLUX = credenciais.get("TOKEN_TIFLUX")

# 2. Configurando o header idêntico ao cURL da documentação
headers = {
    "accept": "application/json",
    "Authorization": f"Bearer {TOKEN_TIFLUX}" 
}

print("Consultando mesas no TiFlux com o filtro correto...\n")

# 3. URL com o parâmetro obrigatório active=true
url_desks = f"{URL_TIFLUX}/desks?active=true"
resposta = requests.get(url_desks, headers=headers)

print(f"Status Code: {resposta.status_code}")
print("Resposta da API:")
print(resposta.text)