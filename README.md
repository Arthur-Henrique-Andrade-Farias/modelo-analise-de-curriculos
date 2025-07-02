# Modelo análise de currículos

API em FastAPI para análise de currículos com apoio de LLMs (OpenAI) via Langchain.

## Como rodar

1. Crie um arquivo `.env` com o conteúdo:
```
OPENAI_API_KEY=sua_chave_aqui
```

2. Crie um ambiente virtual python. Uma forma é utilizando venv:

```bash
python3 -m venv .venv
```

3. Ative o ambiente virtual python. Utilizando venv:

```bash
source .venv/bin/activate
```

4. Instale as dependências:
```bash
pip install -r requirements.txt
```

5. Rode a aplicação:
```bash
uvicorn app.main:app --reload
```

6. Acesse em `http://localhost:8000/docs` para visualizar a interface Open API, que documenta a API e permite interação via UI.

## Endpoint disponível

### POST `/analisar_curriculo`
Recebe:
- `arquivo_pdf`: arquivo `.pdf` com o currículo
- `contexto_vaga`: descrição da vaga (texto)

Retorna:
- Mensagem de recebimento (a lógica real será implementada no projeto)


## Linting com Black

Para garantir estilo de código consistente, utilize o [Black](https://black.readthedocs.io/en/stable/).

Basta executar este comando smpre que quiser formatar o arquivo (geralmente antes dos commits).

```bash
black .
```
