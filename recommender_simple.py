
import pandas as pd
import numpy as np
import os

class MovieRecommender:
    def __init__(self, movies_path="data/movies.csv", ratings_path="data/users_ratings.csv"):
        # fallback paths
        if not os.path.exists(movies_path):
            for alt in ["movies.csv", "data/movies.csv", "./movies.csv"]:
                if os.path.exists(alt):
                    movies_path = alt
                    break
        if not os.path.exists(ratings_path):
            for alt in ["users_ratings.csv", "data/users_ratings.csv", "./users_ratings.csv"]:
                if os.path.exists(alt):
                    ratings_path = alt
                    break

        self.movies = pd.read_csv(movies_path)
        self.ratings = pd.read_csv(ratings_path)

        # --- Normalize Romanian -> English column names ---
        rename_map = {
            'titlu': 'title',
            'gen': 'genres',
            'an': 'year',
            'rating_imdb': 'rating',
            'actori': 'actors',
            'descriere': 'description'
        }
        for old, new in rename_map.items():
            if old in self.movies.columns and new not in self.movies.columns:
                self.movies.rename(columns={old: new}, inplace=True)

        # ensure required columns exist
        if 'genres' not in self.movies.columns:
            # try find any column containing '|'
            for col in self.movies.columns:
                try:
                    if self.movies[col].astype(str).str.contains(r'\|').any():
                        self.movies['genres'] = self.movies[col]
                        break
                except:
                    pass

        if 'genres' not in self.movies.columns:
            self.movies['genres'] = 'Drama'

        self.movies['genres'] = self.movies['genres'].fillna('Drama').astype(str)
        self.movies['genres_list'] = self.movies['genres'].apply(lambda x: [g.strip() for g in x.split('|') if g.strip()])

        all_genres = sorted(list(set(g for sub in self.movies['genres_list'] for g in sub)))
        self.all_genres = all_genres
        for g in all_genres:
            self.movies[g] = self.movies['genres_list'].apply(lambda x: 1 if g in x else 0)
        self.genre_matrix = self.movies[all_genres].values.astype(float)
        norms = np.linalg.norm(self.genre_matrix, axis=1, keepdims=True)
        norms[norms==0]=1
        self.genre_matrix_norm = self.genre_matrix / norms

    def cosine_similarity_manual(self, vec):
        vec = vec.astype(float)
        norm = np.linalg.norm(vec)
        if norm==0: norm=1
        vec = vec / norm
        sims = self.genre_matrix_norm @ vec
        return sims

    def recommend_knn(self, user_id=None, user_profile=None, n=10):
        if user_profile is None:
            user_ratings = self.ratings[self.ratings['user_id']==user_id]
            profile = np.zeros(len(self.all_genres))
            for _, r in user_ratings.iterrows():
                mid = r['movie_id']
                rating = r['rating']
                idx = self.movies[self.movies['movie_id']==mid].index
                if len(idx)>0:
                    profile += self.genre_matrix[idx[0]] * rating
        else:
            profile = user_profile
        sims = self.cosine_similarity_manual(profile)
        if user_id:
            seen = self.ratings[self.ratings['user_id']==user_id]['movie_id'].tolist()
            mask = ~self.movies['movie_id'].isin(seen)
        else:
            mask = np.ones(len(self.movies), dtype=bool)
        df = self.movies[mask].copy()
        df['similarity'] = sims[mask]
        return df.sort_values('similarity', ascending=False).head(n)

    def recommend_cosine(self, user_id=None, user_profile=None, n=10):
        return self.recommend_knn(user_id, user_profile, n)

    def recommend_kmeans(self, user_id=None, user_profile=None, n=10, k=6):
        if user_profile is None:
            user_ratings = self.ratings[self.ratings['user_id']==user_id]
            profile = np.zeros(len(self.all_genres))
            for _, r in user_ratings.iterrows():
                mid = r['movie_id']
                rating = r['rating']
                idx = self.movies[self.movies['movie_id']==mid].index
                if len(idx)>0:
                    profile += self.genre_matrix[idx[0]] * rating
        else:
            profile = user_profile
        top_genre_idx = int(np.argmax(profile)) if len(profile)>0 else 0
        top_genre = self.all_genres[top_genre_idx] if self.all_genres else 'Drama'
        if user_id:
            seen = self.ratings[self.ratings['user_id']==user_id]['movie_id'].tolist()
            candidates = self.movies[(self.movies[top_genre]==1) & (~self.movies['movie_id'].isin(seen))] if top_genre in self.movies.columns else self.movies[~self.movies['movie_id'].isin(seen)]
        else:
            candidates = self.movies[self.movies[top_genre]==1] if top_genre in self.movies.columns else self.movies
        sims = self.cosine_similarity_manual(profile)
        candidates = candidates.copy()
        cand_idx = candidates.index.tolist()
        candidates['similarity'] = [sims[i] for i in cand_idx]
        if len(candidates) < n:
            return self.recommend_knn(user_id, profile, n)
        return candidates.sort_values('similarity', ascending=False).head(n)

    def recommend_hybrid(self, user_id=None, user_profile=None, n=10):
        return self.recommend_knn(user_id, user_profile, n)

    def create_new_user_profile(self, liked_genres, liked_movie_ids):
        profile = np.zeros(len(self.all_genres))
        for g in liked_genres:
            if g in self.all_genres:
                profile[self.all_genres.index(g)] += 2
        for mid in liked_movie_ids:
            idx = self.movies[self.movies['movie_id']==mid].index
            if len(idx)>0:
                profile += self.genre_matrix[idx[0]] * 2
        return profile
