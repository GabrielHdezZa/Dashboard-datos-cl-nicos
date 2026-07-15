let ageChartInstance = null;
let typeChartInstance = null;

document.addEventListener('DOMContentLoaded', () => {
    fetchData();
    // Polling every 5 seconds
    setInterval(fetchData, 5000);
});

function fetchData() {
    fetch('data.json?t=' + new Date().getTime()) // Prevent caching
        .then(response => {
            if (!response.ok) throw new Error("Not OK");
            return response.json();
        })
        .then(data => {
            updateDashboard(data);
        })
        .catch(error => {
            console.error('Error loading data:', error);
        });
}

function updateDashboard(data) {
    if (!data || data.length === 0) return;

    // 1. Calculate KPIs
    const totalPruebas = data.length;
    let sumIA = 0;
    let sumMed = 0;

    data.forEach(row => {
        sumIA += row['Aciertos IA'];
        sumMed += row['Aciertos Médicos'];
    });

    const avgIA = (sumIA / totalPruebas).toFixed(1);
    const avgMed = (sumMed / totalPruebas).toFixed(1);

    document.getElementById('kpi-total').textContent = totalPruebas;
    document.getElementById('kpi-ai').textContent = `${avgIA}%`;
    document.getElementById('kpi-med').textContent = `${avgMed}%`;

    // 2. Prepare Data
    const byAge = {};
    const byType = {};

    data.forEach(row => {
        const age = row['Tramo Edad'];
        if (!byAge[age]) byAge[age] = { ia: [], med: [] };
        byAge[age].ia.push(row['Aciertos IA']);
        byAge[age].med.push(row['Aciertos Médicos']);

        const type = row['Tipo Prueba'];
        if (!byType[type]) byType[type] = 0;
        byType[type]++;
    });

    const calcStats = (arr) => {
        const mean = arr.reduce((a, b) => a + b, 0) / arr.length;
        const variance = arr.reduce((a, b) => a + Math.pow(b - mean, 2), 0) / arr.length;
        return { mean: mean.toFixed(2), variance: variance.toFixed(2) };
    };

    const ageLabels = Object.keys(byAge);
    const iaMeans = [];
    const medMeans = [];
    
    const tbody = document.querySelector('#stats-table tbody');
    tbody.innerHTML = ''; // Clear table for update

    ageLabels.forEach(age => {
        const iaStats = calcStats(byAge[age].ia);
        const medStats = calcStats(byAge[age].med);
        
        iaMeans.push(iaStats.mean);
        medMeans.push(medStats.mean);

        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td><strong>${age}</strong></td>
            <td style="color: var(--accent-ai)">${iaStats.mean}%</td>
            <td>${iaStats.variance}</td>
            <td style="color: var(--accent-med)">${medStats.mean}%</td>
            <td>${medStats.variance}</td>
        `;
        tbody.appendChild(tr);
    });

    // 3. Update Charts
    updateAgeChart(ageLabels, iaMeans, medMeans);
    updateTypeChart(Object.keys(byType), Object.values(byType));
}

function updateAgeChart(labels, dataIA, dataMed) {
    const ctx = document.getElementById('ageChart').getContext('2d');
    
    if (ageChartInstance) {
        ageChartInstance.data.labels = labels;
        ageChartInstance.data.datasets[0].data = dataIA;
        ageChartInstance.data.datasets[1].data = dataMed;
        ageChartInstance.update();
    } else {
        Chart.defaults.color = '#94a3b8';
        Chart.defaults.font.family = "'Outfit', sans-serif";
        ageChartInstance = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [
                    { label: 'IA', data: dataIA, backgroundColor: 'rgba(56, 189, 248, 0.7)', borderColor: '#38bdf8', borderWidth: 1, borderRadius: 4 },
                    { label: 'Médicos', data: dataMed, backgroundColor: 'rgba(129, 140, 248, 0.7)', borderColor: '#818cf8', borderWidth: 1, borderRadius: 4 }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: { min: 80, grid: { color: 'rgba(255, 255, 255, 0.1)' } },
                    x: { grid: { display: false } }
                }
            }
        });
    }
}

function updateTypeChart(labels, data) {
    const ctx = document.getElementById('typeChart').getContext('2d');
    
    if (typeChartInstance) {
        typeChartInstance.data.labels = labels;
        typeChartInstance.data.datasets[0].data = data;
        typeChartInstance.update();
    } else {
        typeChartInstance = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: labels,
                datasets: [{
                    data: data,
                    backgroundColor: ['#38bdf8', '#818cf8', '#c084fc'],
                    borderWidth: 0,
                    hoverOffset: 4
                }]
            },
            options: { responsive: true, maintainAspectRatio: false, cutout: '70%' }
        });
    }
}
