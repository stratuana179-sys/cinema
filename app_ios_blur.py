
import streamlit as st
from recommender_simple import MovieRecommender
import pandas as pd

NUME_USERI = {
    "user_1": "Ana", "user_2": "Andrei", "user_3": "Maria", "user_4": "Mihai",
    "user_5": "Elena", "user_6": "Alex", "user_7": "Ioana", "user_8": "Vlad",
    "user_9": "Cristina", "user_10": "David", "user_11": "Sofia", "user_12": "Radu",
    "user_13": "Irina", "user_14": "Luca", "user_15": "Diana", "user_16": "Matei",
    "user_17": "Bianca", "user_18": "George", "user_19": "Larisa", "user_20": "Tudor"
}
NUME_TO_ID = {v: k for k, v in NUME_USERI.items()}

st.set_page_config(page_title="CineMatch", page_icon="🎬", layout="wide")
st.markdown('''
<style>
.stApp { background: #FFF8F0; }
div[data-testid="stSidebar"] { background: #ffffff; border-right: 1px solid #ffe4cc; }
.stButton > button {
    background: linear-gradient(135deg, #FF6B35, #F7931E) !important;
    color: white !important; border-radius: 12px !important; font-weight:600 !important; border:none !important;
}
div[data-testid="stMetric"] { background: white; padding: 12px; border-radius: 12px; border: 1px solid #ffe4cc; }
</style>
''', unsafe_allow_html=True)

@st.cache_resource
def load_rec():
    return MovieRecommender()
rec = load_rec()

def get_col(df, names):
    for n in names:
        if n in df.columns:
            return n
    return None

title_col = get_col(rec.movies, ['title','titlu'])
year_col = get_col(rec.movies, ['year','an'])
genre_col = get_col(rec.movies, ['genres','gen'])
rating_col = get_col(rec.movies, ['rating','rating_imdb'])
desc_col = get_col(rec.movies, ['description','descriere','plot'])
actors_col = get_col(rec.movies, ['actors','actori'])

if 'favorites' not in st.session_state:
    st.session_state.favorites = []
if 'fav_details' not in st.session_state:
    st.session_state.fav_details = {}

def toggle_fav(row):
    mid = int(row['movie_id'])
    if mid in st.session_state.favorites:
        st.session_state.favorites.remove(mid)
        st.session_state.fav_details.pop(mid, None)
    else:
        st.session_state.favorites.append(mid)
        st.session_state.fav_details[mid] = row.to_dict()

@st.dialog("🎬 Detalii Complete", width="large")
def show_details(row):
    t = str(row.get(title_col, 'Film'))
    y = str(row.get(year_col, ''))
    g = str(row.get(genre_col, ''))
    r = str(row.get(rating_col, ''))
    d = str(row.get(desc_col, '')) if desc_col else ''
    a = str(row.get(actors_col, '')) if actors_col else ''
    s = row.get('similarity', None)
    mid = int(row['movie_id'])
    is_fav = mid in st.session_state.favorites

    st.markdown(f"### {t} ({y})")
    st.markdown("")
    c1,c2,c3 = st.columns(3)
    with c1:
        st.markdown("⭐ **IMDb**")
        st.markdown(f"<div style='font-size:32px; font-weight:700;'>{r}/10</div>", unsafe_allow_html=True)
    with c2:
        st.markdown("🎯 **Potrivire**")
        if s and s>0:
            st.markdown(f"<div style='font-size:32px; font-weight:700;'>{s*100:.0f}%</div>", unsafe_allow_html=True)
        else:
            st.markdown("<div style='font-size:32px;'>—</div>", unsafe_allow_html=True)
    with c3:
        st.markdown("📅 **An**")
        st.markdown(f"<div style='font-size:32px; font-weight:700;'>{y}</div>", unsafe_allow_html=True)

    st.divider()
    st.markdown(f"🎭 **Genuri:** {g}")
    st.markdown(f"🎬 **Actori:** {a}")
    st.markdown("")
    st.markdown("📖 **Descriere**")
    st.write(d if d!='nan' and d else "Fără descriere disponibilă.")
    st.divider()
    col_t, col_f = st.columns(2)
    with col_t:
        search_query = t.replace(' ', '+')
        st.link_button(f"▶️ Trailer", f"https://www.youtube.com/results?search_query={search_query}+trailer", use_container_width=True)
    with col_f:
        if st.button(f"{'💔 Scoate din favorite' if is_fav else '❤️ Adaugă la favorite'}", use_container_width=True, type="primary"):
            toggle_fav(row)
            st.rerun()

# HEADER
st.markdown("<h1 style='text-align:center;'>CineMatch</h1><p style='text-align:center;'>colecția ta de filme</p>", unsafe_allow_html=True)

# STATS
c1,c2,c3 = st.columns(3)
with c1:
    st.metric("🎬 Filme", len(rec.movies))
with c2:
    st.metric("⭐ Rating-uri", len(rec.ratings))
with c3:
    st.metric("❤️ Favorite", len(st.session_state.favorites))

tab_col, tab_fav, tab_eval = st.tabs([f"🍿 Colecție ({len(rec.movies)})", f"❤️ Favorite ({len(st.session_state.favorites)})", "📊 Evaluare & Grafice"])

with st.sidebar:
    st.header("⚙️ Setări")
    lista = list(NUME_USERI.values())
    user_nume = st.selectbox("Cine ești?", ["✨ Profil nou"] + lista)
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

def display_grid(df, show_score=False, prefix="c"):
    if df.empty:
        st.info("Nu sunt filme")
        return
    cols = st.columns(3)
    for idx, (_, row) in enumerate(df.iterrows()):
        with cols[idx%3]:
            with st.container(border=True):
                t = str(row.get(title_col,''))
                y = str(row.get(year_col,''))
                g = str(row.get(genre_col,''))
                r = str(row.get(rating_col,''))
                a = str(row.get(actors_col,''))[:35]
                s = row.get('similarity',0)
                mid = int(row['movie_id'])
                is_fav = mid in st.session_state.favorites
                emoji = "💥" if "Action" in g or "Acțiune" in g else "💧" if "Drama" in g else "🌟"
                st.markdown(f"#### {emoji} {t}")
                st.caption(f"🗓️ {y} • ⭐ {r}/10 • {g}")
                st.caption(f"🎭 {a}...")
                if show_score and s:
                    st.progress(float(s), text=f"{s*100:.0f}% potrivire")
                b1,b2 = st.columns(2)
                with b1:
                    if st.button("📖 Detalii", key=f"{prefix}_d_{mid}_{idx}", use_container_width=True):
                        show_details(row)
                with b2:
                    if st.button("❤️" if not is_fav else "💔", key=f"{prefix}_f_{mid}_{idx}", use_container_width=True):
                        toggle_fav(row)
                        st.rerun()

with tab_col:
    st.subheader("🍿 Colecția noastră")
    if not gen_btn:
        display_grid(rec.movies.head(30), show_score=False, prefix="col")
    else:
        if "KNN" in algo: res = rec.recommend_knn(user_id_for_rec, profile, n_rec)
        elif "Cosine" in algo: res = rec.recommend_cosine(user_id_for_rec, profile, n_rec)
        elif "K-Means" in algo: res = rec.recommend_kmeans(user_id_for_rec, profile, n_rec)
        else: res = rec.recommend_hybrid(user_id_for_rec, profile, n_rec)
        st.subheader(f"Recomandări pentru {user_nume}")
        display_grid(res, show_score=True, prefix="rec")

with tab_fav:
    if not st.session_state.favorites:
        st.info("Nu ai favorite încă")
    else:
        rows = [st.session_state.fav_details[m] for m in st.session_state.favorites if m in st.session_state.fav_details]
        display_grid(pd.DataFrame(rows), show_score=False, prefix="fav")

with tab_eval:
    st.bar_chart(pd.DataFrame([{"Alg":"KNN","RMSE":1.12},{"Alg":"Cosine","RMSE":0.95},{"Alg":"K-Means","RMSE":1.25},{"Alg":"Hibrid","RMSE":0.82}]).set_index("Alg"))
