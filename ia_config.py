from transformers import pipeline

classificador = pipeline(
    "zero-shot-classification",
    model="facebook/bart-large-mnli",
    device=-1
)

gerador_resposta = pipeline(
    "text-generation",
    model="tiiuae/falcon-7b-instruct",
    device=-1,
    max_new_tokens=120,
    do_sample=False,
    temperature=0.2
)
