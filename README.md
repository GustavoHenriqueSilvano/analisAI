# Case Prático AutoU - Automação de Respostas de E-mails

Este projeto é um **case prático da AutoU**, desenvolvido **apenas para estudo**. Não possui caráter comercial e **não deve ser usado comercialmente**.

O objetivo é demonstrar uma solução para **automatizar a leitura, classificação e sugestão de respostas de e-mails corporativos**, liberando tempo da equipe para tarefas que exigem julgamento humano.

---

## Autor

**Gustavo Henrique Silvano**  
Todos os direitos reservados © 2025

---

## Como funciona

- **Heurísticas**: identifica palavras-chave, remetentes internos (`@empresa.com`) e e-mails urgentes.  
- **Modelos de IA via Hugging Face**:
  - Classificação de e-mails: `facebook/bart-large-mnli`
  - Geração de respostas: `tiiuae/falcon-7b-instruct`  

O sistema gera respostas **curtas, objetivas e humanizadas**, evitando respostas robotizadas ou genéricas.

---

## Dependências

- Python 3.9+
- Bibliotecas listadas no `requirements.txt`, incluindo:
  - `transformers`
  - `torch`

Instale todas com:

```bash
pip install -r requirements.txt
