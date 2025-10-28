(function () {
  const nakitCanvas = document.getElementById('nakitAkisGrafik');
  if (nakitCanvas) {
    fetch(nakitCanvas.dataset.source)
      .then((resp) => resp.json())
      .then((data) => {
        new Chart(nakitCanvas.getContext('2d'), {
          type: 'line',
          data: {
            labels: data.labels,
            datasets: [
              {
                label: 'Gelir',
                data: data.gelir,
                borderColor: '#16a34a',
                backgroundColor: 'rgba(22, 163, 74, 0.2)',
                fill: true,
              },
              {
                label: 'Gider',
                data: data.gider,
                borderColor: '#dc2626',
                backgroundColor: 'rgba(220, 38, 38, 0.2)',
                fill: true,
              },
            ],
          },
          options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
              legend: { position: 'bottom' },
            },
            scales: {
              y: {
                ticks: {
                  callback: (value) => `₺${value.toFixed(0)}`,
                },
              },
            },
          },
        });
      });
  }
})();
