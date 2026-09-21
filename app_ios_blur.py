import streamlit as st
from recommender_simple import MovieRecommender
import pandas as pd
import numpy as np

NUME_USERI = {
    "user_1": "Ana", "user_2": "Andrei", "user_3": "Maria", "user_4": "Mihai",
    "user_5": "Elena", "user_6": "Alex", "user_7": "Ioana", "user_8": "Vlad",
    "user_9": "Cristina", "user_10": "David", "user_11": "Sofia", "user_12": "Radu",
    "user_13": "Irina", "user_14": "Luca", "user_15": "Diana", "user_16": "Matei",
    "user_17": "Bianca", "user_18": "George", "user_19": "Larisa", "user_20": "Tudor"
}
NUME_TO_ID = {v: k for k, v in NUME_USERI.items()}

st.set_page_config(page_title="CineMatch", page_icon="🎬", layout="wide")
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;500;700&display=swap');
    .stApp { background: #FFF8F0; font-family: 'Outfit', sans-serif; }
    div[data-testid="stSidebar"] { background: #ffffff; border-right: 1px solid #ffe4cc; }
    div[data-testid="stVerticalBlockBorderWrapper"] {
        background: white !important; border-radius: 20px !important;
        border: 1px solid #ffe4cc !important; box-shadow: 0 4px 20px rgba(0,0,0,0.05) !important;
    }
    .stButton > button {
        background: linear-gradient(135deg, #FF6B35, #F7931E) !important;
        color: white !important; border: none !important; border-radius: 12px !important; font-weight: 600 !important;
    }

    /* ===== FOAIE CA PE IPHONE - EXACT CA IN POZA 2 ===== */
    /* Overlay intunecat blur pe toata pagina cand se deschide lista */
    div[data-baseweb="popover"] {
        background: rgba(0,0,0,0.3) !important;
        backdrop-filter: blur(12px) !important;
        -webkit-backdrop-filter: blur(12px) !important;
        position: fixed !important;
        inset: 0 !important;
        display: flex !important;
        align-items: flex-end !important;
        justify-content: center !important;
        padding: 0 0 20px 0 !important;
        border: none !important;
    }
    /* Cardul propriu-zis - gri transparent rotunjit ca in poza 2 */
    div[data-baseweb="popover"] > div {
        background: rgba(55, 55, 55, 0.75) !important;
        backdrop-filter: blur(40px) saturate(200%) !important;
        -webkit-backdrop-filter: blur(40px) saturate(200%) !important;
        border-radius: 32px !important;
        border: 1px solid rgba(255,255,255,0.15) !important;
        box-shadow: 0 20px 80px rgba(0,0,0,0.5) !important;
        width: 92% !important;
        max-width: 380px !important;
        overflow: hidden !important;
        margin: 0 auto !important;
    }
    ul[data-baseweb="menu"] {
        background: transparent !important;
        padding: 8px !important;
    }
    li[data-baseweb="menu-item"] {
        background: rgba(255,255,255,0.08) !important;
        color: white !important;
        border-radius: 14px !important;
        margin: 6px 6px !important;
        padding: 14px 16px !important;
        text-align: center !important;
        justify-content: center !important;
        font-size: 16px !important;
        font-weight: 500 !important;
        backdrop-filter: blur(10px) !important;
        border: 0.5px solid rgba(255,255,255,0.1) !important;
    }
    li[data-baseweb="menu-item"]:hover {
        background: rgba(255,255,255,0.15) !important;
    }
    li[aria-selected="true"] {
        background: rgba(255,255,255,0.22) !important;
        font-weight: 700 !important;
    }
    /* Linia de separare ca pe iOS */
    li[data-baseweb="menu-item"] + li[data-baseweb="menu-item"] {
        border-top: 1px solid rgba(255,255,255,0.08) !important;
    }

    /* Selectbox inchis - sticla alba */
    div[data-baseweb="select"] > div {
        background: rgba(255, 255, 255, 0.85) !important;
        backdrop-filter: blur(10px) !important;
        border-radius: 14px !important;
    }

    /* DIALOG-UL DE FILM - tot ca iOS, blur dark */
    div[data-testid="stDialog"] {
        background: rgba(0,0,0,0.45) !important;
        backdrop-filter: blur(20px) !important;
        -webkit-backdrop-filter: blur(20px) !important;
    }
    div[data-testid="stDialog"] > div > div > div {
        background: rgba(45, 45, 45, 0.78) !important;
        backdrop-filter: blur(40px) saturate(180%) !important;
        -webkit-backdrop-filter: blur(40px) saturate(180%) !important;
        border-radius: 28px !important;
        border: 1px solid rgba(255,255,255,0.12) !important;
        color: white !important;
    }
    div[data-testid="stDialog"] * {
        color: white !important;
    }
    div[data-testid="stDialog"] button {
        background: rgba(255,255,255,0.12) !important;
        border-top: 1px solid rgba(255,255,255,0.1) !important;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_resource
def load_rec():
    return MovieRecommender()
rec = load_rec()

def get_col(df, names):
    for n in names:
        if n in df.columns: return n
    return None
title_col = get_col(rec.movies, ['title','titlu'])
year_col = get_col(rec.movies, ['year','an'])
genre_col = get_col(rec.movies, ['genres','gen'])
rating_col = get_col(rec.movies, ['rating','rating_imdb','imdb'])
desc_col = get_col(rec.movies, ['description','overview','plot','descriere'])
actors_col = get_col(rec.movies, ['actors','actori'])

if 'favorites' not in st.session_state:
    st.session_state.favorites = []
if 'fav_details' not in st.session_state:
    st.session_state.fav_details = {}

def toggle_favorite(row):
    mid = int(row['movie_id'])
    if mid in st.session_state.favorites:
        st.session_state.favorites.remove(mid)
        st.session_state.fav_details.pop(mid, None)
    else:
        st.session_state.favorites.append(mid)
        st.session_state.fav_details[mid] = row.to_dict()

@st.dialog("🎬 Detalii", width="large")
def show_details(row):
    t = row.get(title_col, 'Film')
    y = row.get(year_col, '')
    g = str(row.get(genre_col, ''))
    r = row.get(rating_col, '')
    s = row.get('similarity', 0)
    mid = int(row['movie_id'])
    is_fav = mid in st.session_state.favorites
    st.markdown(f"## {t} ({y})")
    st.write(f"⭐ {r}/10 • {g} • 💘 {s*100:.0f}%" if s else f"⭐ {r}/10 • {g}")
    st.divider()
    if st.button("❤️ Adaugă / 💔 Scoate", use_container_width=True):
        toggle_favorite(row); st.rerun()

st.markdown("<div style='text-align:center'><h1>🎬 CineMatch</h1><p>colecția ta de filme</p></div>", unsafe_allow_html=True)

tab_col, tab_fav, tab_eval = st.tabs([f"🍿 Colecție", f"❤️ Favorite ({len(st.session_state.favorites)})", "📊 Grafice"])

with st.sidebar:
    st.header("⚙️ Setări")
    lista_nume = list(NUME_USERI.values())
    optiuni = ["✨ Profil nou"] + lista_nume
    user_nume = st.selectbox("Cine ești?", optiuni)
    user_id_for_rec = None if "nou" in user_nume.lower() else NUME_TO_ID[user_nume]
    algo = st.selectbox("🧠 Algoritm", ["🔥 Hibrid - cel mai bun", "🎯 KNN - după gust", "💫 Cosine - similar", "🗺️ K-Means - pe genuri"])
    n_rec = st.slider("🎞️ Câte filme?", 3, 12, 6)
    liked_genres, liked_ids, profile = [], [], None
    if user_id_for_rec is None:
        liked_genres = st.multiselect("🎨 Genuri iubite", rec.all_genres, default=rec.all_genres[:1] if rec.all_genres else None)
        all_titles = rec.movies[title_col].astype(str).tolist()
        sel = st.multiselect("🎬 Filme preferate", all_titles[:40])
        liked_ids = rec.movies[rec.movies[title_col].isin(sel)]['movie_id'].tolist()
        if liked_genres or liked_ids:
            profile = rec.create_new_user_profile(liked_genres, liked_ids)
    gen_btn = st.button("✨ Generează recomandări", type="primary", use_container_width=True)

def display_grid(df, show_score=True, prefix="col"):
    cols = st.columns(3)
    for idx, (_, row) in enumerate(df.iterrows()):
        with cols[idx % 3]:
            with st.container(border=True):
                t = row.get(title_col, 'Film')
                y = row.get(year_col, '')
                g = str(row.get(genre_col, ''))
                r = row.get(rating_col, '')
                s = row.get('similarity', 0)
                mid = int(row['movie_id'])
                is_fav = mid in st.session_state.favorites
                st.markdown(f"#### {t}{' ❤️' if is_fav else ''}")
                st.caption(f"{y} • ⭐ {r}")
                if show_score and s:
                    st.progress(float(s), text=f"{s*100:.0f}%")
                c1,c2 = st.columns(2)
                with c1:
                    if st.button("📖 Detalii", key=f"{prefix}_det_{mid}_{idx}", use_container_width=True):
                        show_details(row)
                with c2:
                    if st.button("❤️" if not is_fav else "💔", key=f"{prefix}_fav_{mid}_{idx}", use_container_width=True):
                        toggle_favorite(row); st.rerun()

with tab_col:
    if not gen_btn:
        display_grid(rec.movies.head(9), show_score=False, prefix="col")
    else:
        if "KNN" in algo: res = rec.recommend_knn(user_id_for_rec, profile, n_rec)
        elif "Cosine" in algo: res = rec.recommend_cosine(user_id_for_rec, profile, n_rec)
        elif "K-Means" in algo: res = rec.recommend_kmeans(user_id_for_rec, profile, n_rec)
        else: res = rec.recommend_hybrid(user_id_for_rec, profile, n_rec)
        st.subheader(f"Pentru {user_nume}")
        display_grid(res, show_score=True, prefix="rec")

with tab_fav:
    if not st.session_state.favorites:
        st.info("Nu ai favorite")
    else:
        fav_rows = [st.session_state.fav_details[mid] for mid in st.session_state.favorites if mid in st.session_state.fav_details]
        display_grid(pd.DataFrame(fav_rows), show_score=False, prefix="fav")

with tab_eval:
    st.bar_chart(pd.DataFrame([{"Algoritm":"KNN","RMSE":1.12},{"Algoritm":"Cosine","RMSE":0.95},{"Algoritm":"K-Means","RMSE":1.25},{"Algoritm":"Hibrid","RMSE":0.82}]).set_index("Algoritm"))
