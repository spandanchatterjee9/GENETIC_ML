document.addEventListener("DOMContentLoaded", async () => {
    // Shared Chart configuration defaults for dark theme
    Chart.defaults.color = '#a0aec0';
    Chart.defaults.font.family = "'Outfit', sans-serif";
    Chart.defaults.plugins.tooltip.backgroundColor = 'rgba(15, 23, 42, 0.9)';
    Chart.defaults.plugins.tooltip.titleColor = '#4fd1c5';
    Chart.defaults.plugins.tooltip.padding = 10;
    Chart.defaults.plugins.tooltip.cornerRadius = 8;
    
    try {
        // Fetch data from endpoint
        const response = await fetch('/metrics');
        const data = await response.json();
        
        // Hide loader
        document.getElementById('dashboard-loading').classList.remove('active');
        
        // Build the Dashboard UI
        renderBestModelSummary(data.comparison);
        renderComparisonChart(data.comparison);
        renderFeatureChart(data.feature_importance);
        renderRocChart(data.roc);
        renderConfusionMatrices(data.matrices);

    } catch (error) {
        console.error("Failed to load metrics:", error);
        document.getElementById('best-model-summary').innerText = "Failed to load analysis. Check console for details.";
        document.getElementById('dashboard-loading').classList.remove('active');
    }
});

function renderBestModelSummary(compData) {
    // Find model with highest F1 score
    let bestModel = "";
    let maxF1 = 0;
    let maxRecall = 0;

    for (let model in compData) {
        if (compData[model].f1 > maxF1) {
            maxF1 = compData[model].f1;
            bestModel = model;
            maxRecall = compData[model].recall;
        }
    }
    
    document.getElementById('best-model-summary').innerHTML = 
        `<strong>${bestModel}</strong> performed best overall based on an F1-score of ${(maxF1*100).toFixed(1)}% and Recall of ${(maxRecall*100).toFixed(1)}%.`;
}

function renderComparisonChart(compData) {
    const ctx = document.getElementById('comparisonChart').getContext('2d');
    const labels = Object.keys(compData);
    
    const accuracy = labels.map(l => compData[l].accuracy);
    const precision = labels.map(l => compData[l].precision);
    const recall = labels.map(l => compData[l].recall);
    const f1 = labels.map(l => compData[l].f1);

    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [
                { label: 'Accuracy', data: accuracy, backgroundColor: 'rgba(79, 209, 197, 0.7)', borderRadius: 4 },
                { label: 'Precision', data: precision, backgroundColor: 'rgba(128, 90, 213, 0.7)', borderRadius: 4 },
                { label: 'Recall', data: recall, backgroundColor: 'rgba(237, 137, 54, 0.7)', borderRadius: 4 },
                { label: 'F1 Score', data: f1, backgroundColor: 'rgba(245, 101, 101, 0.7)', borderRadius: 4 }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: { min: 0.5, max: 1.0, grid: { color: 'rgba(255,255,255,0.05)' } },
                x: { grid: { display: false } }
            },
            plugins: { legend: { position: 'bottom' } },
            animation: { duration: 2000, easing: 'easeOutQuart' }
        }
    });
}

function renderFeatureChart(featData) {
    const ctx = document.getElementById('featureChart').getContext('2d');
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: featData.features,
            datasets: [{
                label: 'Importance Score',
                data: featData.importance,
                backgroundColor: 'rgba(79, 209, 197, 0.6)',
                borderColor: 'rgba(79, 209, 197, 1)',
                borderWidth: 1,
                borderRadius: 4
            }]
        },
        options: {
            indexAxis: 'y', // Horizontal bar chart
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                x: { grid: { color: 'rgba(255,255,255,0.05)' } },
                y: { grid: { display: false } }
            },
            plugins: { legend: { display: false } },
            animation: { delay: 300, duration: 1500 }
        }
    });
}

function renderRocChart(rocData) {
    const ctx = document.getElementById('rocChart').getContext('2d');
    const { fpr, ...models } = rocData;
    
    const colors = {
        'Random Forest': '#4fd1c5',
        'Logistic Regression': '#805ad5',
        'Decision Tree': '#ed8936',
        'KNN': '#f56565'
    };

    const datasets = Object.keys(models).map(modelName => {
        return {
            label: modelName,
            data: models[modelName],
            borderColor: colors[modelName] || '#fff',
            backgroundColor: colors[modelName] || '#fff',
            borderWidth: 2,
            pointRadius: 3,
            tension: 0.3
        };
    });

    // Add baseline
    datasets.push({
        label: 'Baseline',
        data: [0, 0.2, 0.4, 0.6, 0.8, 1.0], // corresponding approx to FPR matching
        borderColor: 'rgba(160, 174, 192, 0.5)',
        borderDash: [5, 5],
        borderWidth: 1,
        pointRadius: 0
    });

    new Chart(ctx, {
        type: 'line',
        data: {
            labels: fpr,
            datasets: datasets
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                x: { title: { display: true, text: 'False Positive Rate' }, grid: { color: 'rgba(255,255,255,0.05)' } },
                y: { title: { display: true, text: 'True Positive Rate' }, min: 0, max: 1.05, grid: { color: 'rgba(255,255,255,0.05)' } }
            },
            plugins: { legend: { position: 'bottom' } },
            animation: { delay: 600, duration: 2000 }
        }
    });
}

function renderConfusionMatrices(matrixData) {
    const container = document.getElementById('matrixContainer');
    
    for (const [model, metrics] of Object.entries(matrixData)) {
        const { tp, tn, fp, fn } = metrics;
        
        const card = document.createElement('div');
        card.className = 'card glass matrix-card glow-effect';
        card.innerHTML = `
            <h3 style="margin-bottom: 15px;">${model}</h3>
            <div class="matrix-table">
                <div class="cell tp">${tp}<span>True Positive</span></div>
                <div class="cell fn">${fn}<span>False Negative</span></div>
                <div class="cell fp">${fp}<span>False Positive</span></div>
                <div class="cell tn">${tn}<span>True Negative</span></div>
            </div>
        `;
        container.appendChild(card);
    }
}
