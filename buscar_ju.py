import requests

credenciais = {}
with open("credenciais.txt", "r") as arquivo:
    for linha in arquivo:
        if "=" in linha:
            chave, valor = linha.split("=", 1)
            credenciais[chave.strip()] = valor.strip()

URL_TIFLUX = credenciais.get("URL_TIFLUX")
TOKEN_TIFLUX = credenciais.get("TOKEN_TIFLUX")
CLIENT_ID = 762707  # SP-CARAGUATATUBA-PM

headers = {
    "accept": "application/json",
    "Authorization": f"Bearer {TOKEN_TIFLUX}"
}

email_busca = "helpdesk@caraguatatuba.sp.gov.br"
print(f"Buscando solicitante pelo e-mail '{email_busca}' no cliente {CLIENT_ID}...\n")

url = f"{URL_TIFLUX}/clients/{CLIENT_ID}/requestors?email={email_busca}"
resposta = requests.get(url, headers=headers)

print(f"Status Code: {resposta.status_code}")
print("Resposta da API:")
print(resposta.text)