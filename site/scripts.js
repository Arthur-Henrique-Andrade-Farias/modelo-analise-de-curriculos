document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('analysis-form');
    const submitButton = document.getElementById('submit-button');
    const loadingSpinner = document.getElementById('loading-spinner');
    const resultsContainer = document.getElementById('results-container');

    form.addEventListener('submit', async (event) => {
        event.preventDefault();
        const pdfFile = document.getElementById('curriculo-pdf').files[0];
        const jobContext = document.getElementById('contexto-vaga').value;

        if (!pdfFile || !jobContext) {
            alert('Por favor, preencha todos os campos.');
            return;
        }

        const formData = new FormData();
        formData.append('arquivo_pdf', pdfFile);
        formData.append('contexto_vaga', jobContext);

        submitButton.disabled = true;
        submitButton.innerHTML = `
            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="spinner-icon"><path d="M21 12a9 9 0 1 1-6.219-8.56"/></svg>
            Analisando...
        `;
        loadingSpinner.classList.remove('hidden');
        resultsContainer.classList.add('hidden');
        resultsContainer.innerHTML = '';

        try {
            const response = await fetch('http://127.0.0.1:8000/analisar_curriculo', {
                method: 'POST',
                body: formData,
            });
            const data = await response.json();
            if (!response.ok) {
                throw new Error(data.detail || 'Ocorreu um erro desconhecido.');
            }
            displayResults(data);
        } catch (error) {
            displayError(error.message);
        } finally {
            submitButton.disabled = false;
            submitButton.innerHTML = `
                <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m9 17 5-5-5-5"/></svg>
                Analisar Compatibilidade
            `;
            loadingSpinner.classList.add('hidden');
            resultsContainer.classList.remove('hidden');
        }
    });

    function displayResults(data) {
        const criteriaMap = {
            aderencia_tecnica: 'Aderência Técnica',
            compatibilidade_experiencia: 'Compatibilidade de Experiência',
            compatibilidade_geografica: 'Compatibilidade Geográfica',
            alinhamento_educacional: 'Alinhamento Educacional',
            valor_diferenciais: 'Valor dos Diferenciais',
        };

        let criteriaHTML = '';
        for (const key in criteriaMap) {
            if (data[key]) {
                const item = data[key];
                criteriaHTML += `
                    <div class="criterion-card">
                        <h3><span>${criteriaMap[key]}</span> <span class="score">${item.nota}/10</span></h3>
                        <p>${item.justificativa}</p>
                    </div>`;
            }
        }

        const createListItems = (list) => list.map(item => `<li>${item}</li>`).join('');

        resultsContainer.innerHTML = `
            <div class="result-header">
                <div class="score-circle" id="score-circle">
                    <div class="score-circle-inner">
                        <div class="score-value">${data.score_final_ponderado}<span>/10</span></div>
                    </div>
                </div>
                <h2>Score Final Ponderado</h2>
            </div>
            
            <div class="criteria-grid">${criteriaHTML}</div>

            <div class="summary-section">
                <h3>Pontos Fortes</h3>
                <ul class="summary-list fortes">${createListItems(data.pontos_fortes)}</ul>
            </div>
            
            <div class="summary-section">
                <h3>Pontos de Desenvolvimento</h3>
                <ul class="summary-list desenvolvimento">${createListItems(data.pontos_de_desenvolvimento)}</ul>
            </div>

            ${data.perguntas_sugeridas && data.perguntas_sugeridas.length > 0 ? `
            <div class="summary-section">
                <h3>Perguntas Sugeridas</h3>
                <ul class="summary-list perguntas">${createListItems(data.perguntas_sugeridas)}</ul>
            </div>` : ''}
        `;

        // Anima o círculo de score
        setTimeout(() => {
            const scoreCircle = document.getElementById('score-circle');
            if (scoreCircle) {
                scoreCircle.style.setProperty('--score', data.score_final_ponderado * 10);
            }
        }, 100);
    }

    function displayError(message) {
        resultsContainer.classList.remove('hidden');
        resultsContainer.innerHTML = `<div class="error-message"><strong>Erro na Análise:</strong> ${message}</div>`;
    }
});