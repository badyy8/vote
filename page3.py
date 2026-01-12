import streamlit as st
import pandas as pd
import plotly.express as px
from data_loader import load_data,get_contestants_df
from itertools import combinations
from collections import Counter

@st.cache_data(show_spinner=True)
def get_df():
    df = load_data()
    return df

df = get_df()

district_candidate_df = get_contestants_df()
# ======================================================
# Нийтлэг бэлтгэл
# ======================================================
city_candidate_cols = ["choice_1", "choice_2", "choice_3", "choice_4"]

# Candidate → Party map
candidate_party_map = {}
for i in range(1, 5):
    for cand, party in zip(df[f"choice_{i}"], df[f"party_{i}"]):
        candidate_party_map[cand] = party

@st.cache_data(show_spinner=True)
def format_candidate(name):
    """Жишээ: 'БИШЭЭ ЭРДЭНЭСҮХ' → 'ЭРДЭНЭСҮХ (АН)'"""
    if pd.isna(name):
        return name
    last_name = name.split()[-1]
    party = candidate_party_map.get(name, "UNK")
    return f"{last_name} ({party})"

df['district_candidate_1_with_party'] = df.apply(lambda x: f"{x.district_candidate_1} [{x.district_party_1}]", axis=1)
df['district_candidate_2_with_party'] = df.apply(lambda x: f"{x.district_candidate_2} [{x.district_party_2}]", axis=1)

@st.cache_data(show_spinner=True)
def format_last_name(name):
    if pd.isna(name):
        return name
    return name.split()[-1]

df['district_candidate_1_with_party'] = (
    df['district_candidate_1'].apply(format_last_name)
    + " ["
    + df['district_party_1']
    + "]"
)

df['district_candidate_2_with_party'] = (
    df['district_candidate_2'].apply(format_last_name)
    + " ["
    + df['district_party_2']
    + "]"
)


# ======================================================
# Нэр дэвшигчдийн хамт сонгогдсон тооцоолол (1 удаа)
# ======================================================
pair_counter = Counter()

for _, row in df.iterrows():
    candidates = sorted(set(row[city_candidate_cols]))
    for a, b in combinations(candidates, 2):
        pair_counter[(a, b)] += 1

co_vote_df = pd.DataFrame(
    [(a, b, c) for (a, b), c in pair_counter.items()],
    columns=["candidate_a", "candidate_b", "count"]
).sort_values("count", ascending=False)

# ======================================================
# Табууд
# ======================================================
tab1, tab2,tab3 = st.tabs([
    "Хамт сонгогдсон нэр дэвшигчдийн хослол (Хотын сонгууль)",
    "Хамт сонгогдсон нэр дэвшигчдийн хослол (Дүүргийн сонгууль)",
    'Дүүргийн түвшний шинжилгээ'
])

# ======================================================
# TAB 1: Хамт сонгогдсон нэр дэвшигчдийн хослол
# ======================================================
with tab1:

    # 1. Prepare data
    top_n = 15
    top_pairs = co_vote_df.head(top_n).copy()

    top_pairs["pair_label"] = top_pairs.apply(
        lambda r: f"<b>{format_candidate(r['candidate_a'])}</b> + <b>{format_candidate(r['candidate_b'])}</b>",
        axis=1
    )

    # Calculate total for percentage labels (optional but helpful)
    total_mixed_votes = co_vote_df["count"].sum()

    # 2. Plotting
    fig = px.bar(
        top_pairs,
        x="count",
        y="pair_label",
        orientation="h",
        text="count", # Add the number on the bar
        title="<b>Хамт сонгогдсон хамгийн түгээмэл нэр дэвшигчдийн хослол</b><br><sup>Хотын сонгуулийн шилдэг 15 хослол</sup>",
        template="plotly_white",
        color="count",
        color_continuous_scale="Blues"
    )

    # 3. Clean up the look
    fig.update_traces(
        textposition='outside',
        cliponaxis=False,
        marker_line_color='rgb(8,48,107)',
        marker_line_width=1,
        opacity=0.9
    )

    fig.update_layout(
        xaxis_title="<b>Саналын хуудасны тоо</b>",
        yaxis_title=None, # Usually clear enough from context
        height=700, # Taller height to give 15 rows room to breathe
        showlegend=False,
        coloraxis_showscale=False,
        margin=dict(l=50, r=80, t=80, b=50), # Large right margin for labels
        # Force the highest count to the top
        yaxis=dict(categoryorder="total ascending"),
        xaxis=dict(showgrid=True, gridcolor='LightGray')
    )

    st.plotly_chart(fig, use_container_width=True)

    st.markdown("""

    ### Зорилго
    Энэхүү шинжилгээ нь хотын төлөөлөгчдийг сонгох үед **аль нэр дэвшигчид нэг саналын хуудас дээр хамгийн их хамт сонгогдож** байгааг тодорхойлох зорилготой.

    ---

    ### Аргачлал
    Саналын хуудас бүр дээр сонгогдсон дөрвөн нэр дэвшигчийн дунд үүсэх бүх боломжит хослолыг бүртгэж, тухайн хоёр нэр дэвшигч **хамт гарч ирсэн саналын хуудасны тоогоор** нэгтгэн тооцоолсон.

    ---

    ### Гол дүгнэлт
    - Хамт сонгогдсон хамгийн түгээмэл хослолууд нь **намаар бүлэглэн сонгох (slate voting)** зан төлөв давамгай байгааг харуулж байна.
    - Нэр дэвшигчдийн хамт сонгогдох хэв шинж тодорхой бүтэцтэй байна.


    """)

# ======================================================
# TAB 2: Зангуу нэр дэвшигчид
# ======================================================
# with tab2:
#     anchor_scores = Counter()

#     for _, row in co_vote_df.iterrows():
#         anchor_scores[row["candidate_a"]] += row["count"]
#         anchor_scores[row["candidate_b"]] += row["count"]

#     anchor_df = (
#         pd.DataFrame(anchor_scores.items(), columns=["candidate", "anchor_score"])
#         .sort_values("anchor_score", ascending=False)
#     )

#     anchor_df["candidate_label"] = anchor_df["candidate"].apply(format_candidate)
#     # 1. Prepare data
#     top_n = 15
#     top_anchor_df = anchor_df.head(top_n).copy()

#     # 2. Plotting
#     fig = px.bar(
#         top_anchor_df,
#         x="anchor_score",
#         y="candidate_label",
#         orientation="h",
#         text="anchor_score", # Show the score value on the bar
#         title="<b>Хотын сонгууль: Шилдэг 'Зангуу' нэр дэвшигчид</b><br><sup>Бусад нэр дэвшигчидтэй хамгийн их сонгогдсон байдал</sup>",
#         template="plotly_white",
#         color="anchor_score",
#         color_continuous_scale="Greens" # Different color (Green) to distinguish from the "Pairs" chart
#     )

#     # 3. Clean and Professional Styling
#     fig.update_traces(
#         textposition='outside',
#         cliponaxis=False,
#         marker_line_color='rgb(0,68,27)',
#         marker_line_width=1,
#         opacity=0.9
#     )

#     fig.update_layout(
#         xaxis_title="<b>Зангуу оноо (Хамт сонгогдсон нийт тоо)</b>",
#         yaxis_title=None, 
#         height=700, # Height adjusted for 15 candidates
#         showlegend=False,
#         coloraxis_showscale=False,
#         margin=dict(l=50, r=80, t=80, b=50),
#         # Largest score at the top
#         yaxis=dict(categoryorder="total ascending"),
#         xaxis=dict(showgrid=True, gridcolor='#f0f0f0')
#     )

#     # Add a note explaining what "Anchor Score" means
#     st.plotly_chart(fig, use_container_width=True)

#     st.info("""
#     **Тайлбар:** 'Зангуу оноо' нь тухайн нэр дэвшигч бусад нэр дэвшигчидтэй нийт хэдэн удаа 
#     хослож сонгогдсоныг илэрхийлнэ. Энэ нь тухайн нэр дэвшигч хэр их 'татагч' хүчтэй байгааг харуулна.
#     """)

#     st.markdown("""
# ## Шинжилгээ 6: Зангуу нэр дэвшигчид (Хотын сонгууль)

# ### Зорилго
# Энэхүү шинжилгээ нь хотын сонгууль дахь **зангуу нэр дэвшигчдийг** тодорхойлох зорилготой. Зангуу нэр дэвшигчид гэдэг нь бусад олон нэр дэвшигчтэй нэг саналын хуудас дээр **хамгийн олон удаа хамт сонгогдсон** хүмүүсийг хэлнэ.

# ---

# ### Аргачлал
# Нэр дэвшигч бүрийн хувьд бусад нэр дэвшигчидтэй хамт сонгогдсон нийт тоог нэгтгэн **зангуу оноо** болгон тооцоолсон.

# ---

# ### Гол дүгнэлт
# - Зангуу нэр дэвшигчид нь гол төлөв **томоохон намуудад төвлөрсөн** байна.
# - Цөөн тооны нэр дэвшигч өндөр зангуу оноо авч байгаа нь хотын сонгуулийн сонголт **“цөм–захын” бүтэцтэй** байгааг илтгэнэ.
# - Эдгээр нэр дэвшигчид нь сонгогчдын сонголтыг чиглүүлэгч гол цэгүүд болж байна.

# ---

# ### Энэ яагаад чухал вэ?
# Зангуу нэр дэвшигчдийг тодорхойлох нь:
# - Нам доторх албан бус манлайллыг илрүүлэх
# - Яагаад тодорхой хослолууд давамгайлж байгааг тайлбарлах
# - Хотын түвшний намын сахилга батыг хувь хүний түвшинд ойлгох
# боломж олгодог.

# ---

# ### Дараагийн хэсэг
# Дараагийн шинжилгээгээр сонгогчид хот болон дүүргийн сонгуулийн хооронд намын сонголтоо хэр тууштай хадгалж байгааг (cross-contest alignment) авч үзнэ.
# """)


with tab2:

    # --------------------------------------------------
    # 1. Count district candidate pairs
    # --------------------------------------------------
    pair_counter = Counter()

    for _, row in df.iterrows():
        a = row["district_candidate_1_with_party"]
        b = row["district_candidate_2_with_party"]

        pair = tuple(sorted([a, b]))  # (A,B) == (B,A)
        pair_counter[pair] += 1

    district_pair_df = (
        pd.DataFrame(
            [(a, b, c) for (a, b), c in pair_counter.items()],
            columns=["candidate_a", "candidate_b", "count"]
        )
        .sort_values("count", ascending=False)
    )

    # --------------------------------------------------
    # 2. Prepare top pairs
    # --------------------------------------------------
    top_n = 15
    top_pairs = district_pair_df.head(top_n).copy()

    # ✅ THIS WAS MISSING
    top_pairs["pair_label"] = (
        top_pairs["candidate_a"]
        + " + "
        + top_pairs["candidate_b"]
    )

    # --------------------------------------------------
    # 3. Plot (STYLE MATCHES CITY)
    # --------------------------------------------------
    fig = px.bar(
        top_pairs,
        x="count",
        y="pair_label",
        orientation="h",
        text="count",
        title=(
            "<b>Хамт сонгогдсон хамгийн түгээмэл нэр дэвшигчдийн хослол</b><br>"
            "<sup>Дүүргийн сонгуулийн шилдэг 15 хослол</sup>"
        ),
        template="plotly_white",
        color="count",
        color_continuous_scale="Greens"
    )

    fig.update_traces(
        textposition="outside",
        cliponaxis=False,
        marker_line_color="rgb(8,48,107)",
        marker_line_width=1,
        opacity=0.9
    )

    fig.update_layout(
        xaxis_title="<b>Саналын хуудасны тоо</b>",
        yaxis_title=None,
        height=700,
        showlegend=False,
        coloraxis_showscale=False,
        margin=dict(l=50, r=80, t=80, b=50),
        yaxis=dict(categoryorder="total ascending"),
        xaxis=dict(showgrid=True, gridcolor="#f0f0f0")
    )

    st.plotly_chart(fig, use_container_width=True)

    # --------------------------------------------------
    # 4. Explanation
    # --------------------------------------------------
    st.markdown("""
        ### Тайлбар
        Энэхүү график нь дүүргийн сонгуульд **ямар хоёр нэр дэвшигч**
        нэг саналын хуудсанд **хамгийн олон удаа хамт сонгогдсоныг**
        харуулж байна.

        Дүүргийн сонгуульд сонгогч бүр **яг 2 нэр дэвшигч** сонгодог тул
        энд илэрч буй хослолууд нь сонгогчдын
        **шууд бөгөөд зориудын хамтын сонголтыг**
        хамгийн цэвэр хэлбэрээр илэрхийлнэ.
        """)

with tab3:
    st.title("Дүүргийн түвшний шинжилгээ")

    st.markdown("""
    Энэхүү хэсэгт **тойргийг сонгож**, тухайн тойрогт
    хамтдаа сонгогдсон **хоёр нэр дэвшигчийн** тоог харьцуулах
    боломжтой.
    """)
  
    # ======================================================
    # 1. Дүүрэг сонгох input
    # ======================================================
    available_districts = (
        df["district_no"]
        .dropna()
        .astype(int)
        .sort_values()
        .unique()
    )

    selected_district = st.selectbox(
        "Дүүрэг сонгох",
        available_districts
    )

    # ======================================================
    # 2. Сонгосон дүүргийн өгөгдөл
    # ======================================================
    district_df = df[df["district_no"] == selected_district]

    # ======================================================
    # 3. Нэр дэвшигчдийн хослолын давтамж
    # ======================================================
    pair_counts = (
        district_df
        .groupby("district_no")[["district_candidate_1_with_party", "district_candidate_2_with_party"]]
        .value_counts()
        .reset_index(name="Саналын хуудасны тоо")
    )

    # Зөвхөн сонгосон дүүргийг авах
    pair_counts = pair_counts[pair_counts["district_no"] == selected_district]

    # Нэрийг нэг мөр болгох (visual-д зориулж)
    pair_counts["Нэр дэвшигчдийн хослол"] = (
        pair_counts["district_candidate_1_with_party"]
        + " + "
        + pair_counts["district_candidate_2_with_party"]
    )

    # 1. Prepare formatting for the labels (if not already done)
    # Assuming 'pair_counts' has 'candidate_a' and 'candidate_b' columns
    pair_counts["Нэр дэвшигчдийн хослол"] = pair_counts.apply(
        lambda r: f"<b>{r['district_candidate_1_with_party']}</b> + <b>{r['district_candidate_2_with_party']}</b>", 
        axis=1
    )

    # 2. Plotting
    fig = px.bar(
        pair_counts,
        x="Саналын хуудасны тоо",
        y="Нэр дэвшигчдийн хослол",
        orientation="h",
        text="Саналын хуудасны тоо",
        title=f"<b>{selected_district}-Тойрог: Хамт сонгогдсон нэр дэвшигчдийн хослол</b><br><sup>Дүүргийн түвшний нэр дэвшигчдийн хамтын сонголт</sup>",
        template="plotly_white",
        color="Саналын хуудасны тоо",
        color_continuous_scale="Purp" # New color for District-specific pair analysis
    )

    # 3. Refine Traces and Layout
    fig.update_traces(
        textposition='outside',
        cliponaxis=False,
        marker_line_color='#4a148c', # Dark purple border
        marker_line_width=1,
        opacity=0.85
    )

    fig.update_layout(
        xaxis_title="<b>Саналын хуудасны тоо</b>",
        yaxis_title=None,
        height=min(400 + (len(pair_counts) * 30), 800), # Dynamic height based on number of pairs
        showlegend=False,
        coloraxis_showscale=False,
        margin=dict(l=50, r=80, t=90, b=50),
        yaxis=dict(
            categoryorder="total ascending",
            automargin=True
        ),
        xaxis=dict(showgrid=True, gridcolor='#f0f0f0')
    )

    st.plotly_chart(fig, use_container_width=True)

    # ======================================================
    # 5. Тайлал
    # ======================================================
    st.markdown(f"""
    ## Тайлбар ({selected_district}-р тойрог)

    - Дээрх график нь **{selected_district}-р тойрогт** сонгогчид
    **ямар хоёр нэр дэвшигчийг хамгийн олон удаа хамтад нь сонгосон**
    болохыг харуулж байна.
   
    """)