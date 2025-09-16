import re
from collections import Counter
from ia_config import classificador, gerador_resposta

#palavras chave para a IA
OFFER_KEYWORDS = {
    "oferta", "venda", "comprar", "consultor", "apresentar", "apresentação",
    "demo", "demonstração", "proposta", "comercial", "promoção", "preço",
    "agendar", "minuto", "contato comercial", "solução"
}
INVOICE_KEYWORDS = {"nota fiscal", "nota_fiscal", "nota", "fatura", "nf", "anexo"}
REPORT_KEYWORDS = {"relatório", "relatorios", "dre", "fechamento", "balanço", "extrato"}
INVITE_KEYWORDS = {"cafe", "café", "almoço", "jantar", "vamos", "encontro", "convite", "tomar um café"}
GREETING_KEYWORDS = {"feliz natal", "feliz ano", "parabéns", "bom trabalho", "obrigado", "grato"}

def preprocess_text(texto: str) -> str:
    if not texto:
        return ""
    texto = re.sub(r"[^A-Za-zÀ-ÖØ-öø-ÿ0-9\s\.,;:\-@/()]", " ", texto)
    texto = re.sub(r"\s+", " ", texto).strip()
    return texto

def contains_any(texto: str, keywords: set) -> bool:
    t = texto.lower()
    for k in keywords:
        if k in t:
            return True
    return False

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
    selected = matches[:max_sentences]
    return " ".join(s.strip() for s in selected).strip()

def is_bad_generated(texto: str) -> bool:
    if not texto or len(texto) < 6:
        return True
    low = texto.lower()
    bad_signs = ["meu amigo", "i am a", "i am", "doctor", "aaa", "..."]
    for s in bad_signs:
        if s in low:
            return True
    tokens = re.findall(r'\w+', low)
    if not tokens:
        return True
    cnt = Counter(tokens)
    if any(v > max(10, len(tokens)//2) for v in cnt.values()):
        return True
    return False

#$ prompt base para gerar respostas
SUGESTOES_RESPOSTA = [
    "Entendido. Vou verificar e retorno em breve.",
    "Obrigado por enviar a nota fiscal. Retornaremos após a análise.",
    "Mensagem recebida. Aguardamos mais detalhes.",
    "Ignorar | Propaganda ou conteúdo irrelevante.",
    "Agradeço o convite, mas não consigo no momento. Podemos combinar em outra ocasião."
]

# prompt com sugestão de resposta
def gerar_prompt_com_sugestoes(email: str) -> str:
    sugestoes = "\n- " + "\n- ".join(SUGESTOES_RESPOSTA)
    return (
        "Responda profissionalmente ao e-mail abaixo com até duas frases. "
        "Use uma linguagem objetiva, educada e clara. "
        "Considere as sugestões abaixo como base, se forem apropriadas ao caso:\n"
        f"{sugestoes}\n\nE-mail: {email}\n\nResposta:"
    )

# resposta para heurística 
TEMPLATES = {
    "invoice": SUGESTOES_RESPOSTA[1],
    "report": SUGESTOES_RESPOSTA[0],
    "invite": SUGESTOES_RESPOSTA[4],
    "offer": SUGESTOES_RESPOSTA[3]
}

def heuristic_category(texto: str):
    low = texto.lower()
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

def analisar_texto(texto: str):
    texto_orig = texto or ""
    texto_limpo = preprocess_text(texto_orig)

    heur_label, heur_sub = heuristic_category(texto_limpo)
    if heur_label:
        classificacao = heur_label
    else:
        try:
            cls_result = classificador(
                sequences=texto_limpo or " ",
                candidate_labels=["Produtivo", "Improdutivo"],
                hypothesis_template="Este e-mail é {}.",
                truncation=True
            )
            top_label = cls_result.get("labels", [None])[0]
            top_score = cls_result.get("scores", [0.0])[0]
            classificacao = top_label or "Indefinido"
        except Exception:
            classificacao = "Indefinido"

    resposta = ""
    if heur_sub in TEMPLATES:
        resposta = TEMPLATES[heur_sub]
    else:
        low = texto_limpo.lower()
        if classificacao == "Improdutivo":
            resposta = SUGESTOES_RESPOSTA[3]
        elif classificacao == "Produtivo":
            try:
                prompt = gerar_prompt_com_sugestoes(texto_orig)
                gen = gerador_resposta(prompt)
                generated = gen[0].get("generated_text", "").strip()
                generated = remove_duplicacoes(generated)
                generated = first_sentences(generated, max_sentences=2)
                if is_bad_generated(generated):
                    resposta = SUGESTOES_RESPOSTA[0]
                else:
                    resposta = generated
            except Exception:
                resposta = SUGESTOES_RESPOSTA[0]
        else:
            resposta = "Mensagem recebida. Se for necessária alguma ação específica, favor detalhar."

    resposta = remove_duplicacoes(resposta).strip()
    resposta = re.sub(r"\s+", " ", resposta)
    if resposta and resposta[-1] not in ".!?":
        resposta += "."

    return classificacao, resposta
