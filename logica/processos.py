# logica/processos.py
import re
from collections import Counter
from ia_config import classificador, gerador_resposta

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
    bad_signs = ["meu amigo", "i am a", "i am", "doctor", "aaa", "..." ]
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

TEMPLATES = {
    "invoice": "Obrigado por enviar a nota fiscal. Vou analisar e retorno em breve.",
    "report": "Entendido. Vou verificar os relatórios e retornarei até o prazo solicitado.",
    "invite": "Agradeço o convite, mas não consigo no momento. Podemos combinar em outra ocasião.",
    "offer": "Ignorar | Mensagem de oferta/propaganda. Nenhuma ação necessária."
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
            if top_score < 0.55:
                classificacao = top_label or "Indefinido"
            else:
                classificacao = top_label or "Indefinido"
        except Exception:
            classificacao = "Indefinido"

    resposta = ""
    if heur_sub in TEMPLATES:
        resposta = TEMPLATES[heur_sub]
    else:
        low = texto_limpo.lower()
        if classificacao == "Improdutivo":
            resposta = "Ignorar | Mensagem não relacionada ao trabalho. Nenhuma ação necessária."
        elif classificacao == "Produtivo":
            if contains_any(low, INVOICE_KEYWORDS):
                resposta = TEMPLATES["invoice"]
            elif contains_any(low, REPORT_KEYWORDS):
                resposta = TEMPLATES["report"]
            else:
                prompt = (
                    "Você é assistente virtual de uma equipe financeira que responde emails em português.\n"
                    "Leia o e-mail abaixo e gere UMA resposta curta, correta em português (acentuação correta), "
                    "profissional e objetiva, com no máximo 2 frases. Não repita o conteúdo do e-mail.\n\n"
                    f"E-mail: {texto_orig}\n\nResposta:"
                )
                try:
                    gen = gerador_resposta(
                        prompt,
                        max_new_tokens=60,
                        do_sample=False
                    )
                    generated = gen[0].get("generated_text", "")
                    if generated.startswith(prompt):
                        generated = generated[len(prompt):].strip()
                    generated = remove_duplicacoes(generated).strip()
                    generated = first_sentences(generated, max_sentences=2)
                    if is_bad_generated(generated):
                        resposta = "Entendido. Vou verificar e retorno em breve."
                    else:
                        resposta = generated
                except Exception:
                    resposta = "Entendido. Vou verificar e retorno em breve."
        else:
            resposta = "Mensagem recebida. Se for necessária alguma ação específica, favor detalhar."

    resposta = remove_duplicacoes(resposta).strip()
    resposta = re.sub(r"\s+", " ", resposta) 
    if resposta and resposta[-1] not in ".!?":
        resposta = resposta + "."

    return classificacao, resposta
