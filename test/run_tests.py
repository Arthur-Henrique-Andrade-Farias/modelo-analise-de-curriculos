import os
import requests
import json

API_URL = "http://127.0.0.1:8000/analisar_curriculo"

TEST_CASES = [
    {
        "name": "Caso 1: Candidato Quase Perfeito (Java)",
        "resume_path": "resumes/cv_quase_perfeito.pdf",
        "job_path": "jobs/vaga_java_especialista.txt",
        "expectations": {
            "min_score": 8,
            "geo_score": 10,
            "must_contain_question": "Spring Boot"
        }
    },
    {
        "name": "Caso 2: Dilema Geográfico (Dados)",
        "resume_path": "resumes/cv_dilema_geo.pdf",
        "job_path": "jobs/vaga_dados_presencial.txt",
        "expectations": {
            "max_score": 5,
            "geo_score": 0
        }
    },
    {
        "name": "Caso 3: Generalista vs. Vaga Especialista (Backend)",
        "resume_path": "resumes/cv_generalista.pdf",
        "job_path": "jobs/vaga_backend_especialista.txt",
        "expectations": {
            "max_score": 7,
            "must_contain_dev_point": "FastAPI" 
        }
    },
    {
        "name": "Caso 4: Vaga com Localização Ambígua",
        "resume_path": "resumes/cv_qualquer_local.pdf",
        "job_path": "jobs/cv_qualquer_local.txt", 
        "expectations": {
            "geo_score": 10,
            "must_contain_question": "localidade"
        }
    },
    {
        "name": "Caso 5: Transição de Carreira (Marketing para Dados)",
        "resume_path": "resumes/cv_transicao_carreira.pdf",
        "job_path": "jobs/vaga_dados_junior.txt",
        "expectations": {
            "max_score": 5,
            "must_contain_dev_point": "SQL"
        }
    }
]

def run_test(test_case):
    """Executa um único caso de teste contra a API."""
    print(f"--- Executando Teste: {test_case['name']} ---")
    
    try:
        with open(test_case["resume_path"], "rb") as f_resume:
            resume_filename = os.path.basename(f_resume.name)
            files = {'arquivo_pdf': (resume_filename, f_resume, 'application/pdf')}
        
            with open(test_case["job_path"], "r", encoding="utf-8") as f_job:
                job_context = f_job.read()
                data = {'contexto_vaga': job_context}

            response = requests.post(API_URL, files=files, data=data)
            response.raise_for_status()  
        
        result = response.json()
        
        errors = []
        expectations = test_case["expectations"]

        if "min_score" in expectations and result["score_final_ponderado"] < expectations["min_score"]:
            errors.append(f"Score final {result['score_final_ponderado']} é MENOR que o mínimo esperado de {expectations['min_score']}.")
        
        if "max_score" in expectations and result["score_final_ponderado"] > expectations["max_score"]:
            errors.append(f"Score final {result['score_final_ponderado']} é MAIOR que o máximo esperado de {expectations['max_score']}.")
            
        if "geo_score" in expectations and result["compatibilidade_geografica"]["nota"] != expectations["geo_score"]:
            errors.append(f"Score geográfico {result['compatibilidade_geografica']['nota']} é DIFERENTE do esperado {expectations['geo_score']}.")
            
        if "must_contain_question" in expectations:
            if not any(expectations["must_contain_question"].lower() in q.lower() for q in result.get("perguntas_sugeridas", [])):
                errors.append(f"Nenhuma pergunta sugerida continha o termo esperado '{expectations['must_contain_question']}'.")

        if "must_contain_dev_point" in expectations:
            if not any(expectations["must_contain_dev_point"].lower() in p.lower() for p in result.get("pontos_de_desenvolvimento", [])):
                errors.append(f"Nenhum ponto de desenvolvimento continha o termo esperado '{expectations['must_contain_dev_point']}'.")

        if not errors:
            print(f"✅ PASSOU! (Score Final: {result['score_final_ponderado']})")
        else:
            print(f"❌ FALHOU! (Score Final: {result['score_final_ponderado']})")
            for error in errors:
                print(f"  - {error}")
        
    except FileNotFoundError as e:
        print(f"💥 ERRO CRÍTICO: Arquivo de teste não encontrado! Verifique o caminho: {e.filename}")
    except Exception as e:
        print(f"💥 ERRO CRÍTICO ao executar o teste: {e}")
    
    print("-" * (len(test_case['name']) + 24) + "\n")

if __name__ == "__main__":
    print("🚀 Iniciando suíte de testes do Modelo de Análise de Currículos...\n")
    
    try:
        response = requests.get(API_URL.replace("/analisar_curriculo", "/docs"), timeout=3)
        if response.status_code != 200:
             print(f"🚨 AVISO: A API respondeu com status {response.status_code}. Verifique se ela está funcional.")
    except requests.ConnectionError:
        print("🚨 ERRO: Não foi possível conectar à API em {API_URL.replace('/analisar_curriculo', '')}.")
        print("   Certifique-se de que o servidor FastAPI (uvicorn) está rodando no outro terminal.")
        exit()

    for case in TEST_CASES:
        run_test(case)
    print("🏁 Suíte de testes finalizada.")