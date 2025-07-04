import os
import requests
import json
import random # Mantido caso queira reativar partes aleatórias no futuro
import time
import glob
import logging

# --- Configurações ---
API_URL = "http://127.0.0.1:8000/analisar_curriculo"
RESUMES_PATH = "resumes/*.pdf"
JOBS_PATH = "jobs/*.txt"
LOG_FILE = "test_run_ordenado.log" # Nome de log diferente para não sobrescrever os testes aleatórios

# --- Configuração do Logger para salvar resultados detalhados ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE, mode='w', encoding='utf-8'),
    ]
)

def run_single_analysis(resume_path: str, job_path: str):
    """
    Executa uma única análise, mede o tempo e retorna os resultados.
    """
    try:
        with open(resume_path, "rb") as f_resume:
            resume_filename = os.path.basename(resume_path)
            files = {'arquivo_pdf': (resume_filename, f_resume, 'application/pdf')}
            
            with open(job_path, "r", encoding="utf-8") as f_job:
                job_context = f_job.read()
                data = {'contexto_vaga': job_context}

            # Medindo o tempo da requisição
            start_time = time.time()
            response = requests.post(API_URL, files=files, data=data, timeout=120)
            end_time = time.time()
            
            response.raise_for_status()
            
            duration = end_time - start_time
            return {
                "success": True,
                "data": response.json(),
                "duration": duration
            }

    except Exception as e:
        # Define start_time aqui para o caso de falha antes da atribuição
        start_time = time.time() if 'start_time' not in locals() else start_time
        return {
            "success": False,
            "error": str(e),
            "duration": time.time() - start_time
        }

def format_and_log_result(test_num, resume, job, result):
    """Formata a saída para o console e para o arquivo de log."""
    
    header = f"===== TESTE ORDENADO #{test_num} ====="
    resume_name = os.path.basename(resume)
    job_name = os.path.basename(job)
    
    # --- Saída para o Console ---
    print(header)
    print(f"📄 Currículo: {resume_name}")
    print(f"🎯 Vaga     : {job_name}")
    
    if result["success"]:
        analysis = result["data"]
        duration = result["duration"]
        
        print(f"⏱️  Tempo da Consulta: {duration:.2f} segundos")
        print(f"🌟 Score Final      : {analysis.get('score_final_ponderado', 'N/A')}/10")
        print("-" * len(header))
        print("📝 Justificativas Resumidas:")
        for key, value in analysis.items():
            if isinstance(value, dict) and 'justificativa' in value:
                criteria_name = key.replace('_', ' ').title()
                print(f"  - {criteria_name:<28}: Nota {value['nota']:<2} | {value['justificativa']}")
        print("\n")
        
        # --- Saída para o Arquivo de Log ---
        log_entry = {
            "test_number": test_num,
            "resume_file": resume_name,
            "job_file": job_name,
            "duration_seconds": duration,
            "full_response": analysis
        }
        logging.info(json.dumps(log_entry, indent=2, ensure_ascii=False))
        
    else:
        error_message = result["error"]
        print(f"❌ ERRO NA EXECUÇÃO: {error_message}\n")
        logging.error(f"Erro no teste #{test_num} ({resume_name} vs {job_name}): {error_message}")


if __name__ == "__main__":
    print("🚀 Iniciando suíte de testes ORDENADOS (1 para 1)...\n")
    
    # 1. Descoberta automática de arquivos
    resumes_list = glob.glob(RESUMES_PATH)
    jobs_list = glob.glob(JOBS_PATH)

    # 2. ORDENAÇÃO DAS LISTAS (Passo crucial para o pareamento)
    resumes_list.sort()
    jobs_list.sort()

    if not resumes_list or not jobs_list:
        print("🚨 ERRO: Não foram encontrados arquivos de currículo (.pdf) ou de vagas (.txt) nas pastas 'test/resumes' e 'test/jobs'.")
        exit()
        
    # Define o número de testes pelo tamanho da menor lista para evitar erros
    num_tests = min(len(resumes_list), len(jobs_list))
    
    print(f"Encontrados {len(resumes_list)} currículos e {len(jobs_list)} vagas.")
    print(f"Iniciando {num_tests} análises em pares ordenados...\n")

    # 3. Execução do loop de testes de forma ordenada
    total_time = 0
    successful_tests = 0
    
    for i in range(num_tests):
        # Pega o i-ésimo currículo e a i-ésima vaga
        resume_path = resumes_list[i]
        job_path = jobs_list[i]
        
        result = run_single_analysis(resume_path, job_path)
        
        # O número do teste agora corresponde ao índice na lista
        format_and_log_result(i + 1, resume_path, job_path, result)
        
        if result["success"]:
            total_time += result["duration"]
            successful_tests += 1

    # 4. Impressão do Sumário Final
    print("=" * 30)
    print("🏁 Suíte de testes finalizada.")
    print("=" * 30)
    print(f"Total de Pares Testados   : {num_tests}")
    print(f"Testes com Sucesso       : {successful_tests}")
    if successful_tests > 0:
        average_time = total_time / successful_tests
        print(f"Tempo Médio por Consulta : {average_time:.2f} segundos")
    print(f"Resultados detalhados foram salvos no arquivo: '{LOG_FILE}'")
    print("=" * 30)