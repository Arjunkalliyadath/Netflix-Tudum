/* Netflix Tudum - front-end interactivity
 * Handles: My List (localStorage), search filtering, genre chips,
 * show detail modal, hero rotation, navbar scroll state, row arrows,
 * scroll-reveal animations, and toast notifications.
 */

const MY_LIST_KEY = "netflixTudumMyList";

/* ---------- Catalog helpers ---------- */

function getCatalog() {
    const el = document.getElementById("show-catalog");
    if (!el) return [];
    try {
        return JSON.parse(el.textContent);
    } catch (e) {
        console.error("Could not parse show catalog", e);
        return [];
    }
}

function getShowById(id) {
    return getCatalog().find((s) => String(s.id) === String(id));
}

/* ---------- My List (localStorage) ---------- */

function getMyList() {
    try {
        const raw = localStorage.getItem(MY_LIST_KEY);
        return raw ? JSON.parse(raw) : [];
    } catch (e) {
        return [];
    }
}

function saveMyList(list) {
    localStorage.setItem(MY_LIST_KEY, JSON.stringify(list));
}

function isInMyList(id) {
    return getMyList().includes(Number(id));
}

function toggleMyList(id) {
    id = Number(id);
    let list = getMyList();
    let added;
    if (list.includes(id)) {
        list = list.filter((x) => x !== id);
        added = false;
    } else {
        list.push(id);
        added = true;
    }
    saveMyList(list);
    refreshListButtons();

    const show = getShowById(id);
    if (show) {
        showToast(
            added ? `Added "${show.title}" to My List` : `Removed "${show.title}" from My List`,
            added ? "success" : "secondary"
        );
    }
    return added;
}

function refreshListButtons() {
    document.querySelectorAll(".list-btn, #modalListBtn").forEach((btn) => {
        const id = btn.dataset.id || document.getElementById("modalListBtn").dataset.id;
        if (!id) return;
        const inList = isInMyList(id);
        const icon = btn.querySelector("i");
        if (icon) {
            icon.className = inList ? "fas fa-check" : "fas fa-plus";
        }
        btn.classList.toggle("in-list", inList);
        btn.title = inList ? "Remove from My List" : "Add to My List";
    });
}

/* ---------- My List page rendering ---------- */

function renderMyListPage() {
    const grid = document.getElementById("myListGrid");
    const empty = document.getElementById("myListEmpty");
    if (!grid) return;

    const ids = getMyList();
    const catalog = getCatalog();
    const shows = ids
        .map((id) => catalog.find((s) => s.id === id))
        .filter(Boolean);

    if (shows.length === 0) {
        empty.classList.remove("d-none");
        grid.classList.add("d-none");
        return;
    }

    empty.classList.add("d-none");
    grid.classList.remove("d-none");

    grid.innerHTML = shows
        .map(
            (show) => `
        <div class="col-6 col-md-4 col-lg-3">
            <div class="show-card reveal in-view" data-id="${show.id}" data-title="${show.title.toLowerCase()}" data-genre="${show.genre}">
                <div class="show-card-media">
                    <img src="${show.poster_url}" alt="${show.title}" loading="lazy">
                    <div class="show-card-overlay">
                        <div class="show-card-actions">
                            <button type="button" class="icon-btn play-btn" data-id="${show.id}" title="More info"><i class="fas fa-play"></i></button>
                            <button type="button" class="icon-btn list-btn" data-id="${show.id}" title="Remove from My List"><i class="fas fa-check"></i></button>
                            <button type="button" class="icon-btn info-btn" data-id="${show.id}" title="More info"><i class="fas fa-chevron-down"></i></button>
                        </div>
                        <p class="show-card-title">${show.title}</p>
                        <div class="show-card-meta">
                            <span class="match-badge">${show.match_score}% Match</span>
                            <span class="maturity-badge">${show.maturity_rating}</span>
                            <span class="year-badge">${show.release_year}</span>
                        </div>
                    </div>
                </div>
            </div>
        </div>`
        )
        .join("");

    attachCardHandlers();
    refreshListButtons();
}

/* ---------- Show detail modal ---------- */

function openShowModal(id) {
    const show = getShowById(id);
    if (!show) return;

    document.getElementById("modalBackdrop").src = show.backdrop_url || show.poster_url;
    document.getElementById("modalTitle").textContent = show.title;
    document.getElementById("modalTagline").textContent = show.tagline || "";
    document.getElementById("modalDescription").textContent = show.description || "";
    document.getElementById("modalMatch").textContent = `${show.match_score}% Match`;
    document.getElementById("modalYear").textContent = show.release_year;
    document.getElementById("modalMaturity").textContent = show.maturity_rating;
    document.getElementById("modalSeasons").textContent = `${show.seasons} Season${show.seasons > 1 ? "s" : ""}`;
    document.getElementById("modalGenre").textContent = show.genre;
    document.getElementById("modalCast").textContent = (show.cast && show.cast.length) ? show.cast.join(", ") : "Not listed";
    document.getElementById("modalCreator").textContent = show.creator || "Not listed";

    const watchBtn = document.getElementById("modalWatchBtn");
    watchBtn.href = show.netflix_url || "#";

    const listBtn = document.getElementById("modalListBtn");
    listBtn.dataset.id = show.id;

    refreshListButtons();

    const modalEl = document.getElementById("showDetailModal");
    const modal = bootstrap.Modal.getOrCreateInstance(modalEl);
    modal.show();
}

function attachCardHandlers() {
    document.querySelectorAll(".play-btn, .info-btn").forEach((btn) => {
        btn.addEventListener("click", (e) => {
            e.preventDefault();
            openShowModal(btn.dataset.id);
        });
    });

    document.querySelectorAll(".list-btn").forEach((btn) => {
        btn.addEventListener("click", (e) => {
            e.preventDefault();
            e.stopPropagation();
            toggleMyList(btn.dataset.id);
            if (document.getElementById("myListGrid")) {
                renderMyListPage();
            }
        });
    });

    document.querySelectorAll(".show-card").forEach((card) => {
        card.addEventListener("click", () => openShowModal(card.dataset.id));
    });
}

/* ---------- Toasts ---------- */

function showToast(message, variant) {
    const container = document.getElementById("toastContainer");
    if (!container) return;
    const toastEl = document.createElement("div");
    toastEl.className = `toast align-items-center text-bg-${variant || "success"} border-0`;
    toastEl.setAttribute("role", "alert");
    toastEl.innerHTML = `
        <div class="d-flex">
            <div class="toast-body"><i class="fas fa-circle-check me-2"></i>${message}</div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
        </div>`;
    container.appendChild(toastEl);
    const toast = new bootstrap.Toast(toastEl, { delay: 2500 });
    toast.show();
    toastEl.addEventListener("hidden.bs.toast", () => toastEl.remove());
}

/* ---------- Search & genre filtering (home page) ---------- */

function applySearchFilter(query) {
    query = (query || "").trim().toLowerCase();
    const cards = document.querySelectorAll(".show-card");
    let anyVisible = false;

    if (!query) {
        cards.forEach((c) => (c.style.display = ""));
        document.querySelectorAll(".show-row-section").forEach((r) => (r.style.display = ""));
        document.getElementById("noResults") && document.getElementById("noResults").classList.add("d-none");
        return;
    }

    document.querySelectorAll(".show-row-section").forEach((row) => {
        let rowHasMatch = false;
        row.querySelectorAll(".show-card").forEach((card) => {
            const match = card.dataset.title.includes(query) || card.dataset.genre.toLowerCase().includes(query);
            card.style.display = match ? "" : "none";
            if (match) {
                rowHasMatch = true;
                anyVisible = true;
            }
        });
        row.style.display = rowHasMatch ? "" : "none";
    });

    const noResults = document.getElementById("noResults");
    if (noResults) noResults.classList.toggle("d-none", anyVisible);
}

function initSearch() {
    const input = document.getElementById("globalSearchInput");
    if (!input) return;

    const form = input.closest("form");
    const onHomePage = !!document.getElementById("rowsWrapper");

    if (onHomePage) {
        form.addEventListener("submit", (e) => e.preventDefault());
        input.addEventListener("input", () => applySearchFilter(input.value));

        const params = new URLSearchParams(window.location.search);
        const q = params.get("q");
        if (q) {
            input.value = q;
            applySearchFilter(q);
        }
    }
}

function initGenreChips() {
    const chips = document.querySelectorAll(".genre-chip");
    chips.forEach((chip) => {
        chip.addEventListener("click", (e) => {
            chips.forEach((c) => c.classList.remove("active"));
            chip.classList.add("active");
            if (chip.dataset.genre === "all") {
                e.preventDefault();
                const input = document.getElementById("globalSearchInput");
                if (input) {
                    input.value = "";
                    applySearchFilter("");
                }
            }
        });
    });
}

/* ---------- Hero rotation ---------- */

function initHeroRotation() {
    const hero = document.getElementById("heroSection");
    if (!hero) return;
    const slides = hero.querySelectorAll(".hero-slide");
    const dots = hero.querySelectorAll(".hero-dot");
    if (slides.length < 2) return;

    let current = 0;
    function goTo(index) {
        slides[current].classList.remove("active");
        dots[current] && dots[current].classList.remove("active");
        current = index % slides.length;
        slides[current].classList.add("active");
        dots[current] && dots[current].classList.add("active");
    }

    dots.forEach((dot) => {
        dot.addEventListener("click", () => goTo(Number(dot.dataset.index)));
    });

    setInterval(() => goTo(current + 1), 7000);
}

/* ---------- Navbar scroll state ---------- */

function initNavbarScroll() {
    const navbar = document.getElementById("mainNavbar");
    if (!navbar) return;
    function update() {
        navbar.classList.toggle("scrolled", window.scrollY > 40);
    }
    window.addEventListener("scroll", update, { passive: true });
    update();
}

/* ---------- Row horizontal scroll arrows ---------- */

function initRowArrows() {
    document.querySelectorAll(".row-scroll-wrapper").forEach((wrapper) => {
        const scrollEl = wrapper.querySelector(".row-scroll");
        const left = wrapper.querySelector(".row-arrow-left");
        const right = wrapper.querySelector(".row-arrow-right");
        if (!scrollEl) return;
        const amount = () => scrollEl.clientWidth * 0.8;
        left && left.addEventListener("click", () => scrollEl.scrollBy({ left: -amount(), behavior: "smooth" }));
        right && right.addEventListener("click", () => scrollEl.scrollBy({ left: amount(), behavior: "smooth" }));
    });
}

/* ---------- Back to top ---------- */

function initBackToTop() {
    const btn = document.getElementById("backToTop");
    if (!btn) return;
    window.addEventListener(
        "scroll",
        () => btn.classList.toggle("visible", window.scrollY > 500),
        { passive: true }
    );
    btn.addEventListener("click", () => window.scrollTo({ top: 0, behavior: "smooth" }));
}

/* ---------- Scroll reveal ---------- */

function initScrollReveal() {
    const targets = document.querySelectorAll(".reveal");
    if (!("IntersectionObserver" in window)) {
        targets.forEach((t) => t.classList.add("in-view"));
        return;
    }
    const observer = new IntersectionObserver(
        (entries) => {
            entries.forEach((entry) => {
                if (entry.isIntersecting) {
                    entry.target.classList.add("in-view");
                    observer.unobserve(entry.target);
                }
            });
        },
        { threshold: 0.1 }
    );
    targets.forEach((t) => observer.observe(t));
}

/* ---------- Init ---------- */

document.addEventListener("DOMContentLoaded", () => {
    attachCardHandlers();
    refreshListButtons();
    initSearch();
    initGenreChips();
    initHeroRotation();
    initNavbarScroll();
    initRowArrows();
    initBackToTop();
    initScrollReveal();

    const modalListBtn = document.getElementById("modalListBtn");
    if (modalListBtn) {
        modalListBtn.addEventListener("click", () => {
            toggleMyList(modalListBtn.dataset.id);
            if (document.getElementById("myListGrid")) {
                renderMyListPage();
            }
        });
    }
});
