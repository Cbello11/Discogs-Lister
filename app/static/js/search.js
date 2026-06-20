let currentPage = 1;
let debounceTimer = null;

const input = document.getElementById("searchInput");
const formatFilter = document.getElementById("formatFilter");
const resultsEl = document.getElementById("searchResults");
const statusEl = document.getElementById("searchStatus");
const paginationEl = document.getElementById("pagination");

function doSearch(page = 1) {
  const q = input.value.trim();
  if (!q) {
    resultsEl.innerHTML = "";
    statusEl.textContent = "";
    paginationEl.innerHTML = "";
    return;
  }
  currentPage = page;
  statusEl.textContent = "Searching…";
  resultsEl.innerHTML = "";

  const params = new URLSearchParams({ q, format: formatFilter.value, page });
  fetch("/api/search?" + params)
    .then(r => r.json())
    .then(data => {
      if (data.error) { statusEl.textContent = "Error: " + data.error; return; }
      statusEl.textContent = data.total ? `${data.total.toLocaleString()} results` : "No results found.";
      renderResults(data.results);
      renderPagination(data.total, data.per_page, page);
    })
    .catch(() => { statusEl.textContent = "Search failed. Check your connection."; });
}

function renderResults(results) {
  if (!results.length) { resultsEl.innerHTML = ""; return; }
  resultsEl.innerHTML = results.map(r => `
    <div class="col-sm-6 col-lg-4">
      <div class="card h-100 border-0 shadow-sm">
        <div class="d-flex">
          <img src="${r.thumb || '/static/img/no-cover.svg'}" alt="cover"
               class="rounded-start" style="width:80px;height:80px;object-fit:cover"
               onerror="this.src='/static/img/no-cover.svg'">
          <div class="card-body py-2 px-3">
            <div class="fw-semibold small" style="line-height:1.3">${escHtml(r.title)}</div>
            <div class="text-muted small">${escHtml(r.artist)}</div>
            <div class="text-muted" style="font-size:.75rem">
              ${r.year ? r.year + " · " : ""}${escHtml(r.format)}
            </div>
            <a href="/listing/new?release_id=${r.id}" class="btn btn-warning btn-sm mt-1 fw-semibold">
              List This
            </a>
          </div>
        </div>
      </div>
    </div>
  `).join("");
}

function renderPagination(total, perPage, page) {
  const pages = Math.ceil(total / perPage);
  if (pages <= 1) { paginationEl.innerHTML = ""; return; }
  const maxBtns = 7;
  let html = "";
  if (page > 1) html += `<button class="btn btn-sm btn-outline-secondary" onclick="doSearch(${page-1})">‹</button>`;
  for (let p = Math.max(1, page - 3); p <= Math.min(pages, page + 3); p++) {
    html += `<button class="btn btn-sm ${p === page ? "btn-warning" : "btn-outline-secondary"}"
              onclick="doSearch(${p})">${p}</button>`;
  }
  if (page < pages) html += `<button class="btn btn-sm btn-outline-secondary" onclick="doSearch(${page+1})">›</button>`;
  paginationEl.innerHTML = html;
}

function escHtml(str) {
  return String(str || "").replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;");
}

input.addEventListener("input", () => {
  clearTimeout(debounceTimer);
  debounceTimer = setTimeout(() => doSearch(1), 300);
});
formatFilter.addEventListener("change", () => doSearch(1));
document.getElementById("searchBtn").addEventListener("click", () => doSearch(1));
input.addEventListener("keydown", e => { if (e.key === "Enter") doSearch(1); });
