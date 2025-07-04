import os
import requests
import json
import time
import logging

API_URL = "http://127.0.0.1:8000/analisar_curriculo"
LOG_FILE = "test_final_consistency_run.log"

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE, mode='w', encoding='utf-8'),
    ]
)

TEST_CASES = [
    {
        "name": "Teste #1: Vaga Ambígua vs Candidato OK",
        "resume_path": "resumes/Curriculum_2025_01.pdf",
        "job_path": "jobs/cv_qualquer_local.txt",
        "expectations": {"min_score": 7, "max_score": 9, "geo_score": 10, "required_questions": []}
    },
    {
        "name": "Teste #2: Mismatch Técnico e Geográfico (iOS Dev vs QA)",
        "resume_path": "resumes/curriculo_gerado_10_juliana.pdf",
        "job_path": "jobs/vaga_10_completa_analista.txt",
        "expectations": {"min_score": 3, "max_score": 5, "geo_score": 1, "required_questions": []}
    },
    {
        "name": "Teste #3: Superqualificado e Incompatível Geo",
        "resume_path": "resumes/curriculo_gerado_11_caio.pdf",
        "job_path": "jobs/vaga_11_completa_estágio.txt",
        "expectations": {"min_score": 4, "max_score": 6, "geo_score": 0, "required_questions": []}
    },
    {
        "name": "Teste #4: Mismatch Total (Jogos vs ML)",
        "resume_path": "resumes/curriculo_gerado_12_lucas.pdf",
        "job_path": "jobs/vaga_12_completa_engenheiro.txt",
        "expectations": {"min_score": 2, "max_score": 4, "geo_score": 1, "required_questions": []}
    },
    {
        "name": "Teste #5: Mismatch Total (Eng. Dados vs Embarcados)",
        "resume_path": "resumes/curriculo_gerado_13_ricardo.pdf",
        "job_path": "jobs/vaga_13_completa_pessoa.txt",
        "expectations": {"min_score": 1, "max_score": 3, "geo_score": 0, "required_questions": []}
    },
    {
        "name": "Teste #6: Quase Perfeito mas Incompatível Geo (BI)",
        "resume_path": "resumes/curriculo_gerado_14_rafaela.pdf",
        "job_path": "jobs/vaga_14_completa_analista.txt",
        "expectations": {"min_score": 5, "max_score": 7, "geo_score": 0, "required_questions": []}
    },
    {
        "name": "Teste #7: Mismatch Total (Cientista Dados vs Pentester)",
        "resume_path": "resumes/curriculo_gerado_15_matheus.pdf",
        "job_path": "jobs/vaga_15_completa_especialista.txt",
        "expectations": {"min_score": 3, "max_score": 5, "geo_score": 10, "required_questions": []}
    },
    {
        "name": "Teste #8: Mismatch de Senioridade (Jr vs Gerente)",
        "resume_path": "resumes/curriculo_gerado_16_julia.pdf",
        "job_path": "jobs/vaga_16_completa_gerente.txt",
        "expectations": {"min_score": 3, "max_score": 5, "geo_score": 10, "required_questions": []}
    },
    {
        "name": "Teste #9: Mismatch Total (DBA vs Dev Jogos)",
        "resume_path": "resumes/curriculo_gerado_17_rafael.pdf",
        "job_path": "jobs/vaga_17_completa_desenvolvedor.txt",
        "expectations": {"min_score": 1, "max_score": 3, "geo_score": 1, "required_questions": []}
    },
    {
        "name": "Teste #10: Mismatch Parcial (Dados vs UX)",
        "resume_path": "resumes/curriculo_gerado_18_lucas.pdf",
        "job_path": "jobs/vaga_18_completa_ux.txt",
        "expectations": {"min_score": 3, "max_score": 5, "geo_score": 1, "required_questions": []}
    },
    {
        "name": "Teste #11: Mismatch Geo (Admin Linux)",
        "resume_path": "resumes/curriculo_gerado_19_ricardo.pdf",
        "job_path": "jobs/vaga_19_completa_administrador.txt",
        "expectations": {"min_score": 5, "max_score": 7, "geo_score": 0, "required_questions": []}
    },
    {
        "name": "Teste #12: Mismatch Total (Frontend vs Segurança)",
        "resume_path": "resumes/curriculo_gerado_1_diego.pdf",
        "job_path": "jobs/vaga_1_completa_analista.txt",
        "expectations": {"min_score": 1, "max_score": 3, "geo_score": 1, "required_questions": []}
    },
    {
        "name": "Teste #13: Mismatch Total (Recrutadora vs Dev Go)",
        "resume_path": "resumes/curriculo_gerado_1_juliana.pdf",
        "job_path": "jobs/vaga_1_completa_desenvolvedor.txt",
        "expectations": {"min_score": 0, "max_score": 2, "geo_score": 10, "required_questions": []}
    },
    {
        "name": "Teste #14: Mismatch Técnico (Dev vs Suporte)",
        "resume_path": "resumes/curriculo_gerado_1_rodrigo.pdf",
        "job_path": "jobs/vaga_1_completa_engenheiro(a).txt",
        "expectations": {"min_score": 3, "max_score": 5, "geo_score": 1, "required_questions": []}
    },
    {
        "name": "Teste #15: Mismatch Técnico (Cloud vs Salesforce)",
        "resume_path": "resumes/curriculo_gerado_20_carlos.pdf",
        "job_path": "jobs/vaga_20_completa_consultor.txt",
        "expectations": {"min_score": 4, "max_score": 6, "geo_score": 10, "required_questions": []}
    },
    {
        "name": "Teste #16: Quase Perfeito (SRE)",
        "resume_path": "resumes/curriculo_gerado_21_eduardo.pdf",
        "job_path": "jobs/vaga_21_completa_engenheiro(a).txt",
        "expectations": {"min_score": 8, "max_score": 10, "geo_score": 10, "required_questions": []}
    },
    {
        "name": "Teste #17: Superqualificado e Incompatível Geo (2)",
        "resume_path": "resumes/curriculo_gerado_22_luiz.pdf",
        "job_path": "jobs/vaga_22_completa_estágio.txt",
        "expectations": {"min_score": 5, "max_score": 7, "geo_score": 1, "required_questions": []}
    },
    {
        "name": "Teste #18: Mismatch Técnico (QA vs WordPress)",
        "resume_path": "resumes/curriculo_gerado_23_lucas.pdf",
        "job_path": "jobs/vaga_23_completa_desenvolvedor(a).txt",
        "expectations": {"min_score": 4, "max_score": 6, "geo_score": 10, "required_questions": []}
    },
    {
        "name": "Teste #19: Mismatch Técnico e Geo (QA vs Cloud)",
        "resume_path": "resumes/curriculo_gerado_24_lucas.pdf",
        "job_path": "jobs/vaga_24_completa_analista.txt",
        "expectations": {"min_score": 2, "max_score": 4, "geo_score": 1, "required_questions": []}
    },
    {
        "name": "Teste #20: Mismatch de Senioridade (Estagiário vs Tech Lead)",
        "resume_path": "resumes/curriculo_gerado_25_joão.pdf",
        "job_path": "jobs/vaga_25_completa_tech.txt",
        "expectations": {"min_score": 3, "max_score": 5, "geo_score": 10, "required_questions": []}
    },
    {
        "name": "Teste #21: Mismatch Técnico (SaaS vs Elixir)",
        "resume_path": "resumes/curriculo_gerado_26_joão.pdf",
        "job_path": "jobs/vaga_26_completa_desenvolvedor(a).txt",
        "expectations": {"min_score": 5, "max_score": 7, "geo_score": 10, "required_questions": []}
    },
    {
        "name": "Teste #22: Vaga Incompleta vs Gestor Ágil",
        "resume_path": "resumes/curriculo_gerado_27_larissa.pdf",
        "job_path": "jobs/vaga_27_incompleta_vaga.txt",
        "expectations": {"min_score": 6, "max_score": 8, "geo_score": 10, "required_questions": []}
    },
    {
        "name": "Teste #23: Vaga Incompleta vs Gestor Ágil (2)",
        "resume_path": "resumes/curriculo_gerado_28_lucas.pdf",
        "job_path": "jobs/vaga_28_incompleta_vaga.txt",
        "expectations": {"min_score": 4, "max_score": 6, "geo_score": 5, "required_questions": []}
    },
    {
        "name": "Teste #24: Mismatch Total (Designer vs TI) com Vaga Incompleta",
        "resume_path": "resumes/curriculo_gerado_29_renata.pdf",
        "job_path": "jobs/vaga_29_incompleta_vaga.txt",
        "expectations": {"min_score": 2, "max_score": 4, "geo_score": 10, "required_questions": []}
    },
    {
        "name": "Teste #25: Mismatch Técnico e Geo (Pesquisa vs Eng. Dados Corp)",
        "resume_path": "resumes/curriculo_gerado_2_leticia.pdf",
        "job_path": "jobs/vaga_2_completa_engenheira.txt",
        "expectations": {"min_score": 4, "max_score": 6, "geo_score": 1, "required_questions": []}
    },
    {
        "name": "Teste #26: Bom Match com Vaga Incompleta",
        "resume_path": "resumes/curriculo_gerado_2_lucas.pdf",
        "job_path": "jobs/vaga_2_incompleta_vaga.txt",
        "expectations": {"min_score": 8, "max_score": 10, "geo_score": 10, "required_questions": []}
    },
    {
        "name": "Teste #27: Mismatch Técnico (PO vs Estagiário Inovação)",
        "resume_path": "resumes/curriculo_gerado_30_bruno.pdf",
        "job_path": "jobs/vaga_30_incompleta_vaga.txt",
        "expectations": {"min_score": 6, "max_score": 8, "geo_score": 10, "required_questions": []}
    },
    {
        "name": "Teste #28: Bom Match com Vaga de Gerente Incompleta",
        "resume_path": "resumes/curriculo_gerado_31_ricardo.pdf",
        "job_path": "jobs/vaga_31_incompleta_vaga.txt",
        "expectations": {"min_score": 7, "max_score": 9, "geo_score": 10, "required_questions": []}
    },
    {
        "name": "Teste #29: Mismatch Técnico (Segurança vs Dev) com Vaga Incompleta",
        "resume_path": "resumes/curriculo_gerado_32_marcos.pdf",
        "job_path": "jobs/vaga_32_incompleta_vaga.txt",
        "expectations": {"min_score": 6, "max_score": 8, "geo_score": 10, "required_questions": []}
    },
    {
        "name": "Teste #30: Mismatch Total (Tech Writer vs Analista Sistemas)",
        "resume_path": "resumes/curriculo_gerado_33_laura.pdf",
        "job_path": "jobs/vaga_33_incompleta_vaga.txt",
        "expectations": {"min_score": 2, "max_score": 4, "geo_score": 5, "required_questions": []}
    },
    {
        "name": "Teste #31: Mismatch Técnico (SAP vs Inovação) com Vaga Incompleta",
        "resume_path": "resumes/curriculo_gerado_34_carlos.pdf",
        "job_path": "jobs/vaga_34_incompleta_vaga.txt",
        "expectations": {"min_score": 6, "max_score": 8, "geo_score": 10, "required_questions": []}
    },
    {
        "name": "Teste #32: Bom Match (Dev Experiente vs Vaga de Modernização)",
        "resume_path": "resumes/curriculo_gerado_35_carlos.pdf",
        "job_path": "jobs/vaga_35_incompleta_vaga.txt",
        "expectations": {"min_score": 7, "max_score": 9, "geo_score": 10, "required_questions": []}
    },
    {
        "name": "Teste #33: Mismatch Técnico e Geo (Web vs Dados) com Vaga Incompleta",
        "resume_path": "resumes/curriculo_gerado_36_lucas.pdf",
        "job_path": "jobs/vaga_36_incompleta_vaga.txt",
        "expectations": {"min_score": 3, "max_score": 5, "geo_score": 5, "required_questions": []}
    },
    {
        "name": "Teste #34: Mismatch de Senioridade (Estagiária vs Líder Técnico)",
        "resume_path": "resumes/curriculo_gerado_37_rafaela.pdf",
        "job_path": "jobs/vaga_37_incompleta_vaga.txt",
        "expectations": {"min_score": 6, "max_score": 8, "geo_score": 10, "required_questions": []}
    },
    {
        "name": "Teste #35: Mismatch Total (Direito vs DevOps) com Vaga Incompleta",
        "resume_path": "resumes/curriculo_gerado_38_rafaela.pdf",
        "job_path": "jobs/vga_38_incompleta_vaga.txt",
        "expectations": {"min_score": 2, "max_score": 4, "geo_score": 10, "required_questions": []}
    },
    {
        "name": "Teste #36: Mismatch Parcial (Dev vs Mkt/Dev) com Vaga Incompleta",
        "resume_path": "resumes/curriculo_gerado_3_camila.pdf",
        "job_path": "jobs/vaga_39_incompleta_vaga.txt",
        "expectations": {"min_score": 7, "max_score": 9, "geo_score": 10, "required_questions": []}
    },
    {
        "name": "Teste #37: Mismatch Técnico e Geo (ML vs Frontend)",
        "resume_path": "resumes/curriculo_gerado_3_gabriel.pdf",
        "job_path": "jobs/vaga_3_completa_desenvolvedor.txt",
        "expectations": {"min_score": 1, "max_score": 3, "geo_score": 0, "required_questions": []}
    },
    {
        "name": "Teste #38: Mismatch Técnico (DevOps vs ML)",
        "resume_path": "resumes/curriculo_gerado_3_ricardo.pdf",
        "job_path": "jobs/vaga_3_completa_engenheiro.txt",
        "expectations": {"min_score": 3, "max_score": 5, "geo_score": 10, "required_questions": []}
    },
    {
        "name": "Teste #39: Mismatch Total (Designer vs Eng. Civil) com Vaga Incompleta",
        "resume_path": "resumes/curriculo_gerado_4_mariana.pdf",
        "job_path": "jobs/vaga_40_incompleta_vaga.txt",
        "expectations": {"min_score": 2, "max_score": 4, "geo_score": 10, "required_questions": []}
    },
    {
        "name": "Teste #40: Mismatch Técnico e Geo (Dev vs Suporte)",
        "resume_path": "resumes/curriculo_gerado_4_mauricio.pdf",
        "job_path": "jobs/vaga_4_completa_analista.txt",
        "expectations": {"min_score": 3, "max_score": 5, "geo_score": 0, "required_questions": []}
    },
    {
        "name": "Teste #41: Bom Match (Dev vs Gestor) com Vaga Incompleta",
        "resume_path": "resumes/curriculo_gerado_5_mateus.pdf",
        "job_path": "jobs/vaga_4_incompleta_vaga.txt",
        "expectations": {"min_score": 7, "max_score": 9, "geo_score": 10, "required_questions": []}
    },
    {
        "name": "Teste #42: Mismatch de Senioridade (Estagiário vs PM)",
        "resume_path": "resumes/curriculo_gerado_6_lucas.pdf",
        "job_path": "jobs/vaga_5_completa_product.txt",
        "expectations": {"min_score": 3, "max_score": 5, "geo_score": 10, "required_questions": []}
    },
    {
        "name": "Teste #43: Mismatch Técnico e Geo (RoR vs DevOps)",
        "resume_path": "resumes/curriculo_gerado_7_lucas.pdf",
        "job_path": "jobs/vaga_6_completa_devops.txt",
        "expectations": {"min_score": 3, "max_score": 5, "geo_score": 1, "required_questions": []}
    },
    {
        "name": "Teste #44: Bom Match de Arquiteto",
        "resume_path": "resumes/curriculo_gerado_8_ricardo.pdf",
        "job_path": "jobs/vaga_7_completa_arquiteto(a).txt",
        "expectations": {"min_score": 8, "max_score": 10, "geo_score": 10, "required_questions": []}
    },
    {
        "name": "Teste #45: Mismatch Total (Android vs Geoprocessamento)",
        "resume_path": "resumes/curriculo_gerado_9_felipe.pdf",
        "job_path": "jobs/vaga_8_completa_cientista.txt",
        "expectations": {"min_score": 1, "max_score": 3, "geo_score": 1, "required_questions": []}
    },
    {
        "name": "Teste #46: Mismatch Total (Cientista Dados vs Dev iOS)",
        "resume_path": "resumes/cv_dilema_geo.pdf",
        "job_path": "jobs/vaga_9_completa_desenvolvedor.txt",
        "expectations": {"min_score": 1, "max_score": 3, "geo_score": 1, "required_questions": []}
    },
    {
        "name": "Teste #47: Mismatch de Especialização (Generalista vs Especialista)",
        "resume_path": "resumes/cv_generalista.pdf",
        "job_path": "jobs/vaga_backend_especialista.txt",
        "expectations": {"min_score": 6, "max_score": 8, "geo_score": 10, "required_questions": []}
    },
    {
        "name": "Teste #48: Mismatch Técnico e Geo (Java vs Dados)",
        "resume_path": "resumes/cv_qualquer_local.pdf",
        "job_path": "jobs/vaga_dados_junior.txt",
        "expectations": {"min_score": 2, "max_score": 4, "geo_score": 1, "required_questions": []}
    },
    {
        "name": "Teste #49: Mismatch Técnico e Geo (Backend Java vs Cientista Dados)",
        "resume_path": "resumes/cv_quase_perfeito.pdf",
        "job_path": "jobs/vaga_dados_presencial.txt",
        "expectations": {"min_score": 4, "max_score": 6, "geo_score": 0, "required_questions": []}
    },
    {
        "name": "Teste #50: Mismatch Total (Marketing vs Dev Java)",
        "resume_path": "resumes/cv_transicao_carreira.pdf",
        "job_path": "jobs/vaga_java_especialista.txt",
        "expectations": {"min_score": 0, "max_score": 2, "geo_score": 1, "required_questions": []}
    },
]


def run_test(test_case):
    """
    Executa um único caso de teste e retorna um dicionário com todos os detalhes.
    """
    print(f"--- Executando Teste de Consistência: {test_case['name']} ---")
    
    resume_path = test_case.get("resume_path") or test_case.get("resume_file")
    job_path = test_case.get("job_path") or test_case.get("job_file")
    start_time = time.time()
    
    try:
        with open(resume_path, "rb") as f_resume, open(job_path, "r", encoding="utf-8") as f_job:
            resume_filename = os.path.basename(resume_path)
            job_context = f_job.read()
            files = {'arquivo_pdf': (resume_filename, f_resume, 'application/pdf')}
            data = {'contexto_vaga': job_context}
            
            response = requests.post(API_URL, files=files, data=data, timeout=120)
            duration = time.time() - start_time
            response.raise_for_status()
        
        result = response.json()
        errors = []
        expectations = test_case["expectations"]

        score = result["score_final_ponderado"]
        min_s, max_s = expectations.get("min_score"), expectations.get("max_score")
        if min_s is not None and score < min_s:
            errors.append(f"Score Final: [Esperado: >={min_s}, Recebido: {score}]")
        if max_s is not None and score > max_s:
            errors.append(f"Score Final: [Esperado: <={max_s}, Recebido: {score}]")
        
        geo_score = result["compatibilidade_geografica"]["nota"]
        expected_geo = expectations.get("geo_score")
        if expected_geo is not None and geo_score != expected_geo:
            errors.append(f"Score Geográfico: [Esperado: {expected_geo}, Recebido: {geo_score}]")
            
        if "required_questions" in expectations:
            generated_questions_text = " ".join(result.get("perguntas_sugeridas", [])).lower()
            for req_question in expectations["required_questions"]:
                if req_question.lower() not in generated_questions_text:
                    errors.append(f"Pergunta Ausente: Nenhuma pergunta continha o termo '{req_question}'.")

        status = "PASSOU" if not errors else "FALHOU"
        if status == "PASSOU":
            print(f"✅ {status}! (Score: {score}, Tempo: {duration:.2f}s)")
        else:
            print(f"❌ {status}! (Score: {score}, Tempo: {duration:.2f}s)")
            for error in errors:
                print(f"  - {error}")

        log_entry = {
            "test_name": test_case['name'],
            "status": status,
            "duration_seconds": duration,
            "errors": errors,
            "full_response": result
        }
        logging.info(json.dumps(log_entry, indent=2, ensure_ascii=False))
        return log_entry

    except Exception as e:
        duration = time.time() - start_time
        error_message = f"ERRO CRÍTICO ao executar o teste em {duration:.2f}s: {e}"
        print(f"💥 {error_message}")
        logging.error(f"Erro de execução no teste '{test_case['name']}': {e}")
        return {"test_name": test_case['name'], "status": "ERRO_CRITICO", "errors": [str(e)]}
    
    finally:
        print("-" * (len(test_case['name']) + 36) + "\n")


if __name__ == "__main__":
    print("🚀 Iniciando suíte de testes de CONSISTÊNCIA do Modelo...\n")
    
    print(f"Executando {len(TEST_CASES)} casos de teste definidos como 'Gabarito'.")

    results_summary = []
    
    for case in TEST_CASES:
        result = run_test(case)
        results_summary.append(result)
            
    total_tests = len(results_summary)
    passed_tests = [r for r in results_summary if r.get("status") == "PASSOU"]
    failed_tests = [r for r in results_summary if r.get("status") == "FALHOU"]
    crashed_tests = [r for r in results_summary if r.get("status") == "ERRO_CRITICO"]
    
    total_duration = sum(r.get("duration_seconds", 0) for r in passed_tests)
    average_time = total_duration / len(passed_tests) if passed_tests else 0
    
    print("=" * 45)
    print("📊 SUMÁRIO FINAL DA EXECUÇÃO")
    print("=" * 45)
    print(f"Total de Testes Executados   : {total_tests}")
    print(f"✅ Testes que Passaram      : {len(passed_tests)}")
    print(f"❌ Testes que Falharam      : {len(failed_tests)}")
    print(f"💥 Testes com Erro Crítico  : {len(crashed_tests)}")
    if passed_tests:
        print(f"⏱️  Tempo Médio (testes ok)  : {average_time:.2f} segundos")
    
    if failed_tests:
        print("\n📋 DETALHES DAS FALHAS DE VALIDAÇÃO:")
        for failure in failed_tests:
            print(f"\n  - Teste: {failure['test_name']}")
            for error_detail in failure.get('errors', []):
                print(f"    - Motivo: {error_detail}")
    
    if crashed_tests:
        print("\n📋 DETALHES DOS ERROS CRÍTICOS:")
        for crash in crashed_tests:
            print(f"\n  - Teste: {crash['test_name']}")
            for error_detail in crash.get('errors', []):
                print(f"    - Motivo: {error_detail}")

    print("\n" + "=" * 45)
    print(f"Resultados completos foram salvos no arquivo: '{LOG_FILE}'")
    print("=" * 45)
