// License Status Pie Chart
const ctx1 = document.getElementById("statusChart");
if (ctx1) {
    new Chart(ctx1, {
        type: "doughnut",
        data: {
            labels: ["Active", "Expired", "Trial"],
            datasets: [{
                data: [60, 25, 15], // Example data
                backgroundColor: ["#28a745", "#dc3545", "#ffc107"],
                hoverOffset: 10
            }]
        },
        options: { responsive: true }
    });
}

// Expiry Trend Line Chart
const ctx2 = document.getElementById("expiryChart");
if (ctx2) {
    new Chart(ctx2, {
        type: "line",
        data: {
            labels: ["Jan", "Feb", "Mar", "Apr", "May", "Jun"],
            datasets: [{
                label: "Expirations",
                data: [5, 7, 3, 9, 4, 6],
                borderColor: "#007bff",
                backgroundColor: "rgba(0, 123, 255, 0.2)",
                fill: true,
                tension: 0.3
            }]
        },
        options: {
            responsive: true,
            plugins: { legend: { display: false } }
        }
    });
}
