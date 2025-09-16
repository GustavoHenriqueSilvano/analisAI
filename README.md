# 📬 Case Prático AutoU - Automação de Respostas de E-mails

Este projeto é um **case prático da AutoU**, desenvolvido **apenas para estudo**.  
**Não possui caráter comercial** e **não deve ser usado comercialmente**.

O objetivo é demonstrar uma solução para **automatizar a leitura, classificação e sugestão de respostas de e-mails corporativos**, liberando tempo da equipe para tarefas que exigem julgamento humano.

---

## 👤 Autor

**Gustavo Henrique Silvano**  
Todos os direitos reservados © 2025

---

## ⚙️ Como Funciona

- **Heurísticas**: identifica palavras-chave, remetentes internos (`@empresa.com`) e e-mails urgentes.  
- **Modelos de IA via Hugging Face**:
  - Classificação de e-mails: `facebook/bart-large-mnli`
  - Geração de respostas: `tiiuae/falcon-7b-instruct`

O sistema gera respostas **curtas, objetivas e humanizadas**, evitando respostas robotizadas ou genéricas.

---

## 🛠 Tecnologias Usadas

- **Framework Web:** FastAPI  
- **Servidor ASGI:** Uvicorn  
- **Template Engine:** Jinja2  
- **Processamento de Formulários:** python-multipart  
- **Manipulação de PDFs:** PyPDF2  
- **Processamento de Linguagem Natural (NLP):**
  - Transformers (Hugging Face)
  - SentencePiece
  - PyTorch
  - NumPy
- **Requisições HTTP:** Requests  
- **Gerenciamento de Variáveis de Ambiente:** python-dotenv  
- **Aceleração de Treinamento/Inferência:** Accelerate

---

## 🚀 Instalação e Execução

Siga os passos abaixo para configurar e rodar o projeto localmente:

### Clonando o Repositório e executando

```bash
git clone https://github.com/GustavoHenriqueSilvano/analisAI
cd analisAI

# Criar e ativar o ambiente virtual

python -m venv venv

#windows
.\venv\Scripts\activate  

#macOS/Linux
source venv/bin/activate  

#Instalar dependências

pip install -r requirements.txt

# Executar o projeto

uvicorn main:app --reload  

Com tudo isso, o projeto estará disponível em 👉 http://127.0.0.1:8000


