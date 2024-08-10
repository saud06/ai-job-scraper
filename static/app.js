document.addEventListener("DOMContentLoaded", async () => {
  const el = document.getElementById("skillsChart");
  if (!el) return;
  try {
    const res = await fetch("/api/skills");
    const data = await res.json();
    const labels = data.map(d => d.skill);
    const counts = data.map(d => d.count);
    new Chart(el, {
      type: "bar",
      data: {
        labels: labels,
        datasets: [{
          label: "Mentions",
          data: counts
        }]
      },
      options: {
        responsive: true,
        scales: {
          x: { ticks: { autoSkip: true, maxRotation: 0 } },
          y: { beginAtZero: true }
        }
      }
    });
  } catch (e) {
    console.error(e);
  }
});