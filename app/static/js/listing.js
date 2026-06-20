// Autosave every 30 seconds
let autosaveInterval = setInterval(saveDraft, 30000);

function getFormData() {
  const form = document.getElementById("listingForm");
  const data = new FormData(form);
  const obj = {};
  for (const [k, v] of data.entries()) obj[k] = v;
  obj.allow_offers = form.querySelector('[name=allow_offers]')?.checked || false;
  return obj;
}

function saveDraft() {
  const status = document.getElementById("autosaveStatus");
  status.textContent = "Saving…";
  fetch(SAVE_URL, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(getFormData()),
  })
    .then(r => r.json())
    .then(d => {
      if (d.ok) status.textContent = "Draft saved " + new Date().toLocaleTimeString();
      else status.textContent = "Save failed";
    })
    .catch(() => { status.textContent = "Save failed"; });
}

document.getElementById("saveDraftBtn")?.addEventListener("click", () => {
  saveDraft();
});

// Price refresh
document.getElementById("refreshPrice")?.addEventListener("click", function () {
  this.disabled = true;
  this.innerHTML = '<i class="bi bi-arrow-clockwise spin"></i>';
  fetch(PRICE_URL)
    .then(r => r.json())
    .then(d => {
      document.getElementById("priceLow").textContent = d.low ? "$" + d.low.toFixed(2) : "—";
      document.getElementById("priceMedian").textContent = d.median ? "$" + d.median.toFixed(2) : "—";
      document.getElementById("priceHigh").textContent = d.high ? "$" + d.high.toFixed(2) : "—";
      document.getElementById("priceCount").textContent = d.num_for_sale ?? "—";
    })
    .finally(() => {
      this.disabled = false;
      this.innerHTML = '<i class="bi bi-arrow-clockwise"></i> Refresh';
    });
});

// G hotkey opens condition guide
document.addEventListener("keydown", e => {
  if (e.key === "g" || e.key === "G") {
    const active = document.activeElement;
    if (active.tagName === "INPUT" || active.tagName === "TEXTAREA") return;
    const modal = new bootstrap.Modal(document.getElementById("conditionGuideModal"));
    modal.show();
  }
});
