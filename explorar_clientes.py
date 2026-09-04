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

id_alvo = 762707
url = f"{URL_TIFLUX}/clients/{id_alvo}"

print(f"Consultando o ID {id_alvo} no TiFlux...\n")
resposta = requests.get(url, headers=headers)

print(f"Status Code: {resposta.status_code}")
print("Resposta da API:")
print(resposta.text)