const selectAll = document.getElementById("selectAll");
const submitBtn = document.getElementById("submitAllBtn");
const progressArea = document.getElementById("progressArea");
const progressBar = document.getElementById("progressBar");
const progressLog = document.getElementById("progressLog");

selectAll?.addEventListener("change", () => {
  document.querySelectorAll(".row-check").forEach(cb => cb.checked = selectAll.checked);
});

submitBtn?.addEventListener("click", async () => {
  const checked = Array.from(document.querySelectorAll(".row-check:checked")).map(cb => parseInt(cb.value));
  if (!checked.length) { alert("Select at least one item."); return; }
  if (!confirm(`Submit ${checked.length} listing(s) to Discogs?`)) return;

  submitBtn.disabled = true;
  progressArea.classList.remove("d-none");
  progressLog.innerHTML = "";

  const resp = await fetch("/listing/bulk/submit", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ draft_ids: checked }),
  });
  const data = await resp.json();

  data.results.forEach((r, i) => {
    const pct = Math.round(((i + 1) / data.results.length) * 100);
    progressBar.style.width = pct + "%";

    const statusCell = document.getElementById("status-" + r.draft_id);
    if (r.ok) {
      progressLog.insertAdjacentHTML("beforeend",
        `<div class="text-success"><i class="bi bi-check-circle me-1"></i>${r.title} — Listed #${r.listing_id}</div>`);
      if (statusCell) statusCell.innerHTML = '<span class="badge bg-success">Listed</span>';
    } else {
      progressLog.insertAdjacentHTML("beforeend",
        `<div class="text-danger"><i class="bi bi-x-circle me-1"></i>${r.title} — ${r.error}</div>`);
      if (statusCell) statusCell.innerHTML = `<span class="badge bg-danger" title="${r.error}">Failed</span>`;
    }
  });

  const successCount = data.results.filter(r => r.ok).length;
  progressLog.insertAdjacentHTML("beforeend",
    `<div class="fw-semibold mt-2">${successCount}/${data.results.length} listed successfully.</div>`);
  submitBtn.disabled = false;
});
