const dropZone = document.getElementById("dropZone");
const fileInput = document.getElementById("imageFileInput");
const previews = document.getElementById("imagePreviews");

if (dropZone) {
  dropZone.addEventListener("click", () => fileInput.click());
  dropZone.addEventListener("dragover", e => { e.preventDefault(); dropZone.classList.add("drag-over"); });
  dropZone.addEventListener("dragleave", () => dropZone.classList.remove("drag-over"));
  dropZone.addEventListener("drop", e => {
    e.preventDefault();
    dropZone.classList.remove("drag-over");
    uploadFiles(e.dataTransfer.files);
  });
  fileInput.addEventListener("change", () => uploadFiles(fileInput.files));
}

function uploadFiles(files) {
  const currentCount = previews.querySelectorAll(".image-preview-item").length;
  const remaining = 3 - currentCount;
  const toUpload = Array.from(files).slice(0, remaining);
  toUpload.forEach(file => uploadOne(file));
}

function uploadOne(file) {
  const fd = new FormData();
  fd.append("image", file);
  const tmpId = "tmp-" + Date.now();
  const reader = new FileReader();
  reader.onload = e => {
    previews.insertAdjacentHTML("beforeend",
      `<div class="image-preview-item loading" id="${tmpId}">
         <img src="${e.target.result}" alt="">
         <div class="upload-spinner"><div class="spinner-border spinner-border-sm text-warning"></div></div>
       </div>`
    );
  };
  reader.readAsDataURL(file);

  fetch(UPLOAD_URL, { method: "POST", body: fd })
    .then(r => r.json())
    .then(d => {
      const el = document.getElementById(tmpId);
      if (d.ok) {
        el.classList.remove("loading");
        el.dataset.index = d.index;
        el.insertAdjacentHTML("beforeend",
          `<button type="button" class="btn-remove-img"
            data-index="${d.index}"
            data-url="/listing/image/delete/${DRAFT_ID}/${d.index}">
            <i class="bi bi-x"></i>
           </button>`
        );
        el.querySelector(".upload-spinner")?.remove();
      } else {
        el.remove();
        alert("Upload failed: " + d.error);
      }
    })
    .catch(() => {
      document.getElementById(tmpId)?.remove();
      alert("Upload failed.");
    });
}

previews.addEventListener("click", e => {
  const btn = e.target.closest(".btn-remove-img");
  if (!btn) return;
  const url = btn.dataset.url;
  fetch(url, { method: "POST" })
    .then(() => btn.closest(".image-preview-item").remove());
});
