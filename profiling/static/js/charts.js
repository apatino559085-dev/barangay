// Barangay Profiling System - Population Statistics Charts

function initPopulationCharts(data) {
  if (!window.Chart || !data) return;

  const fontConfig = {
    family: "'Plus Jakarta Sans', 'Inter', sans-serif",
    size: 13,
    weight: '500'
  };

  // 1. Gender Distribution Doughnut Chart
  const genderCtx = document.getElementById('genderChart');
  if (genderCtx) {
    new Chart(genderCtx, {
      type: 'doughnut',
      data: {
        labels: data.gender.labels,
        datasets: [{
          data: data.gender.data,
          backgroundColor: ['#2563eb', '#db2777', '#9333ea'],
          hoverOffset: 6,
          borderWidth: 2,
          borderColor: '#ffffff'
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            position: 'bottom',
            labels: { font: fontConfig, boxWidth: 14, padding: 15 }
          },
          tooltip: {
            callbacks: {
              label: function (context) {
                const total = context.dataset.data.reduce((a, b) => a + b, 0);
                const value = context.raw || 0;
                const pct = total > 0 ? ((value / total) * 100).toFixed(1) : 0;
                return ` ${context.label}: ${value} (${pct}%)`;
              }
            }
          }
        },
        cutout: '70%'
      }
    });
  }

  // 2. Voter Registration Status Doughnut Chart
  const voterCtx = document.getElementById('voterChart');
  if (voterCtx) {
    new Chart(voterCtx, {
      type: 'doughnut',
      data: {
        labels: data.voters.labels,
        datasets: [{
          data: data.voters.data,
          backgroundColor: ['#059669', '#cbd5e1'],
          hoverOffset: 6,
          borderWidth: 2,
          borderColor: '#ffffff'
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            position: 'bottom',
            labels: { font: fontConfig, boxWidth: 14, padding: 15 }
          },
          tooltip: {
            callbacks: {
              label: function (context) {
                const total = context.dataset.data.reduce((a, b) => a + b, 0);
                const value = context.raw || 0;
                const pct = total > 0 ? ((value / total) * 100).toFixed(1) : 0;
                return ` ${context.label}: ${value} (${pct}%)`;
              }
            }
          }
        },
        cutout: '70%'
      }
    });
  }

  // 3. Age Demographics Bar Chart
  const ageCtx = document.getElementById('ageChart');
  if (ageCtx) {
    new Chart(ageCtx, {
      type: 'bar',
      data: {
        labels: data.age.labels,
        datasets: [{
          label: 'Residents Count',
          data: data.age.data,
          backgroundColor: ['#f59e0b', '#0284c7', '#7c3aed'],
          borderRadius: 8,
          borderSkipped: false
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: false }
        },
        scales: {
          y: {
            beginAtZero: true,
            ticks: { precision: 0, font: fontConfig },
            grid: { color: '#f1f5f9' }
          },
          x: {
            ticks: { font: fontConfig },
            grid: { display: false }
          }
        }
      }
    });
  }

  // 4. Purok Population Distribution Bar Chart
  const purokCtx = document.getElementById('purokChart');
  if (purokCtx && data.purok.labels.length > 0) {
    new Chart(purokCtx, {
      type: 'bar',
      data: {
        labels: data.purok.labels,
        datasets: [{
          label: 'Residents',
          data: data.purok.data,
          backgroundColor: '#0d9488',
          borderRadius: 6,
          borderSkipped: false
        }]
      },
      options: {
        indexAxis: 'y',
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: false }
        },
        scales: {
          x: {
            beginAtZero: true,
            ticks: { precision: 0, font: fontConfig },
            grid: { color: '#f1f5f9' }
          },
          y: {
            ticks: { font: fontConfig },
            grid: { display: false }
          }
        }
      }
    });
  }
}
