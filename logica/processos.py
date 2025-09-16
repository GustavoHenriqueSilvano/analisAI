import re
from collections import Counter
from random import choice
from ia_config import classificador, gerador_resposta

OFFER_KEYWORDS = {"oferta", "venda", "comprar", "consultor", "apresentar", "apresentação", "demo",
                  "demonstração", "proposta", "comercial", "promoção", "preço", "agendar", "minuto",
                  "contato comercial", "solução"}
INVOICE_KEYWORDS = {"nota fiscal", "nota_fiscal", "nota", "fatura", "nf", "anexo"}
REPORT_KEYWORDS = {"relatório", "relatorios", "dre", "fechamento", "balanço", "extrato"}
INVITE_KEYWORDS = {"cafe", "café", "almoço", "jantar", "vamos", "encontro", "convite", "tomar um café"}
GREETING_KEYWORDS = {"feliz natal", "feliz ano", "parabéns", "bom trabalho", "obrigado", "grato"}
REQUEST_KEYWORDS = {"solicitamos", "favor enviar", "precisamos de", "gentileza de", "por favor", "pedimos"}
URGENT_KEYWORDS = {"urgente", "prioridade máxima", "imediato", "favor confirmar", "atencao", "prazo"}

TEMPLATES_VARIADAS = {
    "invoice": ["Recebido, obrigado pelo envio.", "Obrigado, a nota foi recebida e será processada."],
    "report": ["Recebido, obrigado pelo envio.", "Entendido, providenciaremos o relatório solicitado."],
    "invite": ["Agradeço o contato, mas não consigo neste momento, combinamos em outro momento.",
               "Obrigado pelo convite. Não consigo nesta semana, podemos reagendar."],
    "offer": ["Ignorar | Propaganda ou conteúdo irrelevante.",
              "Esta mensagem será ignorada, pois se trata de conteúdo comercial externo."],
    "request": ["Entendido. Irei verificar e retornarei em breve.",
                "Recebido, vou providenciar e retorno em breve.",
                "Obrigado pelo aviso. Estou analisando e logo retorno."],
    "high_priority": ["Recebi sua solicitação e vou verificar imediatamente, retornarei em breve.",
                      "Vou providenciar a análise desta pendência e retorno em instantes.",
                      "Obrigado pelo aviso. Estou verificando e logo retorno."]
}

SUGESTOES_RESPOSTA = [choice(v) for k,v in TEMPLATES_VARIADAS.items()]

def preprocess_text(texto: str) -> str:
    if not texto:
        return ""
    texto = re.sub(r"[^A-Za-zÀ-ÖØ-öø-ÿ0-9\s\.,;:\-@/()]", " ", texto)
    texto = re.sub(r"\s+", " ", texto).strip()
    return texto

def contains_any(texto: str, keywords: set) -> bool:
    t = texto.lower()
    return any(k in t for k in keywords)

def remove_duplicacoes(texto: str) -> str:
    partes = [p.strip() for p in re.split(r'(?<=[.!?])\s+', texto) if p.strip()]
    resultado = []
    for p in partes:
        if not resultado or p.lower() != resultado[-1].lower():
            resultado.append(p)
    return " ".join(resultado)

def first_sentences(texto: str, max_sentences: int = 2) -> str:
    matches = re.findall(r'[^.!?]+[.!?]?', texto)
    if not matches:
        return texto.strip()
    return " ".join(s.strip() for s in matches[:max_sentences]).strip()

def is_bad_generated(texto: str) -> bool:
    if not texto or len(texto) < 6:
        return True
    low = texto.lower()
    bad_signs = ["meu amigo", "i am a", "i am", "doctor", "aaa", "..."]
    if any(s in low for s in bad_signs):
        return True
    tokens = re.findall(r'\w+', low)
    if not tokens:
        return True
    cnt = Counter(tokens)
    if any(v > max(10, len(tokens)//2) for v in cnt.values()):
        return True
    return False

def gerar_prompt_com_sugestoes(email: str, categoria: str = None) -> str:
    categoria_texto = f"Categoria detectada: {categoria}." if categoria else ""
    few_shot = (
        "Exemplo 1:\nE-mail: Prezados, solicito envio do DRE até dia 30/09.\nResposta: Recebi sua solicitação e irei providenciar o envio até a data indicada.\n\n"
        "Exemplo 2:\nE-mail: Bora jantar essa semana?\nResposta: Agradeço o convite, mas não consigo por enquanto, combinamos em outro momento.\n\n"
        "Exemplo 3:\nE-mail: Encaminhamos em anexo a Nota Fiscal referente ao mês de agosto.\nResposta: Recebido, obrigado pelo envio.\n\n"
        "Exemplo 4:\nE-mail: Solicito o agendamento do pagamento abaixo com prioridade máxima.\nResposta: Recebi sua solicitação e vou verificar imediatamente, retornarei em breve.\n\n"
    )
    return (
        f"Você é uma assistente virtual que responde e-mails corporativos de forma profissional e natural. "
        f"O objetivo é gerar uma resposta curta, objetiva e educada, sem parecer robotizada. "
        f"Para e-mails internos da empresa (@empresa.com) ou com urgência, sempre considere como Produtivo "
        f"e responda informando que a solicitação será verificada imediatamente. "
        f"Evite respostas genéricas e adapte ao contexto real do e-mail. {categoria_texto}\n\n"
        f"{few_shot}"
        f"E-mail:\n{email}\n\n"
        f"Responda como se fosse um humano, mantendo cordialidade e clareza, usando até duas frases:\nResposta:"
    )

def heuristic_category(texto: str, remetente: str = ""):
    low = texto.lower()
    remetente = remetente.lower()
    if remetente.endswith("@empresa.com"):
        return "Produtivo", "high_priority"
    if contains_any(low, URGENT_KEYWORDS):
        return "Produtivo", "high_priority"
    if contains_any(low, REQUEST_KEYWORDS):
        return "Produtivo", "request"
    if contains_any(low, OFFER_KEYWORDS):
        return "Improdutivo", "offer"
    if contains_any(low, INVITE_KEYWORDS):
        return "Improdutivo", "invite"
    if contains_any(low, INVOICE_KEYWORDS) or "em anexo" in low or "anexo" in low:
        return "Produtivo", "invoice"
    if contains_any(low, REPORT_KEYWORDS):
        return "Produtivo", "report"
    if contains_any(low, GREETING_KEYWORDS) and len(low.split()) < 6:
        return "Improdutivo", "greeting"
    return None, None

def analisar_texto(texto: str, remetente: str = ""):
    texto_orig = texto or ""
    texto_limpo = preprocess_text(texto_orig)
    heur_label, heur_sub = heuristic_category(texto_limpo, remetente=remetente)
    classificacao = heur_label or None
    resposta = ""
    if heur_sub in TEMPLATES_VARIADAS:
        resposta = choice(TEMPLATES_VARIADAS[heur_sub])
    else:
        if classificacao == "Improdutivo":
            resposta = choice(TEMPLATES_VARIADAS.get("offer", SUGESTOES_RESPOSTA))
        elif classificacao == "Produtivo":
            try:
                prompt = gerar_prompt_com_sugestoes(texto_orig, categoria=classificacao)
                gen = gerador_resposta(prompt)
                generated = gen[0].get("generated_text", "").strip()
                generated = remove_duplicacoes(generated)
                generated = first_sentences(generated, max_sentences=2)
                if is_bad_generated(generated):
                    resposta = choice(TEMPLATES_VARIADAS.get("request", SUGESTOES_RESPOSTA))
                else:
                    resposta = generated
            except Exception:
                resposta = choice(TEMPLATES_VARIADAS.get("request", SUGESTOES_RESPOSTA))
        else:
            resposta = "Mensagem recebida. Se for necessária alguma ação específica, favor detalhar."
    resposta = remove_duplicacoes(resposta).strip()
    resposta = re.sub(r"\s+", " ", resposta)
    if resposta and resposta[-1] not in ".!?":
        resposta += "."
    return classificacao or "Indefinido", resposta
