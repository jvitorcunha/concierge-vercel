import os
import json
from http.server import BaseHTTPRequestHandler

import google.generativeai as genai

# Configura a chave de API do Gemini usando o ambiente de segredos da Vercel
genai.configure(api_key=os.environ["GEMINI_API_KEY"])

# Inicia o modelo
model = genai.GenerativeModel("gemini-pro")

# O prompt que "ensina" o Gemini sobre a acomodação
prompt_base = """
Você é um concierge online para a acomodação 'Casa de Praia'.
Sua função é responder perguntas dos hóspedes sobre a acomodação, a cidade, e informações úteis de viagem, como a previsão do tempo e dicas de transporte. Responda de forma amigável e direta.
Regras e informações:
- Wi-Fi: Rede "CasaPraia", Senha: "praia123"
- Endereço: Rua da Areia, 45, Praia do Sol.
- Check-in: 14h, Check-out: 12h.
- A lareira só pode ser usada com supervisão. A lenha está na área externa.
- Para ligar a água quente da banheira, gire o botão vermelho.
- Dicas: Restaurantes próximos são "Sabores do Mar" e "Cantinho do Sushi".
- Telefone para emergências: (XX) 9999-9999
Se a pergunta do hóspede não for sobre a acomodação ou sobre a cidade de Gaspar, e você não tiver a resposta, sugira que ele contate o anfitrião.
Pergunta do hóspede:
"""

# A Vercel usa a função handler para lidar com as requisições
def handler(request, response):
    if request.method != 'POST':
        response.set_status(405)
        response.end_with_json({"error": "Method Not Allowed"})
        return

    try:
        body = request.get_json()
        pergunta_do_hospede = body.get("pergunta_do_hospede")
        if not pergunta_do_hospede:
            response.set_status(400)
            response.end_with_json({"error": "No 'pergunta_do_hospede' found"})
            return
    except Exception as e:
        response.set_status(400)
        response.end_with_json({"error": "Invalid JSON"})
        return

    prompt_completo = prompt_base + pergunta_do_hospede

    try:
        gemini_response = model.generate_content(prompt_completo)
        resposta_gemini = gemini_response.text
    except Exception as e:
        resposta_gemini = "Desculpe, não consegui processar a sua pergunta. Tente novamente mais tarde ou contate o anfitrião."
        print(f"Erro na API do Gemini: {e}")

    response.end_with_json({"resposta_do_gemini": resposta_gemini})

# Esta parte é necessária para a Vercel
class MyHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        handler(self, self.wfile)
