import os
import requests
import json
import time
import logging

# --- Configurações ---
API_URL = "http://127.0.0.1:8000/analisar_curriculo"
LOG_FILE = "rerun_failures.log"

# --- Configuração do Logger ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE, mode='w', encoding='utf-8'),
    ]
)

# ==============================================================================
# LISTA APENAS DOS TESTES QUE RETORNARAM ERRO 500 NOS SEUS LOGS
# ==============================================================================
FAILED_TEST_CASES = [
    {
        "name": "Re-teste #17",
        "resume_path": "resumes/curriculo_gerado_22_luiz.pdf",
        "job_path": "jobs/vaga_22_completa_estágio.txt",
    },

]

def run_single_analysis(resume_path: str, job_path: str):
    """Executa uma única análise, mede o tempo e retorna os resultados."""
    start_time = time.time()
    try:
        with open(resume_path, "rb") as f_resume:
            resume_filename = os.path.basename(resume_path)
            files = {'arquivo_pdf': (resume_filename, f_resume, 'application/pdf')}
            
            with open(job_path, "r", encoding="utf-8") as f_job:
                job_context = f_job.read()
                data = {'contexto_vaga': job_context}

            response = requests.post(API_URL, files=files, data=data, timeout=120)
            duration = time.time() - start_time
            response.raise_for_status()
            
            return {
                "success": True,
                "data": response.json(),
                "duration": duration
            }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "duration": time.time() - start_time
        }

def format_rerun_result(test_case, result):
    """Formata a saída da re-execução para o console e log."""
    header = f"--- {test_case['name']} ---"
    resume_name = os.path.basename(test_case['resume_path'])
    job_name = os.path.basename(test_case['job_path'])
    
    print(header)
    print(f"📄 Currículo: {resume_name}")
    print(f"🎯 Vaga     : {job_name}")
    
    if result["success"]:
        duration = result["duration"]
        score = result["data"].get("score_final_ponderado", "N/A")
        print(f"✅ SUCESSO na nova tentativa! (Score: {score}, Tempo: {duration:.2f}s)")
        # Salva o resultado completo no log para análise
        log_entry = {
            "test_name": test_case['name'],
            "status": "SUCESSO (RE-EXECUÇÃO)",
            "duration_seconds": duration,
            "full_response": result["data"]
        }
        logging.info(json.dumps(log_entry, indent=2, ensure_ascii=False))

    else:
        error_message = result["error"]
        print(f"❌ FALHOU NOVAMENTE! Erro: {error_message}")
        logging.error(f"Falha persistente no teste '{test_case['name']}': {error_message}")
    
    print("-" * (len(header) + 2) + "\n")


if __name__ == "__main__":
    print("🚀 Iniciando re-execução dos testes que falharam com erro 500...\n")
    
    for case in FAILED_TEST_CASES:
        result = run_single_analysis(case["resume_path"], case["job_path"])
        format_rerun_result(case, result)
        
    print("🏁 Re-execução finalizada.")
    print(f"Resultados detalhados foram salvos no arquivo: '{LOG_FILE}'")