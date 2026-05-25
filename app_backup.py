import html
import os
import re
import smtplib
import ssl
from email.message import EmailMessage

import requests
import streamlit as st

from movieflix_database import (
    authenticate_user,
    create_reset_code,
    create_user,
    get_user_by_email,
    init_db,
    reset_password,
)

# =============================
# CONFIG
# =============================
API_BASE = "https://movie-rec-466x.onrender.com"
# Local testing:
# API_BASE = "http://127.0.0.1:8000"

TMDB_IMG = "https://image.tmdb.org/t/p/w500"

st.set_page_config(
    page_title="MovieFlix",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# =============================
# CSS
# =============================
st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');

* {
    font-family: 'Inter', sans-serif;
}

:root {
    --red: #D4A017;
    --dark-red: #9C6B00;
    --black: #050505;
    --muted: #bdbdbd;
}

/* =============================
   MAIN BACKGROUND
============================= */
.stApp {
    background:
        radial-gradient(circle at 5% 0%, rgba(212, 160, 23, 0.28), transparent 28%),
        radial-gradient(circle at 95% 5%, rgba(156, 107, 0, 0.22), transparent 30%),
        linear-gradient(180deg, #050505 0%, #090909 45%, #000000 100%);
    color: white;
}

.block-container {
    max-width: 1540px;
    padding-top: 1.2rem;
    padding-bottom: 4rem;
}

header[data-testid="stHeader"] {
    background: transparent;
}

[data-testid="stToolbar"],
[data-testid="stDecoration"],
#MainMenu,
footer {
    display: none !important;
}

/* Remove sidebar completely */
section[data-testid="stSidebar"],
[data-testid="collapsedControl"] {
    display: none !important;
}

/* =============================
   HEADER
============================= */
.header-box {
    width: 100%;
    min-height: 82px;
    padding: 16px 26px;
    border-radius: 26px;
    background: #050505;
    border: 1px solid rgba(255,255,255,0.09);
    box-shadow: 0 24px 75px rgba(0,0,0,0.55);
    margin-bottom: 26px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 28px;
}

.brand {
    display: flex;
    align-items: center;
    gap: 14px;
    flex-shrink: 0;
}

.brand-icon {
    width: 50px;
    height: 50px;
    border-radius: 15px;
    background: linear-gradient(145deg, var(--red), var(--dark-red));
    display: grid;
    place-items: center;
    font-weight: 900;
    font-size: 1.25rem;
    box-shadow: 0 14px 38px rgba(212,160,23,0.36);
}

.brand-text {
    font-size: 1.65rem;
    font-weight: 900;
    letter-spacing: -0.07em;
    color: #ffffff;
}

.brand-text span {
    color: var(--red);
}

.nav-menu {
    display: flex;
    align-items: center;
    justify-content: flex-end;
    gap: 26px;
    flex-wrap: wrap;
}

.nav-link {
    color: #d7d7d7 !important;
    text-decoration: none !important;
    font-size: 0.98rem;
    font-weight: 850;
    transition: color 0.2s ease, transform 0.2s ease;
    background: transparent !important;
    border: none !important;
    padding: 0 !important;
}

.nav-link:hover {
    color: #ffffff !important;
    background: transparent !important;
    transform: translateY(-1px);
}

.nav-link.active {
    color: var(--red) !important;
}

/* =============================
   HERO
============================= */
.hero {
    min-height: 390px;
    border-radius: 38px;
    padding: 52px;
    position: relative;
    overflow: hidden;
    background:
        linear-gradient(90deg, rgba(0,0,0,0.97) 0%, rgba(0,0,0,0.78) 43%, rgba(0,0,0,0.28) 100%),
        radial-gradient(circle at 82% 38%, rgba(212,160,23,0.48), transparent 36%),
        linear-gradient(135deg, #161616, #050505);
    border: 1px solid rgba(255,255,255,0.09);
    box-shadow: 0 38px 110px rgba(0,0,0,0.62);
    margin-bottom: 36px;
    animation: fadeUp 0.75s ease both;
}

.hero-badge {
    display: inline-flex;
    align-items: center;
    padding: 9px 15px;
    border-radius: 999px;
    background: rgba(212,160,23,0.15);
    border: 1px solid rgba(212,160,23,0.45);
    font-weight: 900;
    font-size: 0.9rem;
    margin-bottom: 22px;
}

.hero-title {
    max-width: 820px;
    font-size: clamp(3rem, 6vw, 6.1rem);
    line-height: 0.94;
    letter-spacing: -0.09em;
    font-weight: 900;
    margin-bottom: 22px;
}

.hero-title span {
    display: block;
    color: var(--red);
    text-shadow: 0 18px 55px rgba(212,160,23,0.34);
}

.hero-text {
    max-width: 700px;
    color: #dedede;
    font-size: 1.08rem;
    line-height: 1.8;
    font-weight: 650;
}

/* =============================
   SEARCH
============================= */
.search-wrap {
    margin-bottom: 18px;
}

.search-title {
    font-size: 1.95rem;
    font-weight: 900;
    letter-spacing: -0.06em;
    margin-bottom: 8px;
    color: #ffffff;
}

.search-subtitle {
    color: #c8c8c8;
    font-size: 1.02rem;
    font-weight: 650;
    margin-bottom: 18px;
}

.stTextInput label {
    display: none !important;
}

.stTextInput {
    margin-bottom: 34px !important;
}

.stTextInput > div {
    margin-top: 0 !important;
}

.stTextInput div[data-baseweb="base-input"] {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
}

.stTextInput div[data-baseweb="input"] {
    background:
        linear-gradient(135deg, rgba(255,255,255,0.12), rgba(255,255,255,0.065)) !important;
    border: 1px solid rgba(255,255,255,0.22) !important;
    border-radius: 22px !important;
    min-height: 72px !important;
    height: 72px !important;
    padding-left: 24px !important;
    padding-right: 24px !important;
    box-shadow:
        inset 0 0 0 1px rgba(255,255,255,0.025),
        0 22px 60px rgba(0,0,0,0.36) !important;
    transition: all 0.25s ease !important;
}

.stTextInput div[data-baseweb="input"]:focus-within {
    border-color: rgba(212,160,23,0.96) !important;
    box-shadow:
        0 0 0 5px rgba(212,160,23,0.18),
        0 28px 75px rgba(0,0,0,0.45) !important;
}

.stTextInput input {
    height: 72px !important;
    min-height: 72px !important;
    background: transparent !important;
    border: none !important;
    color: #ffffff !important;
    padding: 0 !important;
    font-size: 1.12rem !important;
    font-weight: 850 !important;
    line-height: 72px !important;
    box-shadow: none !important;
}

.stTextInput input::placeholder {
    color: #eeeeee !important;
    opacity: 0.85 !important;
    font-weight: 750 !important;
}

/* =============================
   SELECTBOX
============================= */
.stSelectbox label {
    color: #ffffff !important;
    font-weight: 850 !important;
}

.stSelectbox div[data-baseweb="select"] > div {
    background: rgba(0,0,0,0.70) !important;
    border: 1px solid rgba(255,255,255,0.16) !important;
    border-radius: 18px !important;
    min-height: 55px !important;
}

/* =============================
   SECTIONS
============================= */
.section-head {
    margin: 36px 0 20px 0;
}

.section-title {
    display: flex;
    align-items: center;
    gap: 12px;
    font-size: 2rem;
    font-weight: 900;
    letter-spacing: -0.06em;
}

.section-title::before {
    content: "";
    width: 6px;
    height: 35px;
    border-radius: 999px;
    background: var(--red);
    box-shadow: 0 0 25px rgba(212,160,23,0.70);
}

.section-subtitle {
    color: #b5b5b5;
    font-size: 1rem;
    margin-top: 8px;
    font-weight: 650;
}

/* =============================
   MOVIE GRID
============================= */
.movie-grid {
    display: grid;
    gap: 22px;
    align-items: start;
    margin-top: 16px;
}

.movie-card {
    position: relative;
    display: block;
    width: 100%;
    height: clamp(255px, 22vw, 330px);
    border-radius: 22px;
    overflow: hidden;
    background: #121212;
    border: 1px solid rgba(255,255,255,0.08);
    box-shadow: 0 20px 55px rgba(0,0,0,0.46);
    text-decoration: none !important;
    color: white !important;
    transition: transform 0.28s ease, box-shadow 0.28s ease, border-color 0.28s ease;
}

.movie-card:hover {
    transform: translateY(-9px) scale(1.035);
    border-color: rgba(212,160,23,0.88);
    box-shadow:
        0 34px 95px rgba(0,0,0,0.74),
        0 0 0 1px rgba(212,160,23,0.22);
    z-index: 20;
}

.movie-poster {
    width: 100%;
    height: 100%;
    object-fit: cover;
    display: block;
    transition: transform 0.38s ease, filter 0.38s ease;
}

.movie-card:hover .movie-poster {
    transform: scale(1.09);
    filter: brightness(0.48);
}

.poster-fallback {
    width: 100%;
    height: 100%;
    display: grid;
    place-items: center;
    background:
        radial-gradient(circle, rgba(212,160,23,0.25), transparent 42%),
        linear-gradient(145deg, #191919, #050505);
    font-size: 3rem;
}

.movie-overlay {
    position: absolute;
    inset: 0;
    padding: 16px;
    display: flex;
    flex-direction: column;
    justify-content: flex-end;
    background:
        linear-gradient(180deg, rgba(0,0,0,0.03) 0%, rgba(0,0,0,0.38) 45%, rgba(0,0,0,0.97) 100%);
    opacity: 0;
    transition: opacity 0.28s ease;
}

.movie-card:hover .movie-overlay {
    opacity: 1;
}

.movie-name {
    font-size: 1rem;
    line-height: 1.23rem;
    font-weight: 900;
    letter-spacing: -0.03em;
    margin-bottom: 8px;
}

.movie-info {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 8px;
    color: #d8d8d8;
    font-size: 0.78rem;
    font-weight: 850;
}

.movie-chip {
    padding: 6px 9px;
    border-radius: 999px;
    background: var(--red);
    color: #fff;
    font-size: 0.7rem;
    font-weight: 900;
}

/* =============================
   DETAIL PAGE
============================= */
.detail-hero {
    min-height: 545px;
    border-radius: 38px;
    overflow: hidden;
    position: relative;
    border: 1px solid rgba(212,160,23,0.34);
    box-shadow: 0 38px 120px rgba(0,0,0,0.72);
    background-size: cover;
    background-position: center;
    margin-top: 10px;
    animation: fadeUp 0.75s ease both;
}

.detail-inner {
    min-height: 545px;
    padding: 44px;
    display: grid;
    grid-template-columns: 245px minmax(0, 1fr);
    gap: 34px;
    align-items: end;
    background:
        linear-gradient(90deg, rgba(0,0,0,0.97) 0%, rgba(0,0,0,0.86) 48%, rgba(0,0,0,0.36) 100%),
        linear-gradient(0deg, rgba(0,0,0,0.94) 0%, transparent 56%);
}

.detail-poster {
    width: 100%;
    border-radius: 24px;
    box-shadow: 0 30px 82px rgba(0,0,0,0.72);
    border: 1px solid rgba(255,255,255,0.15);
}

.detail-fallback {
    height: 360px;
    border-radius: 24px;
    display: grid;
    place-items: center;
    background: #151515;
    font-size: 4rem;
    border: 1px solid rgba(255,255,255,0.12);
}

.detail-kicker {
    color: var(--red);
    font-weight: 900;
    text-transform: uppercase;
    letter-spacing: 0.14em;
    font-size: 0.82rem;
    margin-bottom: 10px;
}

.detail-title {
    font-size: clamp(2.5rem, 5vw, 5.2rem);
    font-weight: 900;
    line-height: 0.96;
    letter-spacing: -0.08em;
    margin-bottom: 18px;
}

.detail-pills {
    display: flex;
    flex-wrap: wrap;
    gap: 9px;
    margin-bottom: 22px;
}

.detail-pill {
    padding: 8px 12px;
    border-radius: 999px;
    background: rgba(255,255,255,0.12);
    border: 1px solid rgba(255,255,255,0.12);
    color: #eee;
    font-size: 0.86rem;
    font-weight: 850;
}

.detail-overview {
    max-width: 860px;
    color: #e0e0e0;
    font-size: 1.02rem;
    line-height: 1.85;
    font-weight: 650;
}

.simple-page {
    padding: 38px;
    border-radius: 32px;
    background: rgba(255,255,255,0.055);
    border: 1px solid rgba(255,255,255,0.10);
    box-shadow: 0 30px 85px rgba(0,0,0,0.45);
}

.simple-page h1 {
    font-size: 3rem;
    letter-spacing: -0.07em;
    margin-bottom: 12px;
}

.simple-page p {
    color: #d0d0d0;
    line-height: 1.8;
    font-size: 1.05rem;
}



/* =============================
   AUTHENTICATION PAGES
============================= */
.auth-shell {
    min-height: calc(100vh - 70px);
    display: grid;
    grid-template-columns: minmax(0, 1fr) 460px;
    gap: 34px;
    align-items: center;
    padding: 26px 0 44px 0;
}

.auth-intro {
    min-height: 620px;
    border-radius: 40px;
    padding: 54px;
    display: flex;
    flex-direction: column;
    justify-content: flex-end;
    background:
        linear-gradient(135deg, rgba(0,0,0,0.97), rgba(0,0,0,0.74)),
        radial-gradient(circle at 80% 25%, rgba(212,160,23,0.52), transparent 36%),
        linear-gradient(135deg, #1c1c1c, #050505);
    border: 1px solid rgba(255,255,255,0.10);
    box-shadow: 0 38px 120px rgba(0,0,0,0.68);
    overflow: hidden;
    position: relative;
}

.auth-intro::before {
    content: "";
    position: absolute;
    inset: 0;
    background:
        linear-gradient(90deg, transparent 0 49%, rgba(255,255,255,0.035) 50%, transparent 51% 100%),
        linear-gradient(0deg, transparent 0 49%, rgba(255,255,255,0.035) 50%, transparent 51% 100%);
    background-size: 64px 64px;
    opacity: 0.18;
}

.auth-intro > * {
    position: relative;
    z-index: 1;
}

.auth-eyebrow {
    display: inline-flex;
    width: fit-content;
    padding: 9px 15px;
    border-radius: 999px;
    background: rgba(212,160,23,0.15);
    border: 1px solid rgba(212,160,23,0.45);
    font-size: 0.84rem;
    font-weight: 900;
    margin-bottom: 18px;
}

.auth-big-title {
    max-width: 760px;
    font-size: clamp(3rem, 6vw, 6rem);
    line-height: 0.94;
    letter-spacing: -0.09em;
    font-weight: 900;
    margin-bottom: 20px;
}

.auth-big-title span {
    color: var(--red);
    display: block;
}

.auth-copy {
    max-width: 650px;
    color: #d8d8d8;
    font-size: 1.05rem;
    line-height: 1.75;
    font-weight: 650;
}

.auth-card {
    border-radius: 34px;
    padding: 30px;
    background: rgba(10,10,10,0.94);
    border: 1px solid rgba(255,255,255,0.12);
    box-shadow: 0 34px 100px rgba(0,0,0,0.62);
}

.auth-title {
    font-size: 2.15rem;
    font-weight: 900;
    letter-spacing: -0.07em;
    margin-bottom: 8px;
}

.auth-subtitle {
    color: #bfbfbf;
    line-height: 1.6;
    font-weight: 650;
    margin-bottom: 22px;
}

.auth-switch {
    color: #d9d9d9;
    font-weight: 750;
    text-align: center;
    margin-top: 18px;
}

.auth-switch a {
    color: var(--red) !important;
    text-decoration: none !important;
    font-weight: 950;
}

.auth-note {
    padding: 13px 15px;
    border-radius: 18px;
    border: 1px solid rgba(212,160,23,0.30);
    background: rgba(212,160,23,0.09);
    color: #f1f1f1;
    line-height: 1.55;
    font-weight: 650;
    margin-top: 14px;
}

.nav-user {
    color: #ffffff !important;
}

.stButton > button,
.stFormSubmitButton > button {
    width: 100% !important;
    min-height: 54px !important;
    border-radius: 17px !important;
    border: 0 !important;
    background: linear-gradient(135deg, var(--red), var(--dark-red)) !important;
    color: #ffffff !important;
    font-weight: 950 !important;
    box-shadow: 0 20px 45px rgba(212,160,23,0.22) !important;
    transition: transform 0.2s ease, box-shadow 0.2s ease !important;
}

.stButton > button:hover,
.stFormSubmitButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 28px 60px rgba(212,160,23,0.28) !important;
}

.auth-card .stTextInput {
    margin-bottom: 14px !important;
}

.auth-card .stTextInput div[data-baseweb="input"] {
    min-height: 58px !important;
    height: 58px !important;
    border-radius: 17px !important;
    background: rgba(255,255,255,0.07) !important;
}

.auth-card .stTextInput input {
    min-height: 58px !important;
    height: 58px !important;
    line-height: 58px !important;
    font-size: 1rem !important;
}

@media screen and (max-width: 1050px) {
    .auth-shell {
        grid-template-columns: 1fr;
    }

    .auth-intro {
        min-height: 420px;
    }
}

/* =============================
   ANIMATION + RESPONSIVE
============================= */
@keyframes fadeUp {
    from {
        opacity: 0;
        transform: translateY(24px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

@media screen and (max-width: 1000px) {
    .header-box {
        align-items: flex-start;
        flex-direction: column;
    }

    .nav-menu {
        justify-content: flex-start;
        gap: 16px;
    }

    .detail-inner {
        grid-template-columns: 1fr;
        padding: 30px;
    }

    .detail-poster {
        max-width: 230px;
    }
}

@media screen and (max-width: 700px) {
    .movie-grid {
        grid-template-columns: repeat(2, minmax(0, 1fr)) !important;
    }

    .hero {
        padding: 32px;
    }

    .hero-title {
        font-size: 3rem;
    }

    .detail-title {
        font-size: 2.7rem;
    }
}
</style>
""",
    unsafe_allow_html=True,
)

# =============================
# DATABASE + SESSION STATE
# =============================
init_db()

VALID_CATEGORIES = ["trending", "popular", "top_rated", "now_playing", "upcoming"]
AUTH_VIEWS = ["login", "signup", "forgot", "reset"]

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if "user" not in st.session_state:
    st.session_state.user = None

if "auth_view" not in st.session_state:
    st.session_state.auth_view = "login"

if "view" not in st.session_state:
    st.session_state.view = "home"

if "home_category" not in st.session_state:
    st.session_state.home_category = "trending"

if "selected_tmdb_id" not in st.session_state:
    st.session_state.selected_tmdb_id = None

qp_auth = st.query_params.get("auth")
qp_view = st.query_params.get("view")
qp_id = st.query_params.get("id")
qp_cat = st.query_params.get("cat")

if qp_auth == "logout":
    st.session_state.authenticated = False
    st.session_state.user = None
    st.session_state.auth_view = "login"
    st.session_state.view = "home"
    st.session_state.selected_tmdb_id = None
    try:
        st.query_params.clear()
    except Exception:
        pass

elif qp_auth in AUTH_VIEWS:
    st.session_state.auth_view = qp_auth

if qp_view in ("home", "details", "account", "help"):
    st.session_state.view = qp_view

if qp_cat in VALID_CATEGORIES:
    st.session_state.home_category = qp_cat
    st.session_state.view = "home"
    st.session_state.selected_tmdb_id = None

if qp_id:
    try:
        st.session_state.selected_tmdb_id = int(qp_id)
        st.session_state.view = "details"
    except Exception:
        pass

# =============================
# API
# =============================
@st.cache_data(ttl=45)
def api_get_json(path: str, params: dict | None = None):
    try:
        r = requests.get(f"{API_BASE}{path}", params=params, timeout=25)
        if r.status_code >= 400:
            return None, f"HTTP {r.status_code}: {r.text[:300]}"
        return r.json(), None
    except Exception as e:
        return None, f"Request failed: {e}"


# =============================
# HELPERS
# =============================
def esc(value):
    return html.escape(str(value)) if value is not None else ""


def esc_attr(value):
    return html.escape(str(value), quote=True) if value is not None else ""


def get_year(value):
    return str(value)[:4] if value else ""


def clean_category_name(value):
    return value.replace("_", " ").title()


def card_genre_text(movie):
    if not isinstance(movie, dict):
        return "Movie"

    for key in ["genres_text", "genre", "genre_names"]:
        value = movie.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()

    genres = movie.get("genres")
    names = []

    if isinstance(genres, list):
        for g in genres:
            if isinstance(g, dict) and g.get("name"):
                names.append(g["name"])
            elif isinstance(g, str):
                names.append(g)

    if names:
        return ", ".join(names[:2])

    year = get_year(movie.get("release_date"))
    return year if year else "Movie"


def parse_tmdb_search_to_cards(data, keyword: str, limit: int = 24):
    keyword_l = keyword.strip().lower()
    raw_items = []

    if isinstance(data, dict) and "results" in data:
        for m in data.get("results") or []:
            title = (m.get("title") or "").strip()
            tmdb_id = m.get("id")
            poster_path = m.get("poster_path")

            if not title or not tmdb_id:
                continue

            raw_items.append(
                {
                    "tmdb_id": int(tmdb_id),
                    "title": title,
                    "poster_url": f"{TMDB_IMG}{poster_path}" if poster_path else None,
                    "release_date": m.get("release_date", ""),
                }
            )

    elif isinstance(data, list):
        for m in data:
            tmdb_id = m.get("tmdb_id") or m.get("id")
            title = (m.get("title") or "").strip()

            if not title or not tmdb_id:
                continue

            raw_items.append(
                {
                    "tmdb_id": int(tmdb_id),
                    "title": title,
                    "poster_url": m.get("poster_url"),
                    "release_date": m.get("release_date", ""),
                    "genres": m.get("genres", []),
                }
            )
    else:
        return [], []

    matched = [x for x in raw_items if keyword_l in x["title"].lower()]
    final_list = matched if matched else raw_items

    suggestions = []
    for x in final_list[:10]:
        year = get_year(x.get("release_date"))
        label = f"{x['title']} ({year})" if year else x["title"]
        suggestions.append((label, x["tmdb_id"]))

    return suggestions, final_list[:limit]


def to_cards_from_tfidf_items(tfidf_items):
    cards = []

    for x in tfidf_items or []:
        tmdb = x.get("tmdb") or {}

        if tmdb.get("tmdb_id"):
            cards.append(
                {
                    "tmdb_id": tmdb.get("tmdb_id"),
                    "title": tmdb.get("title") or x.get("title") or "Untitled",
                    "poster_url": tmdb.get("poster_url"),
                    "release_date": tmdb.get("release_date", ""),
                    "genres": tmdb.get("genres", []),
                }
            )

    return cards


def merge_unique_cards(*card_lists):
    seen = set()
    merged = []

    for cards in card_lists:
        for m in cards or []:
            tmdb_id = m.get("tmdb_id") or m.get("id")

            if not tmdb_id or tmdb_id in seen:
                continue

            seen.add(tmdb_id)
            merged.append(m)

    return merged


def nav_active(view=None, cat=None):
    if view == "home" and st.session_state.view == "home" and cat is None:
        return "active"

    if view and st.session_state.view == view and view != "home":
        return "active"

    if cat and st.session_state.view == "home" and st.session_state.home_category == cat:
        return "active"

    return ""



# =============================
# AUTH HELPERS
# =============================
def get_config_value(name: str, default: str = "") -> str:
    """Read SMTP settings from Streamlit secrets first, then environment variables."""
    try:
        value = st.secrets.get(name, None)
        if value is not None:
            return str(value)
    except Exception:
        pass
    return os.getenv(name, default)


def validate_username(username: str) -> str | None:
    username = username.strip()
    if not username:
        return "Username is required."
    if len(username) < 3:
        return "Username must be at least 3 characters long."
    if len(username) > 30:
        return "Username must be 30 characters or less."
    if not re.fullmatch(r"[A-Za-z0-9_]+", username):
        return "Username can only contain letters, numbers, and underscores."
    return None


def validate_email(email: str) -> str | None:
    email = email.strip().lower()
    if not email:
        return "Email address is required."
    if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email):
        return "Please enter a valid email address."
    return None


def validate_password(password: str) -> str | None:
    if not password:
        return "Password is required."
    if len(password) < 8:
        return "Password must be at least 8 characters long."
    if not re.search(r"[A-Za-z]", password) or not re.search(r"\d", password):
        return "Password must contain at least one letter and one number."
    return None


def send_reset_email(to_email: str, code: str) -> tuple[bool, str]:
    """Send reset code using SMTP configured in secrets/environment variables."""
    smtp_host = get_config_value("SMTP_HOST")
    smtp_port = int(get_config_value("SMTP_PORT", "587") or "587")
    smtp_user = get_config_value("SMTP_USER")
    smtp_password = get_config_value("SMTP_PASSWORD")
    smtp_from = get_config_value("SMTP_FROM", smtp_user)
    show_code_for_demo = get_config_value("SHOW_RESET_CODE_FOR_DEMO", "false").lower() == "true"

    if not all([smtp_host, smtp_port, smtp_user, smtp_password, smtp_from]):
        if show_code_for_demo:
            return True, f"SMTP is not configured. Demo reset code: {code}"
        return False, "SMTP email is not configured yet. Add SMTP settings in .streamlit/secrets.toml."

    message = EmailMessage()
    message["Subject"] = "MovieFlix Password Reset Code"
    message["From"] = smtp_from
    message["To"] = to_email
    message.set_content(
        f"""Hello,

Your MovieFlix password reset verification code is: {code}

This code will expire in 10 minutes. If you did not request this reset, please ignore this email.

MovieFlix Security Team
"""
    )

    try:
        context = ssl.create_default_context()
        with smtplib.SMTP(smtp_host, smtp_port, timeout=20) as server:
            server.starttls(context=context)
            server.login(smtp_user, smtp_password)
            server.send_message(message)
        return True, "Verification code sent to your registered email address."
    except Exception as exc:
        if show_code_for_demo:
            return True, f"Email sending failed, but demo reset code is: {code}. Error: {exc}"
        return False, f"Could not send email: {exc}"


def login_user(user: dict):
    st.session_state.authenticated = True
    st.session_state.user = user
    st.session_state.view = "home"
    st.session_state.selected_tmdb_id = None
    try:
        st.query_params.clear()
        st.query_params["view"] = "home"
    except Exception:
        pass


def render_auth_brand():
    st.markdown(
        """
        <div class='header-box'>
            <div class='brand'>
                <div class='brand-icon'>P</div>
                <div class='brand-text'>Pop<span>Corn</span></div>
            </div>
            <div class='nav-menu'>
                <a class='nav-link active' href='?auth=login'>Login</a>
                <a class='nav-link' href='?auth=signup'>Signup</a>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_login_form():
    st.markdown("<div class='auth-title'>Welcome back</div>", unsafe_allow_html=True)
    st.markdown(
        "<div class='auth-subtitle'>Login with your username or email to access your movie recommendations.</div>",
        unsafe_allow_html=True,
    )

    with st.form("login_form", clear_on_submit=False):
        identifier = st.text_input("Username or Email", placeholder="Enter username or email")
        password = st.text_input("Password", placeholder="Enter password", type="password")
        submitted = st.form_submit_button("Login")

    if submitted:
        if not identifier.strip():
            st.error("Username or email is required.")
        elif not password:
            st.error("Password is required.")
        else:
            ok, message, user = authenticate_user(identifier, password)
            if ok and user:
                st.success(message)
                login_user(user)
                st.rerun()
            else:
                st.error(message)

    st.markdown(
        """
        <div class='auth-switch'>
            <a href='?auth=forgot'>Forgot Password?</a><br><br>
            New to MovieFlix? <a href='?auth=signup'>Create an account</a>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_signup_form():
    st.markdown("<div class='auth-title'>Create account</div>", unsafe_allow_html=True)
    st.markdown(
        "<div class='auth-subtitle'>Signup once, then your account data will be saved securely in SQLite.</div>",
        unsafe_allow_html=True,
    )

    with st.form("signup_form", clear_on_submit=False):
        username = st.text_input("Username", placeholder="e.g. moviefan_01")
        email = st.text_input("Email Address", placeholder="you@example.com")
        password = st.text_input("Password", placeholder="Minimum 8 characters", type="password")
        confirm_password = st.text_input("Confirm Password", placeholder="Re-enter password", type="password")
        submitted = st.form_submit_button("Create Account")

    if submitted:
        errors = []
        for validator, value in [
            (validate_username, username),
            (validate_email, email),
            (validate_password, password),
        ]:
            error = validator(value)
            if error:
                errors.append(error)

        if password != confirm_password:
            errors.append("Password and confirm password do not match.")

        if errors:
            for error in errors:
                st.error(error)
        else:
            ok, message = create_user(username, email, password)
            if ok:
                st.success(message)
                st.session_state.auth_view = "login"
                st.info("Now login with your new username/email and password.")
            else:
                st.error(message)

    st.markdown(
        "<div class='auth-switch'>Already have an account? <a href='?auth=login'>Login here</a></div>",
        unsafe_allow_html=True,
    )


def render_forgot_password_form():
    st.markdown("<div class='auth-title'>Forgot password</div>", unsafe_allow_html=True)
    st.markdown(
        "<div class='auth-subtitle'>Enter your registered email. We will send a 6-digit verification code.</div>",
        unsafe_allow_html=True,
    )

    with st.form("forgot_form", clear_on_submit=False):
        email = st.text_input("Registered Email", placeholder="you@example.com")
        submitted = st.form_submit_button("Send Reset Code")

    if submitted:
        email_error = validate_email(email)
        if email_error:
            st.error(email_error)
        elif not get_user_by_email(email):
            st.error("No registered account found with this email address.")
        else:
            ok, message, code = create_reset_code(email)
            if ok and code:
                sent, mail_message = send_reset_email(email.strip().lower(), code)
                if sent:
                    st.success(mail_message)
                    st.session_state.auth_view = "reset"
                    st.markdown(
                        "<div class='auth-note'>Now open the Reset Password page and enter the verification code.</div>",
                        unsafe_allow_html=True,
                    )
                else:
                    st.error(mail_message)
            else:
                st.error(message)

    st.markdown(
        "<div class='auth-switch'><a href='?auth=reset'>I already have a code</a><br><br><a href='?auth=login'>Back to login</a></div>",
        unsafe_allow_html=True,
    )


def render_reset_password_form():
    st.markdown("<div class='auth-title'>Reset password</div>", unsafe_allow_html=True)
    st.markdown(
        "<div class='auth-subtitle'>Enter the code sent to your registered email and choose a new password.</div>",
        unsafe_allow_html=True,
    )

    with st.form("reset_form", clear_on_submit=False):
        email = st.text_input("Registered Email", placeholder="you@example.com")
        code = st.text_input("Verification Code", placeholder="6-digit code", max_chars=6)
        new_password = st.text_input("New Password", placeholder="Minimum 8 characters", type="password")
        confirm_password = st.text_input("Confirm New Password", placeholder="Re-enter new password", type="password")
        submitted = st.form_submit_button("Reset Password")

    if submitted:
        errors = []
        email_error = validate_email(email)
        password_error = validate_password(new_password)
        if email_error:
            errors.append(email_error)
        if not code.strip():
            errors.append("Verification code is required.")
        elif not re.fullmatch(r"\d{6}", code.strip()):
            errors.append("Verification code must be exactly 6 digits.")
        if password_error:
            errors.append(password_error)
        if new_password != confirm_password:
            errors.append("New password and confirm password do not match.")

        if errors:
            for error in errors:
                st.error(error)
        else:
            ok, message = reset_password(email, code, new_password)
            if ok:
                st.success(message)
                st.session_state.auth_view = "login"
            else:
                st.error(message)

    st.markdown(
        "<div class='auth-switch'><a href='?auth=forgot'>Send a new code</a><br><br><a href='?auth=login'>Back to login</a></div>",
        unsafe_allow_html=True,
    )


def render_auth_page():
    render_auth_brand()

    st.markdown(
        """
        <div class='auth-shell'>
            <div class='auth-intro'>
                <div class='auth-eyebrow'>● Secure Movie Recommendation Account</div>
                <div class='auth-big-title'>Your cinema profile.<span>Protected properly.</span></div>
                <div class='auth-copy'>Create an account, login securely, recover forgotten passwords, and access the MovieFlix recommendation system with a clean professional authentication flow.</div>
            </div>
            <div class='auth-card'>
        """,
        unsafe_allow_html=True,
    )

    auth_view = st.session_state.get("auth_view", "login")
    if auth_view == "signup":
        render_signup_form()
    elif auth_view == "forgot":
        render_forgot_password_form()
    elif auth_view == "reset":
        render_reset_password_form()
    else:
        render_login_form()

    st.markdown("</div></div>", unsafe_allow_html=True)


# =============================
# UI COMPONENTS
# =============================
def render_header():
    username = "Guest"
    if st.session_state.get("user"):
        username = esc(st.session_state.user.get("username", "User"))

    header_html = (
        "<div class='header-box'>"
        "<div class='brand'>"
        "<div class='brand-icon'>P</div>"
        "<div class='brand-text'>Pop<span>Corn</span></div>"
        "</div>"
        "<div class='nav-menu'>"
        f"<a class='nav-link {nav_active(view='home')}' href='?view=home'>Home</a>"
        f"<a class='nav-link {nav_active(cat='trending')}' href='?view=home&cat=trending'>Trending</a>"
        f"<a class='nav-link {nav_active(cat='popular')}' href='?view=home&cat=popular'>Popular</a>"
        f"<a class='nav-link {nav_active(cat='top_rated')}' href='?view=home&cat=top_rated'>Top Rated</a>"
        f"<a class='nav-link {nav_active(cat='now_playing')}' href='?view=home&cat=now_playing'>Now Playing</a>"
        f"<a class='nav-link {nav_active(view='account')} nav-user' href='?view=account'>👤 {username}</a>"
        f"<a class='nav-link {nav_active(view='help')}' href='?view=help'>Help</a>"
        "<a class='nav-link' href='?auth=logout'>Logout</a>"
        "</div>"
        "</div>"
    )

    st.markdown(header_html, unsafe_allow_html=True)


def render_hero():
    hero_html = (
        "<div class='hero'>"
        "<div class='hero-badge'>● AI Movie Recommendation System</div>"
        "<div class='hero-title'>Unlimited movies.<span>Smart picks.</span></div>"
        "<div class='hero-text'>Search your favorite title, open cinematic movie details, and discover similar recommendations with a premium Netflix-style interface.</div>"
        "</div>"
    )

    st.markdown(hero_html, unsafe_allow_html=True)


def render_search():
    search_html = (
        "<div class='search-wrap'>"
        "<div class='search-title'>Find your next movie</div>"
        "<div class='search-subtitle'>Search by movie title and choose from smart suggestions.</div>"
        "</div>"
    )

    st.markdown(search_html, unsafe_allow_html=True)

    return st.text_input(
        "Search movie title",
        placeholder="Search Avatar, Batman, Avengers, Interstellar...",
        key="movie_search_input",
    )


def section_title(title, subtitle=""):
    subtitle_html = f"<div class='section-subtitle'>{esc(subtitle)}</div>" if subtitle else ""

    section_html = (
        f"<div class='section-head'>"
        f"<div class='section-title'>{esc(title)}</div>"
        f"{subtitle_html}"
        f"</div>"
    )

    st.markdown(section_html, unsafe_allow_html=True)


def poster_grid(cards, cols=6):
    if not cards:
        st.info("No movies to show.")
        return

    cols = max(4, min(int(cols), 7))

    grid_html = f"<div class='movie-grid' style='grid-template-columns: repeat({cols}, minmax(0, 1fr));'>"
    count = 0

    for movie in cards:
        tmdb_id = movie.get("tmdb_id") or movie.get("id")

        if not tmdb_id:
            continue

        try:
            tmdb_id = int(tmdb_id)
        except Exception:
            continue

        title = movie.get("title") or "Untitled"
        poster = movie.get("poster_url")
        genre_text = card_genre_text(movie)
        href = f"?view=details&id={tmdb_id}"

        if poster:
            poster_html = f"<img class='movie-poster' src='{esc_attr(poster)}' alt='{esc_attr(title)}'>"
        else:
            poster_html = "<div class='poster-fallback'>🎬</div>"

        grid_html += (
            f"<a class='movie-card' href='{href}'>"
            f"{poster_html}"
            f"<div class='movie-overlay'>"
            f"<div class='movie-name'>{esc(title)}</div>"
            f"<div class='movie-info'>"
            f"<span>{esc(genre_text)}</span>"
            f"<span class='movie-chip'>OPEN</span>"
            f"</div>"
            f"</div>"
            f"</a>"
        )

        count += 1

    grid_html += "</div>"

    if count == 0:
        st.info("No valid movies to show.")
        return

    st.markdown(grid_html, unsafe_allow_html=True)


def render_details_page(data, tmdb_id):
    title = data.get("title") or "Untitled"
    overview = data.get("overview") or "No overview available."
    release = data.get("release_date") or "Unknown"
    poster = data.get("poster_url")
    backdrop = data.get("backdrop_url")

    genre_names = []

    for g in data.get("genres", []):
        if isinstance(g, dict) and g.get("name"):
            genre_names.append(g["name"])
        elif isinstance(g, str):
            genre_names.append(g)

    genres_text = ", ".join(genre_names) if genre_names else "Unknown Genre"

    rating = data.get("vote_average")
    runtime = data.get("runtime")

    rating_html = ""
    if rating:
        try:
            rating_html = f"<span class='detail-pill'>⭐ {round(float(rating), 1)}/10</span>"
        except Exception:
            rating_html = ""

    runtime_html = f"<span class='detail-pill'>⏱ {esc(runtime)} min</span>" if runtime else ""

    if poster:
        poster_html = f"<img class='detail-poster' src='{esc_attr(poster)}' alt='{esc_attr(title)}'>"
    else:
        poster_html = "<div class='detail-fallback'>🎬</div>"

    if backdrop:
        bg_style = f"background-image: url('{esc_attr(backdrop)}');"
    else:
        bg_style = "background-image: linear-gradient(135deg, #141414, #050505);"

    detail_html = (
        f"<div class='detail-hero' style=\"{bg_style}\">"
        f"<div class='detail-inner'>"
        f"<div>{poster_html}</div>"
        f"<div>"
        f"<div class='detail-kicker'>Now Showing</div>"
        f"<div class='detail-title'>{esc(title)}</div>"
        f"<div class='detail-pills'>"
        f"<span class='detail-pill'>📅 {esc(release)}</span>"
        f"<span class='detail-pill'>🎭 {esc(genres_text)}</span>"
        f"<span class='detail-pill'>🆔 TMDB {esc(tmdb_id)}</span>"
        f"{rating_html}"
        f"{runtime_html}"
        f"</div>"
        f"<div class='detail-overview'>{esc(overview)}</div>"
        f"</div>"
        f"</div>"
        f"</div>"
    )

    st.markdown(detail_html, unsafe_allow_html=True)


# =============================
# APP
# =============================
if not st.session_state.get("authenticated"):
    render_auth_page()
    st.stop()

render_header()

# =============================
# HOME PAGE
# =============================
if st.session_state.view == "home":
    render_hero()

    typed = render_search()

    if typed.strip():
        if len(typed.strip()) < 2:
            st.caption("Type at least 2 characters for suggestions.")
            st.stop()

        data, err = api_get_json("/tmdb/search", params={"query": typed.strip()})

        if err or data is None:
            st.error(f"Search failed: {err}")
            st.stop()

        suggestions, cards = parse_tmdb_search_to_cards(data, typed.strip(), limit=30)

        if suggestions:
            labels = ["-- Select a movie --"] + [s[0] for s in suggestions]
            selected = st.selectbox("Smart Suggestions", labels, index=0)

            if selected != "-- Select a movie --":
                label_to_id = {s[0]: s[1] for s in suggestions}
                selected_id = label_to_id[selected]
                st.session_state.selected_tmdb_id = int(selected_id)
                st.session_state.view = "details"
                st.query_params["view"] = "details"
                st.query_params["id"] = str(int(selected_id))
                st.rerun()
        else:
            st.info("No suggestions found. Try another keyword.")

        section_title("Search Results", f"Showing movies matching: {typed.strip()}")
        poster_grid(cards, cols=6)
        st.stop()

    clean_category = clean_category_name(st.session_state.home_category)

    section_title(clean_category, "Browse cinematic movie posters from your selected feed.")

    home_cards, err = api_get_json(
        "/home",
        params={"category": st.session_state.home_category, "limit": 30},
    )

    if err or not home_cards:
        st.error(f"Home feed failed: {err or 'Unknown error'}")
        st.stop()

    poster_grid(home_cards, cols=6)

# =============================
# DETAILS PAGE
# =============================
elif st.session_state.view == "details":
    tmdb_id = st.session_state.selected_tmdb_id

    if not tmdb_id:
        st.warning("No movie selected.")
        st.stop()

    data, err = api_get_json(f"/movie/id/{tmdb_id}")

    if err or not data:
        st.error(f"Could not load details: {err or 'Unknown error'}")
        st.stop()

    render_details_page(data, tmdb_id)

    title = (data.get("title") or "").strip()

    section_title("Recommended For You", "Similar movies generated from your selected movie.")

    if title:
        bundle, err2 = api_get_json(
            "/movie/search",
            params={"query": title, "tfidf_top_n": 12, "genre_limit": 12},
        )

        if not err2 and bundle:
            tfidf_cards = to_cards_from_tfidf_items(bundle.get("tfidf_recommendations"))
            genre_cards = bundle.get("genre_recommendations", [])
            all_recommendations = merge_unique_cards(tfidf_cards, genre_cards)

            poster_grid(all_recommendations, cols=6)

        else:
            genre_only, err3 = api_get_json(
                "/recommend/genre",
                params={"tmdb_id": tmdb_id, "limit": 18},
            )

            if not err3 and genre_only:
                poster_grid(genre_only, cols=6)
            else:
                st.warning("No recommendations available right now.")
    else:
        st.warning("No title available to compute recommendations.")

# =============================
# ACCOUNT PAGE
# =============================
elif st.session_state.view == "account":
    user = st.session_state.get("user") or {}
    username = esc(user.get("username", "User"))
    email = esc(user.get("email", ""))
    created_at = esc(str(user.get("created_at", ""))[:19].replace("T", " "))

    account_html = (
        "<div class='simple-page'>"
        "<h1>👤 Account</h1>"
        f"<p><strong>Username:</strong> {username}</p>"
        f"<p><strong>Email:</strong> {email}</p>"
        f"<p><strong>Account Created:</strong> {created_at if created_at else 'Saved in SQLite database'}</p>"
        "<p>Your MovieFlix account is active. You can now extend this area with watchlist, saved movies, ratings, and personalized recommendations.</p>"
        "</div>"
    )

    st.markdown(account_html, unsafe_allow_html=True)

    if st.button("Logout"):
        st.session_state.authenticated = False
        st.session_state.user = None
        st.session_state.auth_view = "login"
        try:
            st.query_params.clear()
        except Exception:
            pass
        st.rerun()

# =============================
# HELP PAGE
# =============================
elif st.session_state.view == "help":
    help_html = (
        "<div class='simple-page'>"
        "<h1>❔ Help Center</h1>"
        "<p>Use the search bar to find a movie. Select from suggestions or click any poster to open details. Recommendations appear below the selected movie.</p>"
        "</div>"
    )

    st.markdown(help_html, unsafe_allow_html=True)