import streamlit as st
import pandas as pd
import pickle
import requests
import time
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# ---------------------- Create a single reusable session ----------------------
session = requests.Session()

retry = Retry(
    total=5,
    connect=5,
    read=5,
    backoff_factor=1,
    status_forcelist=[429, 500, 502, 503, 504],
    allowed_methods=["GET"]
)

adapter = HTTPAdapter(max_retries=retry)
session.mount("https://", adapter)
session.mount("http://", adapter)

API_KEY = "cd5f573cc81bec634d378ed5780b0d73"

PLACEHOLDER = "https://via.placeholder.com/500x750?text=No+Poster"

# ---------------------- Fetch Poster ----------------------
def fetch_poster(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}"

    params = {
        "api_key": API_KEY,
        "language": "en-US"
    }

    try:
        response = session.get(url, params=params, timeout=10)
        response.raise_for_status()

        data = response.json()

        poster_path = data.get("poster_path")

        if poster_path:
            return "https://image.tmdb.org/t/p/w500" + poster_path
        else:
            print(f"No poster available for movie id {movie_id}")
            return PLACEHOLDER

    except requests.exceptions.RequestException as e:
        print(f"Network Error ({movie_id}): {e}")
        return PLACEHOLDER

    except Exception as e:
        print(f"Unexpected Error ({movie_id}): {e}")
        return PLACEHOLDER


# ---------------------- Recommend Movies ----------------------
def recommend(movie):
    movie_index = movies[movies["title"] == movie].index[0]

    distances = similarity[movie_index]

    movies_list = sorted(
        list(enumerate(distances)),
        key=lambda x: x[1],
        reverse=True
    )[1:6]

    recommended_movies = []
    recommended_posters = []

    for item in movies_list:
        movie = movies.iloc[item[0]]

        recommended_movies.append(movie.title)
        recommended_posters.append(fetch_poster(movie.id))

        # Prevent rapid-fire API requests
        time.sleep(0.2)

    return recommended_movies, recommended_posters


# ---------------------- Load Data ----------------------
movies_dict = pickle.load(open("movies_dict.pkl", "rb"))
movies = pd.DataFrame(movies_dict)

similarity = pickle.load(open("similarity.pkl", "rb"))

# ---------------------- Streamlit UI ----------------------
st.title("🎬 Movie Recommender System")

selected_movie = st.selectbox(
    "Select a Movie",
    movies["title"].values
)

if st.button("Recommend"):

    names, posters = recommend(selected_movie)

    cols = st.columns(5)

    for i in range(5):
        with cols[i]:
            st.text(names[i])
            st.image(posters[i], use_container_width=True)