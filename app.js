const DISEASE_LABELS = {
  diabetes: "Diabetes", hypertension: "Hypertension (high BP)", high_cholesterol: "High cholesterol",
  heart_disease: "Heart disease", thyroid: "Thyroid", pcos: "PCOS / PCOD", anemia: "Anemia",
  obesity: "Obesity", kidney_disease: "Kidney disease", gastritis_acidity: "Gastritis / acidity",
  gout_uric_acid: "Gout / uric acid", lactose_intolerance: "Lactose intolerance",
  gluten_intolerance: "Gluten intolerance",
};
const ICON = { wake: "⏰", exercise: "🏃", meal: "🍽️", water: "💧", walk: "🚶", medicine: "💊", tip: "✨", sleep: "😴" };
const $ = (s) => document.querySelector(s);
const esc = (s) => String(s).replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));

// build disease checkboxes
$("#diseaseChips").innerHTML = Object.entries(DISEASE_LABELS).map(([k, v]) =>
  `<label class="chip"><input type="checkbox" name="disease" value="${k}"><span>${v}</span></label>`).join("");

let DATA = null, activeDay = 0;

$("#form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const f = new FormData(e.target);
  const body = {
    name: (f.get("name") || "").trim() || "Friend",
    age: +f.get("age"), gender: f.get("gender"),
    height_cm: +f.get("height_cm"), weight_kg: +f.get("weight_kg"),
    diet: f.get("diet"), goal: f.get("goal"), dislikes: f.get("dislikes") || "",
    diseases: f.getAll("disease"),
    activity_level: +f.get("activity_level"), wake_time: f.get("wake_time"),
    sleep_hours: +f.get("sleep_hours"), water_litres: +f.get("water_litres"),
    junk_food_per_week: +f.get("junk_food_per_week"),
  };
  const btn = $("#go"), msg = $("#msg");
  btn.disabled = true; btn.textContent = "Building your plan…"; msg.textContent = "";
  try {
    const r = await fetch("/api/plan", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) });
    if (!r.ok) {
      const err = await r.json().catch(() => ({}));
      const d = err.detail;
      throw new Error(Array.isArray(d) ? d.map((x) => `${x.loc.slice(-1)}: ${x.msg}`).join("; ") : (d || "Server error"));
    }
    DATA = await r.json();
    activeDay = 0;
    render();
    $("#formSection").hidden = true;
    $("#report").hidden = false;
    window.scrollTo(0, 0);
  } catch (err) {
    msg.textContent = "Could not generate plan: " + err.message;
  } finally {
    btn.disabled = false; btn.textContent = "Generate my timetable";
  }
});

$("#back").onclick = () => { $("#report").hidden = true; $("#formSection").hidden = false; window.scrollTo(0, 0); };
$("#print").onclick = () => window.print();

function dayHTML(d) {
  const rows = d.events.map((e) => `
    <tr class="${e.kind}">
      <td class="t">${esc(e.time)}</td>
      <td><span class="ic">${ICON[e.kind] || "•"}</span>${esc(e.title)}${e.detail ? `<div class="d">${esc(e.detail)}</div>` : ""}</td>
      <td class="kc">${e.kcal ? e.kcal + " kcal" : ""}</td>
    </tr>`).join("");
  return `<div class="day"><h3>${esc(d.day)} <small>Planned meals ≈ ${d.total_kcal} kcal</small></h3><table>${rows}</table></div>`;
}

function render() {
  const { targets: t, assessment: a, profile: p } = DATA;
  $("#rTitle").textContent = `${p.name}'s weekly diet & lifestyle timetable`;
  const dis = p.diseases.length ? p.diseases.map((d) => DISEASE_LABELS[d]).join(", ") : "No health conditions selected";
  $("#rSub").textContent = `${p.diet.replace("_", "-")} diet · goal: ${t.goal_used.replace("_", " ")} · ${dis}`;

  $("#cards").innerHTML = [
    ["Health risk (ML)", a.risk_level, `confidence ${Math.round(Math.max(...Object.values(a.probabilities)) * 100)}%`, `risk-${a.risk_level}`],
    ["BMI", t.bmi, t.bmi_category, ""],
    ["Daily calories", t.calories, `BMR ${t.bmr} · TDEE ${t.tdee}`, ""],
    ["Protein", t.protein_g + " g", "per day", ""],
    ["Carbs / Fat", `${t.carbs_g} / ${t.fat_g} g`, "per day", ""],
    ["Water", (t.water_ml / 1000).toFixed(2).replace(/\.?0+$/, "") + " L", "per day", ""],
  ].map(([k, v, s, c]) => `<div class="card ${c}"><div class="k">${k}</div><div class="v">${v}</div><div class="s">${s}</div></div>`).join("");

  $("#warnBox").innerHTML = (DATA.warnings || []).map((w) => `<div class="alert">⚠️ ${esc(w)}</div>`).join("");
  $("#findings").innerHTML = a.findings.map((f) => `<li class="${f.level}">${esc(f.text)}</li>`).join("");

  $("#tabs").innerHTML = DATA.days.map((d, i) =>
    `<button class="tab ${i === activeDay ? "active" : ""}" data-i="${i}">${d.day.slice(0, 3)}</button>`).join("");
  document.querySelectorAll(".tab").forEach((b) => b.onclick = () => { activeDay = +b.dataset.i; render(); });
  $("#dayView").innerHTML = dayHTML(DATA.days[activeDay]);
  $("#allDays").innerHTML = DATA.days.map(dayHTML).join("");

  $("#guidance").innerHTML = DATA.guidance.length ? `<h2>Guidance for your health conditions</h2><div class="g-grid">` +
    DATA.guidance.map((g) => `<div class="g"><h3>${esc(g.label)}</h3>
      <h4 class="av">Avoid / limit</h4><ul>${g.avoid.map((x) => `<li>${esc(x)}</li>`).join("")}</ul>
      <h4 class="in">Include</h4><ul>${g.include.map((x) => `<li>${esc(x)}</li>`).join("")}</ul>
      <h4 class="ti">Tips</h4><ul>${g.tips.map((x) => `<li>${esc(x)}</li>`).join("")}</ul></div>`).join("") + `</div>` : "";
}
