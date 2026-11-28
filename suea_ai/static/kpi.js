/* SUEA AI — KPI Control Center */

(function () {
    "use strict";

    function fmt(n) {
        if (n == null) return "-";
        return Number(n).toLocaleString("th-TH");
    }

    function statusBadge(status) {
        var colors = {
            "UNVERIFIED": "#d29922",
            "ACK": "#3fb950",
            "NO_EVIDENCE": "#f85149",
            "VERIFIED": "#58a6ff",
        };
        var color = colors[status] || "#8b949e";
        return '<span style="color:' + color + ';font-weight:600">' + status + '</span>';
    }

    function loadKPI() {
        var container = document.getElementById("kpi-dashboard");
        if (!container) return;

        fetch("/api/kpi")
            .then(function (r) { return r.json(); })
            .then(function (data) {
                container.innerHTML = "";

                var header = document.createElement("div");
                header.className = "kpi-header";
                header.innerHTML =
                    '<span>Mode: <strong>' + data.mode + '</strong></span> · ' +
                    '<span>Read Only: <strong>' + data.read_only + '</strong></span> · ' +
                    '<span>Agents: <strong>' + data.agents.length + '</strong></span>';
                container.appendChild(header);

                var table = document.createElement("table");
                table.innerHTML =
                    "<thead><tr>" +
                    "<th>Agent</th><th>Status</th><th>ACK</th>" +
                    "<th>KPI Score</th><th>Last Report</th>" +
                    "</tr></thead>";
                var tbody = document.createElement("tbody");

                data.agents.forEach(function (agent) {
                    var tr = document.createElement("tr");
                    tr.innerHTML =
                        "<td>" + agent.agent + "</td>" +
                        "<td>" + statusBadge(agent.status) + "</td>" +
                        "<td>" + (agent.ack ? "Yes" : "No") + "</td>" +
                        "<td>" + (agent.kpi_score != null ? agent.kpi_score : "-") + "</td>" +
                        "<td>" + (agent.last_report || "-") + "</td>";
                    tbody.appendChild(tr);
                });

                table.appendChild(tbody);
                container.appendChild(table);
            })
            .catch(function () {
                container.textContent = "ไม่สามารถอ่านข้อมูล KPI ได้";
            });
    }

    function loadPolicy() {
        var container = document.getElementById("policy-info");
        if (!container) return;

        fetch("/api/kpi/policy")
            .then(function (r) { return r.json(); })
            .then(function (p) {
                container.innerHTML = "";
                var items = [
                    "Owner Control: " + p.owner_control,
                    "Private Mode: " + p.private_mode,
                    "Read Only: " + p.read_only,
                    "Free Only: " + p.free_only,
                    "KPI Enforcement: " + p.kpi_enforcement,
                    "ACK Required: " + p.ack_required,
                    "Evidence Required: " + p.evidence_required,
                    "Report Interval: " + p.report_interval_minutes + " min",
                    "Max Retries: " + p.max_retries,
                    "Block Fake Data: " + p.block_fake_data,
                    "Auto Spending: " + p.auto_spending,
                    "Owner Approval: " + p.owner_approval_required,
                    "Report To: " + p.report_destination,
                ];
                items.forEach(function (txt) {
                    var div = document.createElement("div");
                    div.className = "sec-item";
                    var parts = txt.split(": ");
                    div.innerHTML = "<strong>" + parts[0] + ":</strong> " + parts.slice(1).join(": ");
                    container.appendChild(div);
                });
            })
            .catch(function () {});
    }

    function loadTaskStats() {
        var container = document.getElementById("task-stats");
        if (!container) return;

        fetch("/api/tasks/stats")
            .then(function (r) { return r.json(); })
            .then(function (d) {
                container.innerHTML =
                    '<div class="card"><h3>Total</h3><span class="big-num">' + fmt(d.total) + '</span></div>' +
                    '<div class="card"><h3>Queued</h3><span class="big-num">' + fmt(d.queued) + '</span></div>' +
                    '<div class="card"><h3>Running</h3><span class="big-num">' + fmt(d.running) + '</span></div>' +
                    '<div class="card"><h3>Done</h3><span class="big-num">' + fmt(d.done) + '</span></div>' +
                    '<div class="card"><h3>Failed</h3><span class="big-num">' + fmt(d.failed) + '</span></div>';
            })
            .catch(function () {});
    }

    loadKPI();
    loadPolicy();
    loadTaskStats();
    setInterval(loadKPI, 60000);
    setInterval(loadTaskStats, 60000);
})();
