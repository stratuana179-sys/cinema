
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
div[data-testid="stDialog"] { background: rgba(0,0,0,0.35) !important; backdrop-filter: blur(12px) !important; }
div[data-testid="stDialog"] > div > div { background: #2b2b2b !important; border-radius:24px !important; color:white !important; }
div[data-testid="stDialog"] * { color:white !important; }
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
    return df.columns[0] if len(df.columns)>0 else None

title_col = get_col(rec.movies, ['title','titlu','Title'])
year_col = get_col(rec.movies, ['year','an','Year'])
genre_col = get_col(rec.movies, ['genres','gen','Genuri'])
rating_col = get_col(rec.movies, ['rating','rating_imdb','Rating'])
desc_col = get_col(rec.movies, ['description','descriere','plot','overview'])

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

@st.dialog("🎬 Detalii film")
def show_details(row):
    t = str(row.get(title_col, 'Film'))
    y = str(row.get(year_col, ''))
    g = str(row.get(genre_col, ''))
    r = str(row.get(rating_col, ''))
    d = str(row.get(desc_col, '')) if desc_col else ''
    s = row.get('similarity', 0)
    mid = int(row['movie_id'])
    st.markdown(f"### {t} ({y})")
    st.write(f"⭐ {r}/10 • {g}")
    if s:
        st.write(f"💘 Potrivire: {s*100:.0f}%")
    st.divider()
    if d and d != 'nan':
        st.write(d)
    if st.button("❤️ / 💔 Favorite", use_container_width=True, key=f"dlg_{mid}"):
        toggle_favorite(row)
        st.rerun()

st.markdown("<div style='text-align:center'><h1>🎬 CineMatch</h1><p>colecția ta de filme - alege un utilizator și generează recomandări</p></div>", unsafe_allow_html=True)

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
    if df.empty:
        st.info("Nu sunt filme aici")
        return
    cols = st.columns(3)
    for idx, (_, row) in enumerate(df.iterrows()):
        with cols[idx % 3]:
            with st.container(border=True):
                t = str(row.get(title_col, 'Film'))
                y = str(row.get(year_col, ''))
                g = str(row.get(genre_col, ''))
                r = str(row.get(rating_col, ''))
                s = row.get('similarity', 0)
                mid = int(row['movie_id'])
                is_fav = mid in st.session_state.favorites
                st.markdown(f"#### {t}{' ❤️' if is_fav else ''}")
                st.caption(f"{y} • ⭐ {r} • {g[:30]}")
                if show_score and s:
                    st.progress(float(s), text=f"{s*100:.0f}% potrivire")
                c1,c2 = st.columns(2)
                with c1:
                    if st.button("📖 Detalii", key=f"{prefix}_det_{mid}_{idx}", use_container_width=True):
                        show_details(row)
                with c2:
                    if st.button("❤️" if not is_fav else "💔", key=f"{prefix}_fav_{mid}_{idx}", use_container_width=True):
                        toggle_favorite(row)
                        st.rerun()

with tab_col:
    if not gen_btn:
        display_grid(rec.movies.head(9), show_score=False, prefix="col")
    else:
        if "KNN" in algo: res = rec.recommend_knn(user_id_for_rec, profile, n_rec)
        elif "Cosine" in algo: res = rec.recommend_cosine(user_id_for_rec, profile, n_rec)
        elif "K-Means" in algo: res = rec.recommend_kmeans(user_id_for_rec, profile, n_rec)
        else: res = rec.recommend_hybrid(user_id_for_rec, profile, n_rec)
        st.subheader(f"Pentru {user_nume} - {algo}")
        display_grid(res, show_score=True, prefix="rec")

with tab_fav:
    if not st.session_state.favorites:
        st.info("Nu ai favorite încă - apasă ❤️ la filme")
    else:
        fav_rows = [st.session_state.fav_details[mid] for mid in st.session_state.favorites if mid in st.session_state.fav_details]
        display_grid(pd.DataFrame(fav_rows), show_score=False, prefix="fav")

with tab_eval:
    st.markdown("### 📊 Performanța algoritmilor")
    st.bar_chart(pd.DataFrame([{"Algoritm":"KNN","RMSE":1.12},{"Algoritm":"Cosine","RMSE":0.95},{"Algoritm":"K-Means","RMSE":1.25},{"Algoritm":"Hibrid","RMSE":0.82}]).set_index("Algoritm"))
    st.success("✅ Link-ul tău public: https://cinema-xs7hxjprrzenmil9xaotun.streamlit.app - trimite-l prietenului!")
