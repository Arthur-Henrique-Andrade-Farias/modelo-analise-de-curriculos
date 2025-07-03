import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    raise ValueError("A chave da API da OpenAI não foi encontrada. Verifique seu arquivo .env")

def gerar_contexto_vaga(persona_vaga: str, completo: bool = True) -> str:
    """
    Usa um LLM para criar uma descrição de vaga completa ou propositalmente incompleta.
    """
    print(f"🤖 Gerando vaga para a persona: '{persona_vaga}' (Completo: {completo})...")
    
    llm_generator = ChatOpenAI(model="gpt-4o-mini", temperature=0.7, api_key=OPENAI_API_KEY)

    if completo:
        system_prompt = """
        Você é um Gerente de RH / Tech Recruiter escrevendo uma descrição de vaga.
        Sua tarefa é criar uma descrição de vaga COMPLETA e BEM ESTRUTURADA com base na persona fornecida.

        REGRAS IMPORTANTES:
        - O texto DEVE incluir claramente: Nome da Vaga, Nome da Empresa (pode inventar), Localização (Cidade e Estado) e a Modalidade (Presencial, Híbrido ou Remoto).
        - Estruture o texto com seções claras: Descrição da Empresa, Responsabilidades, Requisitos Essenciais e Diferenciais.
        - Seja profissional, claro e atrativo para os candidatos.
        """
    else:
        system_prompt = """
        Você é um Gerente de RH / Tech Recruiter escrevendo uma descrição de vaga.
        Sua tarefa é criar uma descrição de vaga PROPOSITALMENTE INCOMPLETA ou AMBÍGUA, como vemos em muitos sites de emprego.

        REGRAS IMPORTANTES:
        - Você DEVE omitir ou deixar vago pelo menos um dos seguintes itens: Localização ou Modalidade.
        - Os requisitos podem ser genéricos ou usar jargões de startup (ex: "ninja", "rockstar").
        - Exemplos de como fazer isso: Escrever 'local a definir', não mencionar se é remoto, ou listar requisitos vagos como 'conhecimento em programação'.
        """

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", "Por favor, crie uma descrição de vaga para a seguinte persona: '{persona}'")
    ])

    chain = prompt | llm_generator
    vaga_gerada = chain.invoke({"persona": persona_vaga})
    
    return vaga_gerada.content

def salvar_texto_em_arquivo(texto: str, filename: str):
    """Salva um texto em um arquivo .txt."""
    if not os.path.exists("vagas_geradas"):
        os.makedirs("vagas_geradas")
        
    filepath = os.path.join("vagas_geradas", filename)
    
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(texto)
    print(f"✅ Vaga salva com sucesso em: '{filepath}'")


if __name__ == "__main__":
    vagas_para_gerar = [
        {'persona': "Analista de Segurança da Informação Júnior, para uma consultoria em Brasília-DF", 'completo': True},
        {'persona': "Vaga de 'Ninja/Rockstar Developer' para uma startup de fintech, com descrição vaga e empolgada", 'completo': False},
        {'persona': "Engenheiro de Machine Learning Pleno, focado em recomendação para e-commerce, trabalho remoto", 'completo': True},
        {'persona': "Vaga de Gerente de Projetos, mas sem clareza se é para TI ou para outra área da empresa e local a definir", 'completo': False},
        {'persona': "Analista de BI Sênior para uma grande rede de varejo em São Paulo, SP (Híbrido)", 'completo': True}
    ]

    print("🚀 Iniciando o Bot Gerador de Vagas...\n")
    
    for i, vaga_info in enumerate(vagas_para_gerar):
        persona = vaga_info['persona']
        is_completo = vaga_info['completo']
        
        contexto_vaga = gerar_contexto_vaga(persona, completo=is_completo)
        
        tipo = "completa" if is_completo else "incompleta"
        nome_arquivo = f"vaga_{i+1}_{tipo}_{persona.split(' ')[0].lower()}.txt"
        
        salvar_texto_em_arquivo(contexto_vaga, nome_arquivo)
        print("-" * 50)
        
    print("\n🏁 Processo finalizado! Todas as descrições de vagas foram geradas na pasta 'vagas_geradas'.")