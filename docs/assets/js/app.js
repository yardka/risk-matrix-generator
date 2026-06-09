const API_BASE = document.querySelector('meta[name="api-base"]')?.getAttribute("content") || "http://localhost:8000";
const API = `${API_BASE}/api/v1`;

const RISK_CONFIG = {
    low:      { cls: "badge-low",      color: "var(--risk-low)",      label: "Bajo",      ciaColor: "#64748b" },
    medium:   { cls: "badge-medium",   color: "var(--risk-medium)",   label: "Medio",     ciaColor: "#eab308" },
    high:     { cls: "badge-high",     color: "var(--risk-high)",     label: "Alto",      ciaColor: "#f97316" },
    critical: { cls: "badge-critical", color: "var(--risk-critical)", label: "Crítico",   ciaColor: "#ef4444" },
};

function rc(level) {
    return RISK_CONFIG[level] || RISK_CONFIG.low;
}


async function apiGet(path) {
    const res = await fetch(`${API}${path}`);
    if (!res.ok) throw new Error(`Error ${res.status}: ${await res.text()}`);
    return res.json();
}

async function apiPost(path, body) {
    const res = await fetch(`${API}${path}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
    });
    if (!res.ok) {
        const err = await res.json().catch(() => ({ detail: res.statusText }));
        throw new Error(err.detail || `Error ${res.status}`);
    }
    return res.json();
}

function setButtonLoading(btn, loading) {
    btn.disabled = loading;
    btn.classList.toggle("loading", loading);
}


async function checkBackendHealth() {
    const badge = document.getElementById("backend-status");
    const dot   = badge.querySelector(".status-dot");
    const text  = badge.querySelector(".status-text");
    try {
        const data = await fetch(`${API_BASE}/`).then(r => r.json());
        badge.className = "status-badge status-online";
        text.textContent = "API en línea";
    } catch {
        badge.className = "status-badge status-offline";
        text.textContent = "API desconectada";
    }
}


function initTabs() {
    const buttons  = document.querySelectorAll(".tab-btn");
    const sections = document.querySelectorAll(".tab-section");

    buttons.forEach(btn => {
        btn.addEventListener("click", () => {
            const target = btn.dataset.tab;
            buttons.forEach(b => { b.classList.remove("active"); b.setAttribute("aria-selected", "false"); });
            sections.forEach(s => { s.classList.remove("active"); s.style.display = "none"; });
            btn.classList.add("active");
            btn.setAttribute("aria-selected", "true");
            const section = document.getElementById(`section-${target}`);
            section.classList.add("active");
            section.style.display = "block";
        });
    });
}


async function initMatrix() {
    const grid    = document.getElementById("matrix-grid");
    const xAxis   = document.getElementById("matrix-x-axis");
    const yAxis   = document.getElementById("matrix-y-axis");
    const tooltip = document.getElementById("matrix-tooltip");

    let data;
    try {
        data = await apiGet("/matrix");
    } catch {
        grid.innerHTML = `<p style="color:var(--risk-high);font-size:.85rem;padding:1rem;">No se pudo cargar la matriz. Verifica que el backend esté activo.</p>`;
        return;
    }

    data.probability_axis.forEach(({ value, label }) => {
        const el = document.createElement("div");
        el.className = "y-axis-label";
        el.textContent = `${value} — ${label}`;
        yAxis.appendChild(el);
    });

    data.impact_axis.forEach(({ value, label }) => {
        const el = document.createElement("div");
        el.className = "axis-label";
        el.innerHTML = `<span>${value}</span><br><span style="font-size:.6rem">${label}</span>`;
        xAxis.appendChild(el);
    });

    data.matrix.forEach(row => {
        row.forEach(cell => {
            const div = document.createElement("div");
            div.className = "matrix-cell";
            div.setAttribute("role", "gridcell");
            div.setAttribute("tabindex", "0");
            div.setAttribute("aria-label", `P=${cell.probability} I=${cell.impact} Score=${cell.score} Nivel=${cell.level}`);
            div.style.background = `${cell.color}28`;
            div.style.borderColor = `${cell.color}55`;
            div.innerHTML = `<span class="cell-score" style="color:${cell.color}">${cell.score}</span><span class="cell-level" style="color:${cell.color}">${rc(cell.level).label}</span>`;

            function showTooltip(e) {
                const cx = e.touches ? e.touches[0].pageX : e.pageX;
                const cy = e.touches ? e.touches[0].pageY : e.pageY;
                tooltip.innerHTML = `
                    <div class="tooltip-arrow" aria-hidden="true"></div>
                    <div class="tooltip-title" style="color:${cell.color}">${cell.score} — ${rc(cell.level).label}</div>
                    <div class="tooltip-row"><span>Probabilidad</span><span>${cell.probability} (${cell.probability_label})</span></div>
                    <div class="tooltip-row"><span>Impacto</span><span>${cell.impact} (${cell.impact_label})</span></div>
                `;
                const x = cx + 14;
                const y = cy - 10;
                const tw = tooltip.offsetWidth;
                const vw = window.innerWidth;
                tooltip.style.left = (x + tw > vw ? x - tw - 28 : x) + "px";
                tooltip.style.top  = y + "px";
                tooltip.classList.add("visible");
                tooltip.setAttribute("aria-hidden", "false");
            }

            function hideTooltip() {
                tooltip.classList.remove("visible");
                tooltip.setAttribute("aria-hidden", "true");
            }

            div.addEventListener("mouseenter", showTooltip);
            div.addEventListener("mousemove", showTooltip);
            div.addEventListener("mouseleave", hideTooltip);
            div.addEventListener("touchstart", (e) => { showTooltip(e); e.preventDefault(); }, { passive: true });
            div.addEventListener("touchend", hideTooltip);

            grid.appendChild(div);
        });
    });
}


function initClassifyForm() {
    const form   = document.getElementById("form-classify");
    const result = document.getElementById("result-classify");
    const btn    = document.getElementById("btn-classify");

    form.addEventListener("submit", async (e) => {
        e.preventDefault();
        const name  = document.getElementById("cl-asset-name").value.trim();
        const type  = document.getElementById("cl-asset-type").value;
        const conf  = document.getElementById("cl-conf").value;
        const integ = document.getElementById("cl-integ").value;
        const avail = document.getElementById("cl-avail").value;

        if (!name || !type || !conf || !integ || !avail) return;

        setButtonLoading(btn, true);
        try {
            const data = await apiPost("/assets/classify", {
                asset_name: name, asset_type: type,
                confidentiality: conf, integrity: integ, availability: avail,
            });
            renderClassifyResult(result, data);
        } catch (err) {
            result.innerHTML = `<div class="result-placeholder"><p style="color:var(--risk-high)">${err.message}</p></div>`;
        } finally {
            setButtonLoading(btn, false);
        }
    });
}

function renderClassifyResult(container, d) {
    const tpl = document.getElementById("tpl-classify-result");
    const el  = tpl.content.cloneNode(true);

    const cfg = rc(d.criticality);
    const pct = Math.round((d.cia_score / 12) * 100);

    el.querySelector(".classify-asset-name").textContent = d.asset_name;
    el.querySelector(".classify-asset-type").textContent = d.asset_type;
    const badge = el.querySelector(".criticality-badge");
    badge.className = `criticality-badge ${cfg.cls}`;
    badge.textContent = `Criticidad: ${cfg.label.toUpperCase()}`;

    const ciaValues = el.querySelectorAll(".cia-value");
    ciaValues[0].textContent = d.confidentiality.toUpperCase();
    ciaValues[0].style.color = rc(d.confidentiality).ciaColor;
    ciaValues[1].textContent = d.integrity.toUpperCase();
    ciaValues[1].style.color = rc(d.integrity).ciaColor;
    ciaValues[2].textContent = d.availability.toUpperCase();
    ciaValues[2].style.color = rc(d.availability).ciaColor;

    const scoreVal = el.querySelector(".score-bar-value");
    scoreVal.textContent = `${d.cia_score} / 12`;
    scoreVal.style.color = cfg.color;

    const barFill = el.querySelector(".score-bar-fill");
    barFill.style.background = cfg.color;
    requestAnimationFrame(() => {
        setTimeout(() => { barFill.style.width = pct + "%"; }, 50);
    });

    el.querySelector(".rationale-box").textContent = d.rationale;

    container.innerHTML = "";
    container.appendChild(el);
}


function initRiskForm() {
    const form   = document.getElementById("form-risk");
    const result = document.getElementById("result-risk");
    const btn    = document.getElementById("btn-risk");
    const errMsg = document.getElementById("rk-slider-error");

    function updateSliderColor(sliderId, outputId) {
        const slider = document.getElementById(sliderId);
        const val = parseInt(slider.value);
        const colors = ["#22c55e", "#eab308", "#f97316", "#ef4444"];
        const color = val <= 2 ? colors[0] : val === 3 ? colors[1] : val === 4 ? colors[2] : colors[3];
        slider.style.background = `linear-gradient(90deg, ${color} 0%, ${color}66 ${(val/5)*100}%, rgba(255,255,255,0.1) ${(val/5)*100}%)`;
        const out = document.getElementById(outputId);
        out.style.background = color;
    }

    const sliders = [
        { slider: "rk-iprob", output: "rk-iprob-val" },
        { slider: "rk-iimp",  output: "rk-iimp-val"  },
        { slider: "rk-rprob", output: "rk-rprob-val" },
        { slider: "rk-rimp",  output: "rk-rimp-val"  },
    ];

    sliders.forEach(({ slider, output }) => {
        const el = document.getElementById(slider);
        updateSliderColor(slider, output);
        el.addEventListener("input", () => {
            document.getElementById(output).textContent = el.value;
            updateSliderColor(slider, output);
            validateResidual();
        });
    });

    function validateResidual() {
        const ip = +document.getElementById("rk-iprob").value;
        const ii = +document.getElementById("rk-iimp").value;
        const rp = +document.getElementById("rk-rprob").value;
        const ri = +document.getElementById("rk-rimp").value;
        const invalid = rp > ip || ri > ii;
        errMsg.style.display = invalid ? "block" : "none";
        return !invalid;
    }

    form.addEventListener("submit", async (e) => {
        e.preventDefault();
        if (!validateResidual()) return;

        const threat = document.getElementById("rk-threat").value.trim();
        const asset  = document.getElementById("rk-asset").value.trim();
        if (!threat || !asset) return;

        setButtonLoading(btn, true);
        try {
            const data = await apiPost("/risks/calculate", {
                threat_name: threat, asset_name: asset,
                intrinsic_probability: +document.getElementById("rk-iprob").value,
                intrinsic_impact:      +document.getElementById("rk-iimp").value,
                residual_probability:  +document.getElementById("rk-rprob").value,
                residual_impact:       +document.getElementById("rk-rimp").value,
            });
            renderRiskResult(result, data);
        } catch (err) {
            result.innerHTML = `<div class="result-placeholder"><p style="color:var(--risk-high)">${err.message}</p></div>`;
        } finally {
            setButtonLoading(btn, false);
        }
    });
}

function renderRiskResult(container, d) {
    const tpl = document.getElementById("tpl-risk-result");
    const el  = tpl.content.cloneNode(true);

    const ic = rc(d.intrinsic.level);
    const rc2 = rc(d.residual.level);
    const pct = Math.min(100, d.reduction_pct);

    el.querySelector(".risk-threat-name").textContent = d.threat_name;
    el.querySelector(".risk-asset-name").textContent = `Sobre: ${d.asset_name}`;

    const cards = el.querySelectorAll(".risk-card");
    const setCard = (card, data, cfg) => {
        card.style.borderColor = `${cfg.color.replace("var(", "").replace(")", "")}44`;
        card.style.background = `${cfg.color.replace("var(", "").replace(")", "")}10`;
        card.querySelector(".risk-score-big").textContent = data.score;
        card.querySelector(".risk-score-big").style.color = cfg.color;
        const badge = card.querySelector(".risk-level-badge");
        badge.textContent = cfg.label.toUpperCase();
        badge.style.color = cfg.color;
        card.querySelector(".risk-sub-formula").textContent = `P=${data.probability} x I=${data.impact}`;
        card.querySelector(".risk-sub-labels").textContent = `${data.probability_label} / ${data.impact_label}`;
    };
    setCard(cards[0], d.intrinsic, ic);
    setCard(cards[1], d.residual, rc2);

    const redVal = el.querySelector(".reduction-value");
    redVal.textContent = `-${d.risk_reduction} pts (${d.reduction_pct}%)`;

    const barFill = el.querySelector(".reduction-bar-fill");
    requestAnimationFrame(() => {
        setTimeout(() => { barFill.style.width = pct + "%"; }, 50);
    });

    container.innerHTML = "";
    container.appendChild(el);
}


function initControlsForm() {
    const form   = document.getElementById("form-controls");
    const result = document.getElementById("result-controls");
    const btn    = document.getElementById("btn-controls");

    let controlsData = null;
    let activeCtrlTab = "immediate";

    form.addEventListener("submit", async (e) => {
        e.preventDefault();
        const level = document.getElementById("ct-risk-level").value;
        const type  = document.getElementById("ct-asset-type").value;
        if (!level || !type) return;

        setButtonLoading(btn, true);
        try {
            const data = await apiPost("/controls/recommend", { risk_level: level, asset_type: type });
            controlsData = data;
            activeCtrlTab = data.immediate.length > 0 ? "immediate" : (data.short_term.length > 0 ? "short_term" : "long_term");
            renderControlsResult(result, data);
        } catch (err) {
            result.innerHTML = `<div class="result-placeholder"><p style="color:var(--risk-high)">${err.message}</p></div>`;
        } finally {
            setButtonLoading(btn, false);
        }
    });

    function renderControlsList(controls) {
        const container = document.getElementById("controls-list-container");
        if (!container) return;

        if (!controls || controls.length === 0) {
            container.innerHTML = `<div class="no-controls">No hay controles en esta categoría.</div>`;
            return;
        }

        container.innerHTML = "";
        const tpl = document.getElementById("tpl-control-item");
        controls.forEach(c => {
            const el = tpl.content.cloneNode(true);
            el.querySelector(".control-id").textContent = c.id;
            el.querySelector(".control-framework").textContent = c.framework;
            const cat = el.querySelector(".control-category");
            cat.textContent = c.category;
            const lower = (c.category || "").toLowerCase();
            if (lower.includes("prevent")) cat.classList.add("cat-preventivo");
            else if (lower.includes("detect")) cat.classList.add("cat-detectivo");
            else if (lower.includes("correct")) cat.classList.add("cat-correctivo");
            el.querySelector(".control-name").textContent = c.name;
            el.querySelector(".control-desc").textContent = c.description;
            container.appendChild(el);
        });
    }

    function renderControlsResult(container, d) {
        const tpl = document.getElementById("tpl-controls-result");
        const el = tpl.content.cloneNode(true);

        el.querySelector(".treatment-plan").textContent = d.treatment_plan;
        const summary = el.querySelector(".controls-summary");
        summary.innerHTML = `<strong>${d.total_controls}</strong> controles recomendados para nivel <strong>${rc(d.risk_level).label.toUpperCase()}</strong> · activo tipo <strong>${d.asset_type}</strong>`;

        const tabsContainer = el.querySelector(".controls-tabs");
        const tabs = [
            { key: "immediate",  label: "Inmediatos",  count: d.immediate.length },
            { key: "short_term", label: "Corto plazo", count: d.short_term.length },
            { key: "long_term",  label: "Largo plazo", count: d.long_term.length },
        ];
        tabs.forEach(({ key, label, count }) => {
            const btn2 = document.createElement("button");
            btn2.className = `ctrl-tab ${activeCtrlTab === key ? "active" : ""}`;
            btn2.dataset.ctrlTab = key;
            btn2.textContent = `${label} (${count})`;
            btn2.addEventListener("click", () => {
                activeCtrlTab = key;
                tabsContainer.querySelectorAll(".ctrl-tab").forEach(t => t.classList.remove("active"));
                btn2.classList.add("active");
                renderControlsList(d[key]);
            });
            tabsContainer.appendChild(btn2);
        });

        container.innerHTML = "";
        container.appendChild(el);
        renderControlsList(d[activeCtrlTab]);
    }
}


document.addEventListener("DOMContentLoaded", async () => {
    checkBackendHealth();
    initTabs();
    await initMatrix();
    initClassifyForm();
    initRiskForm();
    initControlsForm();
});
