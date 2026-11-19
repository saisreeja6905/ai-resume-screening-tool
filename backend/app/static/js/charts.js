/**
 * AntiGravity AI Resume Screener - Visualization & Analytics Charts
 */

window.AppCharts = {
  // Initialize Candidates Status Pie/Doughnut Chart
  initStatusChart: (canvasId, dataLabels, dataValues) => {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return null;

    return new Chart(ctx, {
      type: 'doughnut',
      data: {
        labels: dataLabels && dataLabels.length > 0 ? dataLabels : ['New', 'Screening', 'Shortlisted', 'Rejected', 'Hired'],
        datasets: [{
          data: dataValues && dataValues.length > 0 ? dataValues : [12, 8, 5, 2, 3],
          backgroundColor: [
            '#3b82f6', // New
            '#f59e0b', // Screening
            '#10b981', // Shortlisted
            '#ef4444', // Rejected
            '#8b5cf6', // Hired
          ],
          borderWidth: 2,
          borderColor: '#ffffff',
        }],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            position: 'bottom',
            labels: {
              boxWidth: 12,
              font: { family: 'Inter', size: 12 },
            },
          },
        },
        cutout: '70%',
      },
    });
  },

  // Initialize Skill Frequency Distribution Chart
  initSkillChart: (canvasId, skillLabels, skillCounts) => {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return null;

    return new Chart(ctx, {
      type: 'bar',
      data: {
        labels: skillLabels && skillLabels.length > 0 ? skillLabels : ['Python', 'SQL', 'React', 'Docker', 'AWS', 'Flask', 'Git'],
        datasets: [{
          label: 'Candidates with Skill',
          data: skillCounts && skillCounts.length > 0 ? skillCounts : [18, 15, 12, 10, 9, 8, 16],
          backgroundColor: '#0284c7',
          borderRadius: 6,
        }],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        indexAxis: 'y',
        scales: {
          x: {
            beginAtZero: true,
            ticks: { precision: 0 },
            grid: { display: false },
          },
          y: {
            grid: { display: false },
          },
        },
        plugins: {
          legend: { display: false },
        },
      },
    });
  },

  // Initialize Radar / Multi-axis Score Breakdown Chart
  initScoreBreakdownChart: (canvasId, scores) => {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return null;

    const labels = ['Skill Match (35%)', 'TF-IDF Similarity (25%)', 'Experience (20%)', 'Education (10%)', 'Keywords (10%)'];
    const values = [
      scores.skill_score || 0,
      scores.tfidf_similarity !== undefined ? scores.tfidf_similarity * 100 : 0,
      scores.experience_score || 0,
      scores.education_score || 0,
      scores.keyword_score || 0,
    ];

    return new Chart(ctx, {
      type: 'radar',
      data: {
        labels,
        datasets: [{
          label: 'Candidate Match Profile',
          data: values,
          backgroundColor: 'rgba(37, 99, 235, 0.2)',
          borderColor: '#2563eb',
          pointBackgroundColor: '#2563eb',
          pointBorderColor: '#fff',
          pointHoverBackgroundColor: '#fff',
          pointHoverBorderColor: '#2563eb',
        }],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          r: {
            angleLines: { color: '#e2e8f0' },
            grid: { color: '#f1f5f9' },
            suggestedMin: 0,
            suggestedMax: 100,
            ticks: { stepSize: 20 },
          },
        },
        plugins: {
          legend: { display: false },
        },
      },
    });
  },
};
