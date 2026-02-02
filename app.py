import textwrap
from collections import Counter

import requests
import streamlit as st


def apply_styles() -> None:
    st.markdown(
        """
        <style>
        .main {
            background: radial-gradient(circle at top, #0f172a, #1e293b 60%, #020617 100%);
            color: #e2e8f0;
        }
        .quiz-card {
            background: rgba(15, 23, 42, 0.85);
            border-radius: 16px;
            padding: 20px;
            box-shadow: 0 12px 28px rgba(15, 23, 42, 0.35);
            margin-bottom: 20px;
        }
        .result-title {
            font-size: 26px;
            font-weight: 800;
            color: #38bdf8;
            margin-bottom: 8px;
        }
        .badge {
            display: inline-block;
            padding: 6px 14px;
            border-radius: 999px;
            background: rgba(56, 189, 248, 0.2);
            color: #7dd3fc;
            font-weight: 600;
        }
        .movie-card {
            background: rgba(15, 23, 42, 0.9);
            border-radius: 16px;
            padding: 16px;
            border: 1px solid rgba(148, 163, 184, 0.2);
            box-shadow: inset 0 0 0 1px rgba(15, 23, 42, 0.2);
        }
        .rating {
            font-weight: 700;
            color: #facc15;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def build_questions() -> list[dict]:
    return [
        {
            "text": "주말에 가장 하고 싶은 일은?",
            "options": [
                ("즉흥적으로 모험 떠나기", "action"),
                ("친구들과 배꼽 잡는 파티", "comedy"),
                ("깊이 있는 생각을 하며 산책", "drama"),
            ],
        },
        {
            "text": "영화를 볼 때 중요한 요소는?",
            "options": [
                ("화려한 비주얼과 미래 세계", "sci-fi"),
                ("두근두근 설레는 감정", "romance"),
                ("마법 같은 상상력", "fantasy"),
            ],
        },
        {
            "text": "친구가 당신을 한 단어로 표현한다면?",
            "options": [
                ("에너지 넘치는 추진력", "action"),
                ("분위기 메이커", "comedy"),
                ("따뜻하고 공감하는 사람", "romance"),
            ],
        },
        {
            "text": "선호하는 이야기 전개는?",
            "options": [
                ("빠르고 긴장감 있는 전개", "action"),
                ("잔잔하지만 여운이 남는 전개", "drama"),
                ("현실을 넘어선 세계", "fantasy"),
            ],
        },
        {
            "text": "지금 가장 필요한 감정은?",
            "options": [
                ("통쾌함과 스릴", "action"),
                ("웃음과 기분 전환", "comedy"),
                ("따뜻한 위로", "drama"),
            ],
        },
    ]


def build_genre_config() -> dict:
    return {
        "action": {
            "label": "액션",
            "id": 28,
            "reason": "에너지 넘치는 도전을 즐기는 성향이 강해요.",
        },
        "comedy": {
            "label": "코미디",
            "id": 35,
            "reason": "웃음과 활기를 통해 기분 전환을 원해요.",
        },
        "drama": {
            "label": "드라마",
            "id": 18,
            "reason": "깊이 있는 감정선을 통해 공감을 찾는 편이에요.",
        },
        "sci-fi": {
            "label": "SF",
            "id": 878,
            "reason": "미래적 상상력과 새로운 세계관에 끌려요.",
        },
        "romance": {
            "label": "로맨스",
            "id": 10749,
            "reason": "설레는 관계의 흐름에서 힐링을 느껴요.",
        },
        "fantasy": {
            "label": "판타지",
            "id": 14,
            "reason": "현실을 넘어선 이야기에 몰입하는 것을 좋아해요.",
        },
    }


def pick_genre(answers: list[str], genre_config: dict) -> str:
    counts = Counter(answers)
    if not counts:
        return "drama"
    return max(counts.items(), key=lambda item: (item[1], item[0]))[0]


def fetch_movies(api_key: str, genre_id: int) -> list[dict]:
    endpoint = "https://api.themoviedb.org/3/discover/movie"
    params = {
        "api_key": api_key,
        "with_genres": genre_id,
        "language": "ko-KR",
        "sort_by": "popularity.desc",
    }
    response = requests.get(endpoint, params=params, timeout=10)
    response.raise_for_status()
    payload = response.json()
    return payload.get("results", [])[:5]


def render_results(genre_key: str, movies: list[dict], genre_config: dict) -> None:
    config = genre_config[genre_key]
    reason_text = textwrap.dedent(
        f"""
        당신의 답변을 분석한 결과 {config['label']} 성향이 가장 두드러졌어요.
        {config['reason']}
        """
    ).strip()

    st.markdown(
        f"""
        <div class="quiz-card">
            <div class="result-title">당신에게 딱인 장르는: {config['label']}!</div>
            <div class="badge">#{config['label']} 추천</div>
            <p>{reason_text}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    columns = st.columns(3)
    poster_base = "https://image.tmdb.org/t/p/w500"

    for index, movie in enumerate(movies):
        column = columns[index % 3]
        with column:
            with st.container():
                st.markdown('<div class="movie-card">', unsafe_allow_html=True)
                poster_path = movie.get("poster_path")
                if poster_path:
                    st.image(f"{poster_base}{poster_path}", use_container_width=True)
                else:
                    st.image("https://via.placeholder.com/500x750?text=No+Image", use_container_width=True)

                st.markdown(
                    f"<div style='font-weight:700;'>{movie.get('title', '제목 없음')}</div>",
                    unsafe_allow_html=True,
                )
                st.markdown(
                    f"<div class='rating'>⭐ {movie.get('vote_average', 0):.1f}</div>",
                    unsafe_allow_html=True,
                )
                with st.expander("상세 정보 보기"):
                    st.write(movie.get("overview") or "줄거리 정보가 없습니다.")
                    st.write(f"이 영화를 추천하는 이유: {config['reason']}")
                st.markdown("</div>", unsafe_allow_html=True)


def main() -> None:
    st.set_page_config(page_title="심리테스트 영화 추천", layout="wide")
    apply_styles()

    st.title("심리테스트 영화 추천")
    st.write("질문에 답하고 결과를 확인해보세요! TMDB 인기 영화 5편을 추천합니다.")

    api_key = st.sidebar.text_input("TMDB API Key", type="password")
    st.sidebar.caption("API Key는 로컬에 저장되지 않습니다.")

    questions = build_questions()
    genre_config = build_genre_config()
    answers = []

    for index, question in enumerate(questions, start=1):
        st.markdown('<div class="quiz-card">', unsafe_allow_html=True)
        st.subheader(f"Q{index}. {question['text']}")
        options = [label for label, _ in question["options"]]
        selection = st.radio(
            "",
            options,
            key=f"question_{index}",
            label_visibility="collapsed",
        )
        st.markdown("</div>", unsafe_allow_html=True)
        mapped = {label: genre for label, genre in question["options"]}
        answers.append(mapped.get(selection))

    if st.button("결과 보기", type="primary"):
        if not api_key:
            st.error("TMDB API Key를 입력해주세요.")
            return
        if any(answer is None for answer in answers):
            st.error("모든 질문에 답해주세요.")
            return

        with st.spinner("TMDB 추천 영화를 가져오는 중..."):
            try:
                chosen_genre = pick_genre(answers, genre_config)
                movies = fetch_movies(api_key, genre_config[chosen_genre]["id"])
            except requests.RequestException:
                st.error("TMDB 데이터를 불러오지 못했습니다. API Key를 확인해주세요.")
                return

        render_results(chosen_genre, movies, genre_config)


if __name__ == "__main__":
    main()
