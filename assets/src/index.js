import './styles.css';
import logoUrl from './logo.svg';

const FETCH_CONFIG = {
    headers: {
        "X-Requested-With": "XMLHttpRequest"
    },
    credentials: "same-origin"
};

const CSS_CLASSES = {
    follow: {
        active: ["bg-red-500", "hover:bg-red-600"],
        inactive: ["bg-blue-500", "hover:bg-blue-600"]
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
    return {
        ...FETCH_CONFIG.headers,
        "X-CSRFToken": getCookie("csrftoken")
    };
}

async function fetchWithAuth(url, options = {}) {
    try {
        const response = await fetch(url, {
            ...FETCH_CONFIG,
            ...options,
            headers: {
                ...createAuthHeaders(),
                ...(options.headers || {})
            }
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
            const response = await fetchWithAuth(form.action, {
                method: "POST",
                body: formData
            });
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
            const response = await fetchWithAuth(actionUrl, {method: "POST"});
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
        {rootMargin: "200px"}
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

        const response = await fetch(url.toString(), {headers: FETCH_CONFIG.headers});
        const html = await response.text();

        appendNewPosts(html);
        state.currentPage = nextPage;

        if (state.currentPage >= state.totalPages) {
            observer.unobserve(sentinel);
        }
    } catch (err) {
        console.error("Load more error:", err);
    } finally {
        state.loading = false;
    }
}

function appendNewPosts(html) {
    const parser = new DOMParser();
    const doc = parser.parseFromString(html, "text/html");
    const newPosts = doc.querySelectorAll("#posts-container > .shadow");
    const container = document.getElementById("posts-container");
    newPosts.forEach(post => container.appendChild(post));
}

document.addEventListener("DOMContentLoaded", () => {
    handleReactions();
    handleFollowing();
    setupInfiniteScroll();
});