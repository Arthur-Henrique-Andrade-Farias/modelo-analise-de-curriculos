from fpdf import FPDF

# --- Dados dos Currículos ---

resumes = {
    "cv_quase_perfeito.pdf": """Nome: Carolina Mendes
Localização: São Paulo, SP
Email: carolina.mendes@email.com
LinkedIn: linkedin.com/in/carolinamendesdev

Resumo: Desenvolvedora Backend Sênior com 8 anos de experiência na construção de sistemas distribuídos robustos e escaláveis para o setor financeiro.

Experiência Profissional:
- Tech Lead, Fintech PagVeloz (São Paulo, SP) | 2021 - Atual
  - Liderança técnica da equipe de microserviços de pagamentos.
  - Arquitetura de novas soluções usando Java 17, Kafka e PostgreSQL.
  - Mentoria de desenvolvedores plenos e juniores.
- Desenvolvedora Backend Sênior, Banco Digital Now (São Paulo, SP) | 2017 - 2021
  - Desenvolvimento de APIs REST para o core bancário usando Java 8 e Oracle.
  - Otimização de queries e performance de serviços críticos.

Educação:
- Bacharelado em Sistemas de Informação, USP (2012-2016)

Habilidades Técnicas: Java (8, 11, 17), Python, SQL, PostgreSQL, Oracle, Kafka, Docker, Kubernetes, AWS, Git.
""",

    "cv_dilema_geo.pdf": """Nome: Ricardo Neves
Localização: Recife, PE
Email: ricardo.neves@email.com

Resumo: Cientista de Dados apaixonado por machine learning, com 3 anos de experiência em modelagem preditiva e análise de dados para o setor de varejo.

Experiência:
- Cientista de Dados, Varejo PontoCom (Recife, PE) | 2022 - Atual
  - Desenvolvimento de modelos de previsão de demanda com Python, Scikit-learn e XGBoost.
  - Criação de dashboards em Power BI para visualização de resultados.

Educação:
- Mestrado em Ciência da Computação (Foco em IA), UFPE (2020-2022)

Habilidades: Python, Pandas, Numpy, Scikit-learn, TensorFlow, Keras, SQL, Power BI.
""",

    "cv_generalista.pdf": """Nome: Fernanda Lima
Localização: Belo Horizonte, MG
Email: fernanda.lima@email.com

Resumo: Desenvolvedora Full-Stack com 4 anos de experiência na criação de aplicações web de ponta a ponta.

Experiência:
- Desenvolvedora Full-Stack, Agência Web Criativa (Belo Horizonte, MG) | 2021 - Atual
  - Criei aplicações web completas usando Python com Django e JavaScript com React.
  - Configurei bancos de dados PostgreSQL e gerenciei pequenos servidores na DigitalOcean com Docker.

Habilidades: Python, Django, JavaScript, React, HTML, CSS, Docker, PostgreSQL.
""",

    "cv_qualquer_local.pdf": """Nome: Bruno Costa
Localização: Curitiba, PR
Email: bruno.costa@email.com

Resumo: Desenvolvedor Backend com 3 anos de experiência em Java.

Experiência:
- Desenvolvedor Java, Consultoria Tech (Curitiba, PR) | 2022 - Atual
  - Manutenção e desenvolvimento de novas features em sistemas legados usando Java e Spring Boot.
  - Análise de requisitos e modelagem de dados com SQL.

Habilidades: Java, Spring Boot, SQL, Git, Microsserviços.
""",

    "cv_transicao_carreira.pdf": """Nome: Sofia Andrade
Localização: Rio de Janeiro, RJ
Email: sofia.andrade.mkt@email.com
LinkedIn: linkedin.com/in/sofiaandrademarketing

Resumo: Profissional de Marketing Digital com 5 anos de experiência em gestão de campanhas, SEO e análise de métricas. Atualmente em transição de carreira para a área de Análise de Dados, com foco em aprender tecnologias relevantes.

Experiência Profissional:
- Analista de Marketing Sênior, E-commerce Brilha (Rio de Janeiro, RJ) | 2020 - Atual
  - Gestão de campanhas de Google Ads e Facebook Ads com foco em performance.
  - Otimização de SEO para blog e páginas de produto, resultando em aumento de 30% no tráfego orgânico.
  - Análise de métricas de engajamento e conversão com Google Analytics.

Educação:
- Bacharelado em Comunicação Social - Publicidade, UFRJ

Habilidades e Interesses em Tecnologia:
- Ferramentas de Marketing: Google Analytics, SEMRush, Google Ads
- Atualmente estudando: Lógica de Programação, Python (básico), SQL (básico).
- Conhecimento em análise de dados de campanhas.
"""
}

def create_pdf(filename, text_content):
    """Cria um arquivo PDF simples a partir de um texto."""
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    
    # Adiciona o texto. O 'multi_cell' lida com quebras de linha automaticamente.
    # Usamos encode/decode para garantir a compatibilidade com caracteres UTF-8.
    pdf.multi_cell(0, 5, text=text_content)
    
    pdf.output(filename)
    print(f"✅ PDF '{filename}' criado com sucesso!")

if __name__ == "__main__":
    print("Gerando arquivos PDF para os casos de teste...")
    for filename, content in resumes.items():
        create_pdf(filename, content)
    print("\nTodos os PDFs foram gerados. Você já pode usá-los para testar a API.")