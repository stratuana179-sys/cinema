import pandas as pd
import numpy as np

class MovieRecommender:
    def __init__(self, movies_path="data/movies.csv", ratings_path="data/users_ratings.csv"):
        import os
        # fallback: if data/ doesn't exist, look in current folder
        if not os.path.exists(movies_path):
            if os.path.exists("movies.csv"):
                movies_path = "movies.csv"
            elif os.path.exists("data/movies.csv"):
                movies_path = "data/movies.csv"
        if not os.path.exists(ratings_path):
            if os.path.exists("users_ratings.csv"):
                ratings_path = "users_ratings.csv"
            elif os.path.exists("data/users_ratings.csv"):
                ratings_path = "data/users_ratings.csv"
        self.movies = pd.read_csv(movies_path)
        self.ratings = pd.read_csv(ratings_path)
        self.movies['genres_list'] = self.movies['genres'].apply(lambda x: x.split('|'))
        # Creeaza matrice genuri
        all_genres = sorted(list(set(g for sub in self.movies['genres_list'] for g in sub)))
        self.all_genres = all_genres
        for g in all_genres:
            self.movies[g] = self.movies['genres_list'].apply(lambda x: 1 if g in x else 0)
        self.genre_matrix = self.movies[all_genres].values.astype(float)
        # Normalizare pentru cosine
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
        # KNN simulat = cosine sortat, ia top N cei mai apropiati
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
        # exclude deja vazute
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
        # K-Means simplu: grupeaza filmele dupa gen, recomanda din acelasi cluster cu profilul
        from collections import Counter
        # atribuim cluster = genul dominant
        # Pentru simplitate: cluster = primul gen
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
        
        # gaseste genul dominant din profil
        top_genre_idx = np.argmax(profile)
        top_genre = self.all_genres[top_genre_idx]
        # recomanda filme cu acel gen
        if user_id:
            seen = self.ratings[self.ratings['user_id']==user_id]['movie_id'].tolist()
            candidates = self.movies[(self.movies[top_genre]==1) & (~self.movies['movie_id'].isin(seen))]
        else:
            candidates = self.movies[self.movies[top_genre]==1]
        
        sims = self.cosine_similarity_manual(profile)
        candidates = candidates.copy()
        # map similarity
        cand_idx = candidates.index.tolist()
        candidates['similarity'] = [sims[i] for i in cand_idx]
        if len(candidates) < n:
            # completeaza cu cosine general
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
