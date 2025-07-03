import os
from dotenv import load_dotenv
from typing import List, Optional
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from fpdf import FPDF

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    raise ValueError("A chave da API da OpenAI não foi encontrada. Verifique seu arquivo .env")

class Educacao(BaseModel):
    instituicao: str
    curso: str
    ano_conclusao: Optional[int]

class Experiencia(BaseModel):
    empresa: str
    cargo: str
    inicio: str
    fim: Optional[str]
    responsabilidades: str

class Curriculo(BaseModel):
    nome: str
    email: str
    localizacao_inferida: str
    linkedin: str
    educacao: List[Educacao]
    experiencia_profissional: List[Experiencia]
    habilidades: List[str]


def gerar_perfil_candidato(persona: str) -> Curriculo:
    """
    Usa um LLM para criar um perfil de candidato detalhado e estruturado
    com base em uma persona.
    """
    print(f"🤖 Gerando perfil para a persona: '{persona}'...")
    
    llm_generator = ChatOpenAI(model="gpt-4-turbo", temperature=0.8, api_key=OPENAI_API_KEY)
    structured_llm_generator = llm_generator.with_structured_output(Curriculo)

    prompt = ChatPromptTemplate.from_messages([
        ("system", """
        Você é um criador de personas profissionais e um 'gerador de currículos' criativo.
        Sua tarefa é criar um perfil de candidato detalhado, realista e coerente com base em uma breve descrição (persona).

        REGRAS IMPORTANTES:
        - Invente um nome, email e link do LinkedIn que pareçam realistas.
        - Crie uma linha do tempo lógica para educação e experiência. As datas não devem se sobrepor de forma impossível.
        - Para as responsabilidades, use verbos de ação fortes e inclua 1 ou 2 métricas ou resultados quantificáveis para tornar o currículo mais convincente.
        - As habilidades listadas devem ser consistentes com a experiência e educação descritas.
        - A 'localizacao_inferida' deve ser consistente com a persona solicitada.
        """),
        ("human", "Por favor, crie um perfil de currículo completo para a seguinte persona: '{persona}'")
    ])

    chain = prompt | structured_llm_generator
    perfil_gerado = chain.invoke({"persona": persona})
    print(f"✅ Perfil para '{perfil_gerado.nome}' gerado com sucesso!")
    return perfil_gerado

class PDF(FPDF):
    def header(self):
        pass

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, 'Página ' + str(self.page_no()), 0, 0, 'C')

def criar_pdf_de_curriculo(perfil: Curriculo, filename: str):
    """
    Pega um objeto Curriculo (Pydantic) e cria um arquivo PDF formatado.
    """
    print(f"📄 Criando PDF '{filename}'...")
    pdf = PDF('P', 'mm', 'A4')
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    pdf.set_font('Arial', 'B', 20)
    pdf.cell(0, 10, perfil.nome, 0, 1, 'C')
    pdf.ln(2)

    pdf.set_font('Arial', '', 10)
    contato = f"{perfil.localizacao_inferida} | {perfil.email} | {perfil.linkedin}"
    pdf.cell(0, 10, contato, 0, 1, 'C')
    pdf.ln(8)
    
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, 'Experiência Profissional', 0, 1, 'L')
    pdf.line(pdf.get_x(), pdf.get_y(), pdf.get_x() + 190, pdf.get_y())
    pdf.ln(4)

    pdf.set_font('Arial', '', 11)
    for exp in perfil.experiencia_profissional:
        pdf.set_font('Arial', 'B', 11)
        pdf.cell(0, 7, f"{exp.cargo} - {exp.empresa}", 0, 1, 'L')
        pdf.set_font('Arial', 'I', 10)
        pdf.cell(0, 5, f"{exp.inicio} - {exp.fim or 'Atual'}", 0, 1, 'L')
        pdf.set_font('Arial', '', 11)
        pdf.multi_cell(0, 5, f"- {exp.responsabilidades}")
        pdf.ln(5)

    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, 'Educação', 0, 1, 'L')
    pdf.line(pdf.get_x(), pdf.get_y(), pdf.get_x() + 190, pdf.get_y())
    pdf.ln(4)

    for edu in perfil.educacao:
        pdf.set_font('Arial', 'B', 11)
        pdf.cell(0, 7, edu.instituicao, 0, 1, 'L')
        pdf.set_font('Arial', '', 11)
        pdf.cell(0, 5, f"{edu.curso} (Conclusão: {edu.ano_conclusao or 'N/A'})", 0, 1, 'L')
        pdf.ln(5)
        
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, 'Habilidades', 0, 1, 'L')
    pdf.line(pdf.get_x(), pdf.get_y(), pdf.get_x() + 190, pdf.get_y())
    pdf.ln(4)

    pdf.set_font('Arial', '', 11)
    habilidades_str = ', '.join(perfil.habilidades)
    pdf.multi_cell(0, 7, habilidades_str)

    pdf.output(filename)
    print(f"✅ PDF '{filename}' salvo com sucesso.")


if __name__ == "__main__":
    personas_para_gerar = [
        "Desenvolvedor Mobile Sênior, especialista em Flutter, morador de Campinas, SP.",
        "Cientista de Dados recém-formada, com mestrado em IA e projetos acadêmicos em PNL, de Belo Horizonte, MG.",
        "Profissional de DevOps Pleno em transição de carreira de Administrador de Sistemas, com foco em automação com Terraform e Ansible, de Curitiba, PR.",
        "UX/UI Designer Júnior, com foco em design de aplicativos para o setor de saúde, residente de Salvador, BA."
    ]

    print("🚀 Iniciando o Bot Gerador de Currículos...\n")
    
    for i, persona in enumerate(personas_para_gerar):
        perfil_candidato = gerar_perfil_candidato(persona)
        
        nome_arquivo_pdf = f"curriculo_gerado_{i+1}_{perfil_candidato.nome.split(' ')[0].lower()}.pdf"
        criar_pdf_de_curriculo(perfil_candidato, nome_arquivo_pdf)
        print("-" * 50)
        
    print("\n🏁 Processo finalizado! Todos os currículos foram gerados.")