// confirm Modal
document.addEventListener("DOMContentLoaded", function () {
  let confirmModal = new bootstrap.Modal(
    document.getElementById("confirmModal"),
  );
  let confirmBtn = document.getElementById("confirmBtn");
  let confirmMessage = document.getElementById("confirmMessage");
  document.querySelectorAll("[data-confirm]").forEach((btn) => {
    btn.addEventListener("click", function (e) {
      e.preventDefault();

      const message = this.getAttribute("data-confirm");
      const form = this.closest("form");

      confirmMessage.textContent = message;

      confirmBtn.onclick = () => {
        form.submit();
      };

      confirmModal.show();
    });
  });
});

// toast auto-dismiss
document.querySelectorAll(".toast").forEach((toastEl) => {
  new bootstrap.Toast(toastEl, { delay: 3000 }).show();
});

// feedback ratings 
const stars = document.querySelectorAll(".star");
const ratingInput = document.getElementById("rating-value");
stars.forEach((star) => {
  star.addEventListener("click", function () {
    let rating = this.dataset.value;

    ratingInput.value = rating;

    stars.forEach((s) => {
      s.classList.remove("active");
    });

    for (let i = 0; i < rating; i++) {
      stars[i].classList.add("active");
    }
  });
});

// control sidebar 
const toggleBtn = document.getElementById("sidebarToggle");
const sidebar = document.getElementById("sidebar");
const overlay = document.getElementById("sidebarOverlay");

if (toggleBtn) {
  toggleBtn.addEventListener("click", () => {
    sidebar.classList.toggle("active");
    overlay.classList.toggle("active");
  });
}

if (overlay) {
  overlay.addEventListener("click", () => {
    sidebar.classList.remove("active");
    overlay.classList.remove("active");
  });
}

