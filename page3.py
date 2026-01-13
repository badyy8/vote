import streamlit as st
import pandas as pd
import plotly.express as px
from itertools import combinations
from collections import Counter
from data_loader import load_data, get_contestants_df


# ======================================================
# DATA LOADING (CACHED)
# ======================================================
@st.cache_data(show_spinner=True)
def get_df():
    return load_data()

@st.cache_data(show_spinner=False)
def get_candidate_party_map(df):
    m = {}
    for i in range(1, 5):
        m.update(dict(zip(df[f"choice_{i}"], df[f"party_{i}"])))
    return m

df = get_df()
district_candidate_df = get_contestants_df()
candidate_party_map = get_candidate_party_map(df)

# ======================================================
# VECTORISED FORMATTING
# ======================================================
def last_name(series: pd.Series):
    return series.str.split().str[-1]

df["district_candidate_1_with_party"] = (
    last_name(df["district_candidate_1"]) + " [" + df["district_party_1"] + "]"
)

df["district_candidate_2_with_party"] = (
    last_name(df["district_candidate_2"]) + " [" + df["district_party_2"] + "]"
)

# ======================================================
# CITY CO-VOTE PAIRS (ONCE)
# ======================================================
@st.cache_data(show_spinner=True)
def compute_city_pairs(df):
    cols = ["choice_1", "choice_2", "choice_3", "choice_4"]
    counter = Counter()

    for row in df[cols].itertuples(index=False):
        cands = sorted(set(row))
        counter.update(combinations(cands, 2))

    return (
        pd.DataFrame(
            [(a, b, c) for (a, b), c in counter.items()],
            columns=["candidate_a", "candidate_b", "count"],
        )
        .sort_values("count", ascending=False)
    )

co_vote_df = compute_city_pairs(df)

def format_candidate(name):
    if pd.isna(name):
        return name
    ln = name.split()[-1]
    party = candidate_party_map.get(name, "UNK")
    return f"{ln} ({party})"

# ======================================================
# DISTRICT PAIRS (ONCE)
# ======================================================
@st.cache_data(show_spinner=True)
def compute_district_pairs(df):
    counter = Counter()
    for a, b in zip(
        df["district_candidate_1_with_party"],
        df["district_candidate_2_with_party"],
    ):
        counter[tuple(sorted((a, b)))] += 1

    return (
        pd.DataFrame(
            [(a, b, c) for (a, b), c in counter.items()],
            columns=["candidate_a", "candidate_b", "count"],
        )
        .sort_values("count", ascending=False)
    )

district_pair_df = compute_district_pairs(df)

# ======================================================
# TABS
# ======================================================
tab1, tab2, tab3 = st.tabs(
    [
        "Хот: Хамт сонгогдсон хослол",
        "Дүүрэг: Хамт сонгогдсон хослол",
        "Дүүргийн түвшний шинжилгээ",
    ]
)

# ======================================================
# TAB 1 — CITY ANALYSIS
# ======================================================
with tab1:
    st.markdown("""
    ### Зорилго
    Хотын сонгуульд сонгогчид **ямар нэр дэвшигчдийг хамтад нь сонгож байгааг** илрүүлэх.

    ---
    ### Аргачлал
    - Саналын хуудас бүр дээр сонгогдсон **4 нэр дэвшигчээс**
      бүх боломжит хослолыг (pair) үүсгэв
    - Хос бүрийн **давтамжийг нэгтгэн** тооцоолсон
    """)

    top_pairs = co_vote_df.head(15).copy()
    top_pairs["pair_label"] = (
        "<b>"
        + top_pairs["candidate_a"].map(format_candidate)
        + "</b> + <b>"
        + top_pairs["candidate_b"].map(format_candidate)
        + "</b>"
    )

    fig = px.bar(
        top_pairs,
        x="count",
        y="pair_label",
        orientation="h",
        text="count",
        title="<b>Хотын сонгууль: Хамт сонгогдсон шилдэг 15 хослол</b>",
        template="plotly_white",
        color="count",
        color_continuous_scale="Blues",
    )

    fig.update_layout(
        height=700,
        showlegend=False,
        coloraxis_showscale=False,
        yaxis=dict(categoryorder="total ascending"),
    )

    st.plotly_chart(fig, use_container_width=True)

    st.markdown("""
    ---
    ### Гол ажиглалт
    - Хамт сонгогдож буй хослолууд нь **намаар бүлэглэн санал өгөх**
      зан төлөв давамгай байгааг харуулж байна
    - Зарим нэр дэвшигчид бусдаасаа илүү **тогтмол хамт сонгогдож** байна
    """)

# ======================================================
# TAB 2 — DISTRICT OVERALL
# ======================================================
with tab2:
    st.markdown("""
    ### Зорилго
    Дүүргийн сонгуульд **ямар хоёр нэр дэвшигч**
    хамгийн олон удаа **хамт сонгогдсон** болохыг тодорхойлох.

    """)

    top_pairs = district_pair_df.head(15).copy()
    top_pairs["pair_label"] = (
        top_pairs["candidate_a"] + " + " + top_pairs["candidate_b"]
    )

    fig = px.bar(
        top_pairs,
        x="count",
        y="pair_label",
        orientation="h",
        text="count",
        title="<b>Дүүргийн сонгууль: Хамт сонгогдсон шилдэг 15 хослол</b>",
        template="plotly_white",
        color="count",
        color_continuous_scale="Greens",
    )

    fig.update_layout(
        height=700,
        showlegend=False,
        coloraxis_showscale=False,
        yaxis=dict(categoryorder="total ascending"),
    )

    st.plotly_chart(fig, use_container_width=True)

# ======================================================
# TAB 3 — SINGLE DISTRICT DEEP DIVE
# ======================================================
with tab3:
    st.markdown("""
    ### Зорилго
    Сонгосон **нэг дүүргийн хүрээнд**
    нэр дэвшигчдийн хамтын сонголтыг
    **нарийвчлан задлан шинжлэх**.
    """)

    districts = sorted(df["district_no"].dropna().astype(int).unique())
    selected = st.selectbox("Дүүрэг сонгох", districts)

    ddf = df[df["district_no"] == selected]

    pair_counts = (
        ddf.groupby(
            [
                "district_candidate_1_with_party",
                "district_candidate_2_with_party",
            ]
        )
        .size()
        .reset_index(name="count")
        .sort_values("count", ascending=False)
    )

    pair_counts["pair_label"] = (
        "<b>"
        + pair_counts["district_candidate_1_with_party"]
        + "</b> + <b>"
        + pair_counts["district_candidate_2_with_party"]
        + "</b>"
    )

    fig = px.bar(
        pair_counts,
        x="count",
        y="pair_label",
        orientation="h",
        text="count",
        title=f"<b>{selected}-р тойрог: Хамт сонгогдсон нэр дэвшигчдийн хослол</b>",
        template="plotly_white",
        color="count",
        color_continuous_scale="Purp",
    )

    fig.update_layout(
        height=min(400 + len(pair_counts) * 30, 800),
        showlegend=False,
        coloraxis_showscale=False,
        yaxis=dict(categoryorder="total ascending"),
    )

    st.plotly_chart(fig, use_container_width=True)

    st.markdown(f"""
    ---
    ### Тайлбар ({selected}-р тойрог)
    - Энэ дүүрэгт сонгогчид **ямар хоёр нэр дэвшигчийг**
      хамтад нь сонгосныг харуулна
    """)
