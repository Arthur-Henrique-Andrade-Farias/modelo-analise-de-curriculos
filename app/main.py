import os
import io
from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from dotenv import load_dotenv
from typing import List, Optional
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from pypdf import PdfReader
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    raise ValueError("A chave da API da OpenAI não foi encontrada. Verifique seu arquivo .env")

# Extração do currículo
class Educacao(BaseModel):
    instituicao: str = Field(description="Nome da instituição de ensino")
    curso: str = Field(description="Nome do curso ou formação")
    ano_conclusao: Optional[int] = Field(description="Ano de conclusão do curso")

class Experiencia(BaseModel):
    empresa: str = Field(description="Nome da empresa")
    cargo: str = Field(description="Cargo ocupado")
    inicio: Optional[str] = Field(description="Data de início no formato YYYY-MM")
    fim: Optional[str] = Field(description="Data de fim no formato YYYY-MM ou 'Atual'")
    responsabilidades: str = Field(description="Descrição das responsabilidades e conquistas")

class Curriculo(BaseModel):
    """Modelo de dados para estruturar as informações extraídas de um currículo."""
    nome: str = Field(description="Nome completo do candidato")
    email: Optional[str] = Field(description="Email de contato")
    localizacao_inferida: Optional[str] = Field(description="Cidade e Estado de residência mais provável do candidato, inferido a partir da localização da última experiência profissional ou acadêmica. Ex: 'Dourados, MS'")
    linkedin: Optional[str] = Field(description="URL do perfil do LinkedIn")
    educacao: List[Educacao] = Field(description="Lista de formações acadêmicas")
    experiencia_profissional: List[Experiencia] = Field(description="Lista de experiências profissionais")
    habilidades: List[str] = Field(description="Lista de competências técnicas e soft skills")

# Extração informações da vaga
class InfoVaga(BaseModel):
    """Modelo de dados para estruturar as informações extraídas da descrição de uma vaga."""
    cidade: Optional[str] = Field(description="Cidade onde a vaga está localizada. Ex: 'Dourados, MS'")
    modalidade: str = Field(description="Modalidade de trabalho, pode ser 'Presencial', 'Remoto' ou 'Híbrido'.")

class CriterioAvaliacao(BaseModel):
    nota: int = Field(description="Nota de 0 a 10 para este critério.")
    justificativa: str = Field(description="Explicação concisa do porquê a nota foi atribuída.")

class AnaliseDetalhadaVaga(BaseModel):
    aderencia_tecnica: CriterioAvaliacao
    compatibilidade_experiencia: CriterioAvaliacao
    compatibilidade_geografica: CriterioAvaliacao
    alinhamento_educacional: CriterioAvaliacao
    valor_diferenciais: CriterioAvaliacao
    
    score_final_ponderado: int = Field(description="Nota final calculada com base nos pesos de cada critério para a vaga.")
    
    pontos_fortes: List[str] = Field(description="Resumo dos principais pontos positivos do candidato para esta vaga.")
    pontos_de_desenvolvimento: List[str] = Field(description="Resumo dos principais gaps ou pontos de desenvolvimento do candidato para esta vaga.")
    
    perguntas_sugeridas: Optional[List[str]] = Field(description="Perguntas para o candidato sobre informações relevantes que não foram encontradas.")

def extrair_texto_de_pdf(pdf_bytes: bytes) -> str:
    pdf_file = io.BytesIO(pdf_bytes)
    reader = PdfReader(pdf_file)
    texto = ""
    for page in reader.pages:
        texto += page.extract_text() or ""
    return texto

llm = ChatOpenAI(model="gpt-4-turbo", temperature=0.0, api_key=OPENAI_API_KEY)

def processar_curriculo(texto_curriculo: str) -> Curriculo:
    """Usa o LLM para extrair informações estruturadas, incluindo a INFERÊNCIA da localização."""
    structured_llm_extractor = llm.with_structured_output(Curriculo)
    prompt = ChatPromptTemplate.from_messages([
        ("system", """
        Você é um assistente de RH expert em extrair informações de currículos. Sua tarefa mais importante é inferir a localização do candidato.
        Regras de Extração:
        1.  Extraia nome, email, linkedin, educação, experiências e habilidades.
        2.  Para o campo 'localizacao_inferida', analise as cidades das experiências profissionais e da educação mais recentes. Se o currículo mencionar explicitamente uma cidade de residência, use-a. Caso contrário, sua melhor estimativa é a cidade da última atividade profissional ou acadêmica.
        """),
        ("human", "Analise o seguinte currículo e extraia as informações no formato JSON solicitado: \n\n{texto_curriculo}")
    ])
    chain = prompt | structured_llm_extractor
    return chain.invoke({"texto_curriculo": texto_curriculo})

def processar_vaga(contexto_vaga: str) -> InfoVaga:
    """NOVA FUNÇÃO: Usa o LLM para extrair a cidade e a modalidade da descrição da vaga."""
    structured_llm_vaga_extractor = llm.with_structured_output(InfoVaga)
    prompt = ChatPromptTemplate.from_messages([
        ("system", "Você é um especialista em analisar descrições de vagas. Sua tarefa é extrair a cidade e a modalidade de trabalho (Presencial, Remoto ou Híbrido) do texto a seguir."),
        ("human", "Analise a seguinte descrição de vaga e extraia as informações no formato JSON solicitado: \n\n{contexto_vaga}")
    ])
    chain = prompt | structured_llm_vaga_extractor
    return chain.invoke({"contexto_vaga": contexto_vaga})

def analisar_compatibilidade(perfil: Curriculo, info_vaga: InfoVaga, contexto_vaga: str) -> AnaliseDetalhadaVaga:
    """Usa o LLM para realizar a análise comparando dois objetos JSON estruturados."""
    structured_llm_analyzer = llm.with_structured_output(AnaliseDetalhadaVaga)
    analysis_prompt = ChatPromptTemplate.from_messages([
        ("system", """
        Você é um Tech Recruiter sênior realizando uma análise de compatibilidade. Você receberá informações estruturadas do candidato e da vaga.
        O foco principal é a aderência técnica e de experiência.

        **Siga esta Rubrica de Avaliação Detalhada:**

        1.  **aderencia_tecnica:** (Peso Alto) Compare as habilidades técnicas ESSENCIAIS da vaga com o currículo.
        2.  **compatibilidade_experiencia:** (Peso Alto) Avalie o nível e o tipo de experiência.
        3.  **compatibilidade_geografica:** (Fator Eliminatório) Avalie com base nos dados estruturados. Se a modalidade da vaga for 'Remoto', a nota é 10. Se for 'Presencial' ou 'Híbrido', compare a cidade da vaga com a localização inferida do candidato. Se forem diferentes, a nota deve ser 0 ou 1, a menos que o candidato mencione disposição para se mudar. Se a localização do candidato não pôde ser inferida, a nota é 5 e uma pergunta deve ser gerada.
        4.  **alinhamento_educacional:** (Peso Médio) Verifique a relevância da formação.
        5.  **valor_diferenciais:** (Peso Baixo) Pontue com base nos itens listados como 'diferenciais' no texto da vaga.
        
        **Cálculo do Score Final Ponderado:**
        Calcule uma nota final ponderada. A compatibilidade geográfica deve ter um impacto drástico: se a nota for baixa, o score final deve ser muito baixo.

        Finalmente, resuma os pontos fortes, pontos de desenvolvimento e sugira perguntas.
        """),
        ("human", """
        **Descrição Completa da Vaga (para contexto):**
        {contexto_vaga}

        ---
        **Informações Estruturadas da Vaga (JSON):**
        {info_vaga}

        ---
        **Perfil do Candidato (JSON extraído do currículo):**
        {perfil_candidato}
        """)
    ])
    
    chain = analysis_prompt | structured_llm_analyzer
    perfil_json_str = perfil.model_dump_json(indent=2)
    info_vaga_json_str = info_vaga.model_dump_json(indent=2)
    
    return chain.invoke({
        "contexto_vaga": contexto_vaga,
        "info_vaga": info_vaga_json_str,
        "perfil_candidato": perfil_json_str
    })

app = FastAPI(
    title="API de RH Inteligente",
    description="Uma API que extrai e infere dados de currículos e vagas para realizar uma análise de compatibilidade automatizada e inteligente.",
    version="4.0.0"
)

origins = [
    "http://localhost:9000",
    "http://127.0.0.1:9000",
    "http://0.0.0.0:9000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins, 
    allow_credentials=True,
    allow_methods=["*"], 
    allow_headers=["*"], 
)

@app.post("/analisar_curriculo", response_model=AnaliseDetalhadaVaga)
async def analisar_curriculo_endpoint(
    arquivo_pdf: UploadFile = File(..., description="Arquivo de currículo em formato .pdf"), 
    contexto_vaga: str = Form(..., description="Texto completo com a descrição e requisitos da vaga.")
):
    """
    Recebe um currículo em PDF e um contexto de vaga, retorna uma análise completa.
    """
    if arquivo_pdf.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="O arquivo deve ser um PDF.")
    
    try:
        pdf_bytes = await arquivo_pdf.read()
        texto_do_curriculo = extrair_texto_de_pdf(pdf_bytes)
        
        if not texto_do_curriculo.strip():
            raise HTTPException(status_code=400, detail="Não foi possível extrair texto do PDF.")

        perfil_extraido = processar_curriculo(texto_do_curriculo)
        
        info_vaga_extraida = processar_vaga(contexto_vaga)

        analise_final = analisar_compatibilidade(
            perfil=perfil_extraido,
            info_vaga=info_vaga_extraida,
            contexto_vaga=contexto_vaga 
        )
        
        return analise_final

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ocorreu um erro interno: {str(e)}")