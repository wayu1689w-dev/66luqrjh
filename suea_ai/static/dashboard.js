/* SUEA AI Dashboard v008 — Frontend */

(function () {
    "use strict";

    function fmt(n) {
        if (n == null) return "-";
        return Number(n).toLocaleString("th-TH");
    }

    function updateClock() {
        var now = new Date();
        var el = document.getElementById("clock");
        if (el) el.textContent = now.toLocaleString("th-TH", { timeZone: "Asia/Bangkok" });
    }
    setInterval(updateClock, 1000);
    updateClock();

    /* ── Dashboard summary ──────────────────────── */
    fetch("/api/dashboard")
        .then(function (r) { return r.json(); })
        .then(function (d) {
            document.getElementById("num-products").textContent = fmt(d.products);
            document.getElementById("num-videos").textContent = fmt(d.videos);
            document.getElementById("num-ads").textContent = fmt(d.ads_records);
            document.getElementById("num-connectors").textContent =
                d.connectors_ready + "/" + d.connectors_total;
        })
        .catch(function () {});

    /* ── Connectors ─────────────────────────────── */
    fetch("/api/connectors")
        .then(function (r) { return r.json(); })
        .then(function (data) {
            var container = document.getElementById("connectors-list");
            var keys = Object.keys(data);
            keys.forEach(function (k) {
                var c = data[k];
                var div = document.createElement("div");
                div.className = "conn-item";
                div.innerHTML =
                    '<span class="dot ' + c.status + '"></span>' +
                    '<span class="conn-name">' + (c.name || k) + '</span>' +
                    '<span class="conn-env">' + c.status +
                    (c.env_key ? " — " + c.env_key : "") + '</span>';
                container.appendChild(div);
            });
        })
        .catch(function () {});

    /* ── Products ───────────────────────────────── */
    fetch("/api/products?limit=20&sort=score")
        .then(function (r) { return r.json(); })
        .then(function (rows) {
            var tbody = document.querySelector("#products-table tbody");
            rows.forEach(function (p, i) {
                var tr = document.createElement("tr");
                tr.innerHTML =
                    "<td>" + (i + 1) + "</td>" +
                    "<td>" + (p.name || "-") + "</td>" +
                    "<td>" + (p.category || "-") + "</td>" +
                    "<td>" + fmt(p.gmv) + "</td>" +
                    "<td>" + fmt(p.orders) + "</td>" +
                    "<td>" + (p.commission_rate || 0) + "%</td>" +
                    "<td>" + (p.conversion_rate || 0) + "%</td>" +
                    "<td>" + (p.score || 0) + "</td>";
                tbody.appendChild(tr);
            });
        })
        .catch(function () {});

    /* ── Videos ─────────────────────────────────── */
    fetch("/api/videos/performance")
        .then(function (r) { return r.json(); })
        .then(function (d) {
            var container = document.getElementById("video-stats");
            var items = [
                { label: "Total Videos", val: d.total_videos },
                { label: "Total Views", val: d.total_views },
                { label: "Total Likes", val: d.total_likes },
                { label: "Avg Views", val: d.avg_views },
            ];
            items.forEach(function (item) {
                var div = document.createElement("div");
                div.className = "card";
                div.innerHTML =
                    '<h3>' + item.label + '</h3>' +
                    '<span class="big-num">' + fmt(item.val) + '</span>';
                container.appendChild(div);
            });
        })
        .catch(function () {});

    fetch("/api/videos?limit=20")
        .then(function (r) { return r.json(); })
        .then(function (rows) {
            var tbody = document.querySelector("#videos-table tbody");
            rows.forEach(function (v, i) {
                var tr = document.createElement("tr");
                tr.innerHTML =
                    "<td>" + (i + 1) + "</td>" +
                    "<td>" + (v.title || v.video_id || "-") + "</td>" +
                    "<td>" + fmt(v.views) + "</td>" +
                    "<td>" + fmt(v.likes) + "</td>" +
                    "<td>" + fmt(v.comments) + "</td>" +
                    "<td>" + fmt(v.shares) + "</td>";
                tbody.appendChild(tr);
            });
        })
        .catch(function () {});

    /* ── Security ───────────────────────────────── */
    fetch("/api/security/policy")
        .then(function (r) { return r.json(); })
        .then(function (d) {
            var container = document.getElementById("security-info");
            var items = [
                "Mode: " + d.mode,
                "Billing: " + (d.billing_enabled ? "ON" : "OFF"),
                "Public Access: " + (d.public_access ? "ON" : "OFF"),
                "Auto Publish: " + (d.auto_publish ? "ON" : "OFF"),
                "Kill Switches: " + d.kill_switches,
                "RBAC Tiers: " + d.rbac_tiers,
                "Risk Threshold: " + d.risk_approval_threshold,
                "Blocked: " + d.blocked_actions.join(", "),
            ];
            items.forEach(function (txt) {
                var div = document.createElement("div");
                div.className = "sec-item";
                div.innerHTML = "<strong>" + txt.split(":")[0] + ":</strong> " + txt.split(":").slice(1).join(":");
                container.appendChild(div);
            });
        })
        .catch(function () {});
})();
