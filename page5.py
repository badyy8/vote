import streamlit as st
import pandas as pd
import plotly.express as px
from collections import Counter
from data_loader import load_data

st.title("Хотын сонгууль: Намын хослолын бүтэц")


party_colors = {
    'АН': "#1D72C2",           
    'МАН': '#E21F26',          
    'ХҮН': '#6A2A85',          
    'ИЗНН': '#009543',         
    'ИОНН': "#142458",         
    'АТОЗН': '#FF8C00',        
    'ҮНДЭСНИЙ ЭВСЭЛ': "#7EB431" 
}


# ======================================================
# LOAD DATA (ONCE)
# ======================================================
@st.cache_data(show_spinner=True)
def get_df():
    return load_data()

df = get_df()

city_party_cols = ["party_1", "party_2", "party_3", "party_4"]


@st.cache_data(show_spinner=True)
def preprocess_party_patterns(df):

    # Convert to numpy for speed
    party_array = df[city_party_cols].to_numpy()

    patterns = []
    dominant_party = []
    minority_party = []
    pair_22 = []

    for row in party_array:
        counts = Counter(row)
        values = sorted(counts.values(), reverse=True)
        pattern = "-".join(map(str, values))
        patterns.append(pattern)

        if pattern == "3-1":
            dom = next(p for p, c in counts.items() if c == 3)
            mino = next(p for p, c in counts.items() if c == 1)
            dominant_party.append(dom)
            minority_party.append(mino)
            pair_22.append(None)

        elif pattern == "2-2":
            parties = sorted(p for p, c in counts.items() if c == 2)
            dominant_party.append(None)
            minority_party.append(None)
            pair_22.append(tuple(parties))

        else:
            dominant_party.append(None)
            minority_party.append(None)
            pair_22.append(None)

    df_out = df.copy()
    df_out["party_combination_pattern"] = patterns
    df_out["dominant_party"] = dominant_party
    df_out["minority_party"] = minority_party
    df_out["pair_22"] = pair_22

    return df_out

@st.cache_data(show_spinner=True)
def preprocess_candidate_party_31(df):
    city_party_cols = ["party_1", "party_2", "party_3", "party_4"]
    city_candidate_cols = ["choice_1", "choice_2", "choice_3", "choice_4"]

    rows = []

    for parties, candidates in zip(
        df[city_party_cols].to_numpy(),
        df[city_candidate_cols].to_numpy()
    ):
        counts = Counter(parties)

        if sorted(counts.values(), reverse=True) != [3, 1]:
            continue

        dominant_party = next(p for p, c in counts.items() if c == 3)
        minority_party = next(p for p, c in counts.items() if c == 1)

        for cand, party in zip(candidates, parties):
            if party == minority_party:
                rows.append({
                    "candidate": cand,
                    "minority_party": minority_party,
                    "dominant_party": dominant_party
                })

    return pd.DataFrame(rows)

candidate_party_31_df = preprocess_candidate_party_31(df)
df = preprocess_party_patterns(df)

tab1,tab2 = st.tabs(['Намын хослолын бүтэц', 'Сонгогдогч vs нам (1-3 бүлэг)'])
with tab1:
    pattern_dist = (
        df["party_combination_pattern"]
        .value_counts()
        .reset_index()
    )

    pattern_dist.columns = ["Намын хослолын бүтэц", "Саналын хуудасны тоо"]

    total_ballots = pattern_dist["Саналын хуудасны тоо"].sum()
    pattern_dist["Хувь (%)"] = (
        pattern_dist["Саналын хуудасны тоо"] / total_ballots * 100
    ).round(2)

    fig = px.bar(
        pattern_dist,
        x="Намын хослолын бүтэц",
        y="Саналын хуудасны тоо",
        text="Хувь (%)",
        title=(
            "<b>Хотын сонгууль: Намын хослолын хэв шинж</b><br>"
            "<sup>Нэг саналын хуудсан дахь 4 сонголтын бүтэц</sup>"
        ),
        template="plotly_white",
        color="Намын хослолын бүтэц",
    )

    fig.update_traces(
        texttemplate="%{text}%",
        textposition="outside",
        cliponaxis=False
    )

    fig.update_layout(
        showlegend=False,
        bargap=0.3,
        yaxis=dict(showgrid=True, gridcolor="#f0f0f0"),

    )

    st.plotly_chart(fig, use_container_width=True)

    # ======================================================
    # 3–1 DOMINANT PARTY ANALYSIS
    # ======================================================
    with st.expander("🔹 3–1 хослол: Нэг нам давамгайлсан холимог санал"):
        subset_31 = df[df["party_combination_pattern"] == "3-1"]

        dominance_df = (
            subset_31
            .value_counts(["dominant_party", "minority_party"])
            .reset_index(name="count")
            .sort_values("count", ascending=False)
        )

        dominance_df["percentage"] = (
            dominance_df["count"] / dominance_df["count"].sum() * 100
        ).round(2)

        dominance_df["pair_label"] = (
            "<b>" + dominance_df["dominant_party"] + "</b> → " + dominance_df["minority_party"]
        )

        fig = px.bar(
            dominance_df.head(10),
            x="count",
            y="pair_label",
            orientation="h",
            text="percentage",
            title="<b>3–1 Намын давамгайлал</b>",
            template="plotly_white",
            color="dominant_party",
            color_discrete_map=party_colors
        )

        fig.update_traces(
            texttemplate="%{text}%",
            textposition="outside",
            cliponaxis=False
        )

        fig.update_layout(
            showlegend=False,
            yaxis=dict(categoryorder="total ascending"),
        )

        st.plotly_chart(fig, use_container_width=True)
        st.metric("Нийт саналын хуудас", f"{len(subset_31):,}")

        st.markdown("""
        **3–1** гэдэг нь:
        - 3 нэр дэвшигч **нэг намынх**
        - 1 нэр дэвшигч **өөр намынх**
        """)

    # ======================================================
    # 2–2 BALANCED PARTY ANALYSIS
    # ======================================================
    with st.expander("🔹 2–2 хослол: 2 нам тэнцүү санал"):
        subset_22 = df[df["party_combination_pattern"] == "2-2"]

        subset_22["party_a"] = subset_22["pair_22"].str[0]
        subset_22["party_b"] = subset_22["pair_22"].str[1]

        dominance_df = (
            subset_22
            .value_counts(["party_a", "party_b"])
            .reset_index(name="count")
            .sort_values("count", ascending=False)
        )

        dominance_df["percentage"] = (
            dominance_df["count"] / dominance_df["count"].sum() * 100
        ).round(2)

        dominance_df["pair_label"] = (
            dominance_df["party_a"] + " = " + dominance_df["party_b"]
        )

        fig = px.bar(
            dominance_df.head(10),
            x="count",
            y="pair_label",
            orientation="h",
            text="percentage",
            title="<b>2 нам тэнцүү санал</b>",
            template="plotly_white",
            color="party_a",
            color_discrete_map=party_colors
        )

        fig.update_traces(
            texttemplate="%{text}%",
            textposition="outside",
            cliponaxis=False
        )

        fig.update_layout(
            showlegend=False,
            yaxis=dict(categoryorder="total ascending")
        )

        st.plotly_chart(fig, use_container_width=True)
        st.metric("Нийт саналын хуудас", f"{len(subset_22):,}")


    with st.expander("🔹 2–1–1 хослол: Нэг суурь нам + хоёр нэмэлт нам"):
        subset_211 = df[df["party_combination_pattern"] == "2-1-1"].copy()

        # Extract core and secondary parties (vector-safe)
        def extract_211(row):
            counts = Counter(row)
            core = next(p for p, c in counts.items() if c == 2)
            others = sorted(p for p, c in counts.items() if c == 1)
            return core, tuple(others)

        extracted = subset_211[city_party_cols].apply(
            lambda r: extract_211(r),
            axis=1
        )

        subset_211["core_party"] = extracted.str[0]
        subset_211["other_parties"] = extracted.str[1]

        dominance_df = (
            subset_211
            .value_counts(["core_party", "other_parties"])
            .reset_index(name="count")
            .sort_values("count", ascending=False)
        )

        dominance_df["percentage"] = (
            dominance_df["count"] / dominance_df["count"].sum() * 100
        ).round(2)


        dominance_df["pair_label"] = (
            "<b>" + dominance_df["core_party"] + "</b> → " + dominance_df["other_parties"].astype(str)
        )

        fig = px.bar(
            dominance_df.head(10),
            x="count",
            y="pair_label",
            orientation="h",
            text="percentage",
            title="<b>2–1–1: Нэг суурь намтай холимог санал</b>",
            template="plotly_white",
            color="core_party",
            color_discrete_map=party_colors
        )

        fig.update_traces(
            texttemplate="%{text}%",
            textposition="outside",
            cliponaxis=False
        )

        fig.update_layout(
            showlegend=False,
            yaxis=dict(categoryorder="total ascending")
        )

        st.plotly_chart(fig, use_container_width=True)

        st.metric("Нийт саналын хуудас", f"{len(subset_211):,}")

        st.markdown("""
        **2–1–1** гэдэг нь:
        - 2 нэр дэвшигч **нэг намынх**
        - 2 нэр дэвшигч **өөр өөр намуудаас**
        
        """)


    with st.expander("🔹 1–1–1–1 хослол: Бүрэн задгай сонголт"):
        subset_1111 = df[df["party_combination_pattern"] == "1-1-1-1"].copy()

        party_sets = (
            subset_1111[city_party_cols]
            .apply(lambda r: tuple(sorted(r)), axis=1)
        )

        dominance_df = (
            party_sets
            .value_counts()
            .reset_index(name="count")
            .rename(columns={"index": "party_set"})
            .sort_values("count", ascending=False)
        )

        dominance_df["percentage"] = (
            dominance_df["count"] / dominance_df["count"].sum() * 100
        ).round(2)

        dominance_df["pair_label"] = dominance_df["party_set"].astype(str)

        fig = px.bar(
            dominance_df.head(10),
            x="count",
            y="pair_label",
            orientation="h",
            text="percentage",
            title="<b>1–1–1–1: Бүрэн холимог санал</b>",
            template="plotly_white",
            color_discrete_map=party_colors

        )

        fig.update_traces(
            texttemplate="%{text}%",
            textposition="outside",
            cliponaxis=False
        )

        fig.update_layout(
            showlegend=False,
            yaxis=dict(categoryorder="total ascending")
        )

        st.plotly_chart(fig, use_container_width=True)

        st.metric("Нийт саналын хуудас", f"{len(subset_1111):,}")

        st.markdown("""
        **1–1–1–1** гэдэг нь:
        - 4 нэр дэвшигч **4 өөр намынх**

        """)

    with st.expander("4 хослол: Цэвэр намын санал – Нам тус бүрээр", expanded=False):

        # --------------------------------------------------
        # 1. Filter pure party ballots (4/4)
        # --------------------------------------------------
        df_4 = df[df["party_combination_pattern"] == "4"].copy()

        # Party receiving all 4 votes
        df_4["pure_party"] = df_4["party_1"]

        party_dist = (
            df_4["pure_party"]
            .value_counts()
            .reset_index()
        )

        party_dist.columns = ["Нам", "Саналын хуудасны тоо"]

        # Percent
        total_4 = party_dist["Саналын хуудасны тоо"].sum()
        party_dist["Хувь (%)"] = (
            party_dist["Саналын хуудасны тоо"] / total_4 * 100
        ).round(2)

        # --------------------------------------------------
        # 2. Plot
        # --------------------------------------------------
        fig = px.bar(
            party_dist,
            x="Саналын хуудасны тоо",
            y="Нам",
            orientation="h",
            text="Хувь (%)",
            title=(
                "<b>Цэвэр намын санал (4/4)</b><br>"
                "<sup>Нэг саналын хуудсан дээр 4 төлөөлөгчийг бүрэн авсан намууд</sup>"
            ),
            template="plotly_white",
            color="Нам",
            color_discrete_map=party_colors
        )

        fig.update_traces(
            texttemplate="%{text}%",
            textposition="outside",
            cliponaxis=False,
            marker_line_width=1,
            opacity=0.9
        )

        fig.update_layout(
            xaxis_title="<b>Саналын хуудасны тоо</b>",
            yaxis_title=None,
            showlegend=False,
            height=500,
            margin=dict(l=60, r=90, t=80, b=50),
            yaxis=dict(categoryorder="total ascending"),
            xaxis=dict(showgrid=True, gridcolor="#f0f0f0")
        )

        st.plotly_chart(fig, use_container_width=True)
        #st.dataframe(party_dist,hide_index = True, use_container_width=True)


    # ======================================================
    # FINAL INTERPRETATION
    # ======================================================
    st.markdown("""
    ## Шинжилгээ: Намын хослолын бүтэц (Хотын сонгууль)

    ### Гол дүгнэлт
    Хотын сонгууль дахь холимог санал нь санамсаргүй бус,  
    **тодорхой давамгайлал бүхий бүтэцтэй** байна.

    Сонгогчид ихэнхдээ:
    - нэг намыг “суурь” болгон,
    - бусад намуудаас хязгаарлагдмал сонголт хийж байна.
    """)
with tab2:
    top_candidates = (
    candidate_party_31_df
    .value_counts(["candidate", "minority_party",'dominant_party'])
    .reset_index(name="count")
    .sort_values("count", ascending=False)
    )

    top_candidates["percentage"] = (
        top_candidates["count"]
        / top_candidates["count"].sum() * 100
    ).round(2)



    top_candidates["label"] = ("<b>" + 
        top_candidates["candidate"].str.split().str[-1]
        + " ("
        + top_candidates["minority_party"] + ')' + '</b>' 
        + " → " +
        top_candidates["dominant_party"] 
    )
    #top_candidates

    fig = px.bar(
    top_candidates.head(15),
    x="count",
    y="label",
    orientation="h",
    text="percentage",
    title=(
        "<b>1–3 Хослол: Бусад намтай ганцаараа хамт сонгогдсон нэр дэвшигчид</b><br>"
        "<sup>Нэр дэвшигч → Нэмэлтээр сонгогдсон нам</sup>"
    ),
    template="plotly_white",
    color="minority_party",
    color_discrete_map=party_colors
    )

    fig.update_traces(
        texttemplate="%{text}%",
        textposition="outside",
        cliponaxis=False
    )

    fig.update_layout(
        xaxis_title="Саналын хуудасны тоо",
        yaxis_title=None,
        showlegend=True,
        yaxis=dict(categoryorder="total ascending"),
        height = 700

    )

    st.plotly_chart(fig, use_container_width=True)
