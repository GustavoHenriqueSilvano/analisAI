# main.py
from fastapi import FastAPI, Request, Form, UploadFile, File
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from typing import List, Optional
import io
import PyPDF2

from logica.processos import analisar_texto

app = FastAPI()

templates = Jinja2Templates(directory="templates")
templates.env.globals.update(zip=zip)

app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/analisar", response_class=HTMLResponse)
async def analisar(
    request: Request,
    texto: Optional[str] = Form(None),
    arquivos: Optional[List[UploadFile]] = File(None)
):
    textos = []

    if texto and texto.strip():
        textos.append(texto.strip())

    if arquivos:
        for arq in arquivos:
            filename = (arq.filename or "").lower()
            try:
                data = await arq.read()
            except Exception:
                data = None

            if filename.endswith(".txt"):
                try:
                    conteudo = data.decode("utf-8", errors="ignore")
                    textos.append(conteudo)
                except Exception:
                    textos.append("")
            elif filename.endswith(".pdf"):
                try:
                    bio = io.BytesIO(data)
                    reader = PyPDF2.PdfReader(bio)
                    pages_text = []
                    for p in reader.pages:
                        page_text = p.extract_text()
                        if page_text:
                            pages_text.append(page_text)
                    textos.append("\n".join(pages_text))
                except Exception:
                    textos.append("")

    if not textos:
        return HTMLResponse("Nenhum conteúdo ou arquivo válido para análise.", status_code=400)

    classificacoes = []
    respostas = []

    for t in textos:
        cls, resp = analisar_texto(t)
        classificacoes.append(cls)
        respostas.append(resp)

    return templates.TemplateResponse(
        "resultado.html",
        {
            "request": request,
            "textos": textos,
            "classificacoes": classificacoes,
            "respostas": respostas
        }
    )
