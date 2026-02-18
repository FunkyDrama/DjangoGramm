import './styles.css';
import logoUrl from './logo.svg';

const FETCH_CONFIG = {
    headers: { "X-Requested-With": "XMLHttpRequest" },
    credentials: "same-origin"
};

const CSS_CLASSES = {
    follow: {
        active: ["bg-red-500", "hover:bg-red-600"],
        inactive: ["bg-[#0095f6]", "hover:bg-blue-600"]
    }
};

const favicon = document.createElement("link");
favicon.rel = "icon";
favicon.type = "image/svg+xml";
favicon.href = logoUrl;
document.head.appendChild(favicon);

function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(";").shift();
}

function createAuthHeaders() {
    return { ...FETCH_CONFIG.headers, "X-CSRFToken": getCookie("csrftoken") };
}

async function fetchWithAuth(url, options = {}) {
    try {
        const response = await fetch(url, {
            ...FETCH_CONFIG,
            ...options,
            headers: { ...createAuthHeaders(), ...(options.headers || {}) }
        });
        if (!response.ok) throw new Error("Network error");
        return response;
    } catch (error) {
        console.error(`Fetch error: ${error.message}`);
        throw error;
    }
}


function handleReactions() {
    document.body.addEventListener("click", async (e) => {
        const btn = e.target.closest("button[name='reaction']");
        if (!btn) return;

        const form = btn.closest("form");
        if (!form) return;

        e.preventDefault();
        const formData = new FormData(form);
        formData.set(btn.name, btn.value);

        try {
            const response = await fetchWithAuth(form.action, { method: "POST", body: formData });
            const data = await response.json();
            updateReactionCounts(form, data);
        } catch (err) {
            console.error("Reaction error:", err);
        }
    });
}

function updateReactionCounts(form, data) {
    const likeSpan = form.querySelector(".like-count");
    const dislikeSpan = form.querySelector(".dislike-count");
    if (likeSpan) likeSpan.textContent = data.likes;
    if (dislikeSpan) dislikeSpan.textContent = data.dislikes;
}

function handleFollowing() {
    const followBtn = document.getElementById("follow-btn");
    if (!followBtn) return;

    followBtn.addEventListener("click", async (e) => {
        e.preventDefault();
        const isFollowing = followBtn.dataset.following === "true";
        const actionUrl = isFollowing ? followBtn.dataset.unfollowUrl : followBtn.dataset.followUrl;

        try {
            const response = await fetchWithAuth(actionUrl, { method: "POST" });
            const data = await response.json();
            updateFollowButton(followBtn, data.is_following);
        } catch (err) {
            console.error("Follow/unfollow error:", err);
        }
    });
}

function updateFollowButton(btn, isFollowing) {
    btn.textContent = isFollowing ? "Unfollow" : "Follow";
    btn.dataset.following = isFollowing.toString();
    const [removeClasses, addClasses] = isFollowing
        ? [CSS_CLASSES.follow.inactive, CSS_CLASSES.follow.active]
        : [CSS_CLASSES.follow.active, CSS_CLASSES.follow.inactive];
    btn.classList.remove(...removeClasses);
    btn.classList.add(...addClasses);
}

function initCarousels(root = document) {
    root.querySelectorAll(".post-carousel:not([data-carousel-init])").forEach(setupCarousel);
}

function setupCarousel(el) {
    el.dataset.carouselInit = "1";

    const track = el.querySelector(".carousel-track");
    const slides = el.querySelectorAll(".carousel-slide");
    const count = slides.length;

    if (count <= 1) return; // nothing to slide

    const dotsContainer = el.querySelector(".carousel-dots");
    const dots = dotsContainer ? dotsContainer.querySelectorAll(".carousel-dot") : [];
    const counter = el.querySelector(".carousel-counter");
    const prevBtn = el.querySelector(".carousel-prev");
    const nextBtn = el.querySelector(".carousel-next");

    let current = 0;
    let startX = 0;
    let startY = 0;
    let dragging = false;
    let dragDelta = 0;

    function goTo(index) {
        current = Math.max(0, Math.min(index, count - 1));
        track.style.transform = `translateX(-${current * 100}%)`;

        dots.forEach((d, i) => {
            d.classList.toggle("active", i === current);
        });

        if (counter) counter.textContent = `${current + 1} / ${count}`;

        if (prevBtn) prevBtn.classList.toggle("is-hidden", current === 0);
        if (nextBtn) nextBtn.classList.toggle("is-hidden", current === count - 1);
    }

    if (prevBtn) prevBtn.addEventListener("click", () => goTo(current - 1));
    if (nextBtn) nextBtn.addEventListener("click", () => goTo(current + 1));

    el.addEventListener("touchstart", (e) => {
        startX = e.touches[0].clientX;
        startY = e.touches[0].clientY;
        dragging = true;
        dragDelta = 0;
        track.style.transition = "none";
    }, { passive: true });

    el.addEventListener("touchmove", (e) => {
        if (!dragging) return;
        const dx = e.touches[0].clientX - startX;
        const dy = e.touches[0].clientY - startY;

        if (!dragDelta && Math.abs(dy) > Math.abs(dx)) {
            dragging = false;
            restoreTransition();
            return;
        }
        dragDelta = dx;
        const offset = -(current * 100) + (dx / el.offsetWidth) * 100;
        track.style.transform = `translateX(${offset}%)`;
    }, { passive: true });

    el.addEventListener("touchend", () => {
        if (!dragging) return;
        restoreTransition();
        if (dragDelta < -50) goTo(current + 1);
        else if (dragDelta > 50) goTo(current - 1);
        else goTo(current); // snap back
        dragging = false;
    }, { passive: true });

    function restoreTransition() {
        track.style.transition = "transform 0.35s cubic-bezier(0.25,0.46,0.45,0.94)";
    }

    let mouseStartX = 0;
    let mouseDragging = false;

    el.addEventListener("mousedown", (e) => {
        mouseStartX = e.clientX;
        mouseDragging = true;
        track.style.transition = "none";
        e.preventDefault();
    });

    window.addEventListener("mousemove", (e) => {
        if (!mouseDragging) return;
        const dx = e.clientX - mouseStartX;
        const offset = -(current * 100) + (dx / el.offsetWidth) * 100;
        track.style.transform = `translateX(${offset}%)`;
    });

    window.addEventListener("mouseup", (e) => {
        if (!mouseDragging) return;
        mouseDragging = false;
        restoreTransition();
        const dx = e.clientX - mouseStartX;
        if (dx < -50) goTo(current + 1);
        else if (dx > 50) goTo(current - 1);
        else goTo(current);
    });

    el.setAttribute("tabindex", "0");
    el.addEventListener("keydown", (e) => {
        if (e.key === "ArrowLeft") goTo(current - 1);
        if (e.key === "ArrowRight") goTo(current + 1);
    });

    goTo(0);
}


function setupInfiniteScroll() {
    const sentinel = document.getElementById("scroll-sentinel");
    if (!sentinel) return;

    const state = {
        currentPage: parseInt(sentinel.dataset.currentPage || sentinel.dataset.currentpage || "1", 10),
        totalPages: parseInt(sentinel.dataset.totalPages || sentinel.dataset.totalpages || "1", 10),
        loading: false
    };

    const observer = new IntersectionObserver(
        entries => {
            if (entries[0].isIntersecting) loadMorePosts(state, sentinel, observer);
        },
        { rootMargin: "300px" }
    );

    observer.observe(sentinel);
}

async function loadMorePosts(state, sentinel, observer) {
    if (state.loading || state.currentPage >= state.totalPages) return;

    state.loading = true;
    try {
        const nextPage = state.currentPage + 1;
        const url = new URL(window.location.href);
        url.searchParams.set("page", nextPage);

        const response = await fetch(url.toString(), { headers: FETCH_CONFIG.headers });
        const html = await response.text();

        appendNewPosts(html);
        state.currentPage = nextPage;

        if (state.currentPage >= state.totalPages) observer.unobserve(sentinel);
    } catch (err) {
        console.error("Load more error:", err);
    } finally {
        state.loading = false;
    }
}

function appendNewPosts(html) {
    const parser = new DOMParser();
    const doc = parser.parseFromString(html, "text/html");
    const newPosts = doc.querySelectorAll("#posts-container > .post-card");
    const container = document.getElementById("posts-container");
    newPosts.forEach(post => {
        container.appendChild(post);
    });
    initCarousels(container);
}


function highlightActiveNav() {
    const path = window.location.pathname;
    document.querySelectorAll(".nav-icon-link").forEach(link => {
        const href = link.getAttribute("href");
        if (href && path === href) {
            link.classList.add("active");
            const svg = link.querySelector("svg");
            if (svg) svg.style.strokeWidth = "2.5";
        }
    });
}

document.addEventListener("DOMContentLoaded", () => {
    handleReactions();
    handleFollowing();
    setupInfiniteScroll();
    initCarousels();
    highlightActiveNav();
});
