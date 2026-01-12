import streamlit as st
import pandas as pd
import plotly.express as px
from data_loader import load_data

df = load_data()

# ===== Табууд =====
tab1, tab2 = st.tabs([
    "Хот – Намын тууштай сонголт",
    "Дүүрэг – Намын тууштай сонголт",
])

# ======================================================
# TAB 1: Хотын түвшний намын тууштай сонголт
# ======================================================
with tab1:

    st.markdown("### Сонгогчдын хотын түвшний намын тууштай сонголт")

    city_party_cols = ["party_1", "party_2", "party_3", "party_4"]

    # 1. Саналын хуудас бүр дэх давхардаагүй намын тоо
    city_unique_parties = df[city_party_cols].nunique(axis=1)

    # 2. Нэгтгэсэн тоон үзүүлэлт
    city_party_dist = (
        city_unique_parties
        .value_counts()
        .sort_index()
        .reset_index()
    )

    city_party_dist.columns = [
        "Сонгосон намын тоо",
        "Саналын хуудасны тоо"
    ]

    # Calculate total for percentages
    total_votes = city_party_dist["Саналын хуудасны тоо"].sum()
    max_val = city_party_dist["Саналын хуудасны тоо"].max()

    fig = px.bar(
        city_party_dist,
        x="Сонгосон намын тоо",
        y="Саналын хуудасны тоо",
        text="Саналын хуудасны тоо",
        title="<b>Хотын сонгууль: Нэг саналын хуудас дахь намын холимог сонголт</b><br><sup>Сонгогчид 4 хүртэлх нам сонгох боломжтой</sup>",
        template="plotly_white"
    )

    # 1. Style the bars and labels
    fig.update_traces(
        # Show both count and percentage
        texttemplate='<b>%{text}</b><br>%{customdata:.1f}%',
        customdata=(city_party_dist["Саналын хуудасны тоо"] / total_votes * 100),
        textposition='outside',
        cliponaxis=False,
        # Professional Solid Color (Steel Blue)
        marker_color='#1f77b4', 
        marker_line_color='#0a3d62',
        marker_line_width=1,
        opacity=0.85
    )

    # 2. Clean Layout (No color bar, better spacing)
    fig.update_layout(
        xaxis_title="<b>Сонгосон намын тоо</b>",
        yaxis_title="<b>Саналын хуудасны тоо</b>",
        bargap=0.4, # Slightly wider gap for a cleaner look
        margin=dict(t=90, b=50, l=70, r=50),
        # Headroom for text labels
        yaxis=dict(
            range=[0, max_val * 1.25], 
            showgrid=True, 
            gridcolor='#eeeeee',
            zeroline=True,
            zerolinecolor='black'
        ),
        xaxis=dict(tickmode="linear", dtick=1),
        font=dict(family="Arial", size=14, color="#2c3e50"),
        height=550 # Fixed height for better control in Streamlit
    )

    st.plotly_chart(fig, use_container_width=True)

    st.markdown("""
    ## Шинжилгээ 1: Хотын түвшний намын тууштай сонголт

    ### Зорилго
    Энэхүү шинжилгээ нь хотын төлөөлөгчдийг сонгох явцад сонгогчид **намын тууштай сонголтыг баримталж**, нэг намын нэр дэвшигчдийг тууштай сонгож байна уу, эсвэл **өөр өөр намуудын нэр дэвшигчдийг хольж** сонгож байна уу гэдгийг тодорхойлох зорилготой.

    ---

    ### Аргачлал
    Саналын хуудас бүрд хотын сонгуульд сонгогдсон дөрвөн нэр дэвшигчийн дунд хэдэн **давхардаагүй улс төрийн нам** байгааг тооцоолсон.

    Үзүүлэлт нь **1-ээс 4** хүртэлх утгатай байна:

    - **1 нам:** Сонгогч бүх төлөөлөгчөө нэг намын хүрээнд сонгосон.
    - **2–4 нам:** Сонгогч өөр өөр намуудын нэр дэвшигчдийг хольж сонгосон.

    ---

    ### Үр дүн

    | Сонгосон намын тоо | Саналын хуудасны эзлэх хувь (%) |
    |------------------:|--------------------------------:|
    | 1 нам | **68.76%** |
    | 2 нам | 15.96% |
    | 3 нам | 9.52% |
    | 4 нам | 5.77% |

    ---

    ### Тайлбар
    Үр дүнгээс харахад хотын сонгуульд **намын тууштай сонголт харьцангуй өндөр** байна:

    - **Арван сонгогч тутмын долоо орчим нь (68.76%)** дөрвөн төлөөлөгчөө бүгдийг нь **нэг намаас** сонгосон байна.
    - 2–4 намтай саналын хувь багасч байгаа нь **хэт задгай сонголт харьцангуй бага** байгааг илтгэнэ.

    ---

    ### Гол дүгнэлт
    Хотын төлөөлөгчдийг сонгох сонгогчдын зан төлөв **гол төлөв намаар тодорхойлогдож** байгаа ч нэг хэвийн биш байна. 
    """)

# ======================================================
# TAB 2: Дүүргийн түвшний намын тууштай сонголт
# ======================================================
with tab2:

    st.markdown("### Сонгогчдын дүүргийн түвшний намын тууштай сонголт")

    # 1. Дүүргийн намын тууштай сонголт
    district_party_discipline = (
        df["district_party_1"] == df["district_party_2"]
    )

    # 2. Нэгтгэсэн тоон үзүүлэлт
    district_discipline_dist = (
        district_party_discipline
        .value_counts()
        .rename(index={True: "Нэг нам", False: "Холимог намууд"})
        .reset_index()
    )

    district_discipline_dist.columns = [
        "Дүүргийн сонголтын хэв шинж",
        "Саналын хуудасны тоо"
    ]

    # Calculate percentages for the donut chart
    district_discipline_dist['Percentage'] = (
        district_discipline_dist["Саналын хуудасны тоо"] /
        district_discipline_dist["Саналын хуудасны тоо"].sum() * 100
    ).round(1)

    fig = px.pie(
        district_discipline_dist,
        names="Дүүргийн сонголтын хэв шинж",
        values="Саналын хуудасны тоо",
        title="<b>Дүүргийн сонгууль: Намын тууштай сонголт</b><br><sup>Сонгогчид нэг нам сонгосон эсвэл олон нам хольж сонгосон дүн</sup>",
        hole=0.5,
        template="plotly_white",
        color="Дүүргийн сонголтын хэв шинж",
        color_discrete_map={
            'Нэг нам': '#1f77b4',
            'Холимог намууд': '#ff7f0e'
        }
    )

    # 4. Update Traces - Fixed the connector syntax
    fig.update_traces(
        textinfo='percent+label', 
        textposition='outside',
        # Plotly uses 'pull' or simple textposition for connectors
        # Removing the explicit 'connector' dict fixes the common 'Invalid property' error
        hovertemplate="<b>%{label}</b><br>Тоо: %{value}<br>Хувь: %{percent}<extra></extra>",
        marker=dict(line=dict(color='#ffffff', width=2))
    )

    # 5. Update Layout
    # We calculate total separately to avoid errors inside the dict
    total_val = district_discipline_dist['Саналын хуудасны тоо'].sum()

    fig.update_layout(
        font=dict(family="Arial", size=14, color="#2c3e50"),
        height=550, 
        margin=dict(t=100, b=80, l=80, r=80), 
        showlegend=False, 
        annotations=[
            dict(
                text=f"<b>Нийт<br>{total_val:,}</b>",
                x=0.5, y=0.5, 
                font=dict(size=22, color='#2c3e50'), # Fixed font structure
                showarrow=False,
                align='center'
            )
        ]
    )


    st.plotly_chart(fig, use_container_width=True)

    st.markdown("""
    ## Шинжилгээ 2: Дүүргийн түвшний намын тууштай сонголт

    ### Зорилго
    Энэхүү шинжилгээ нь дүүргийн төлөөлөгчдийг сонгох явцад сонгогчид **намын чиг баримжаатай сонголтыг хэр зэрэг** хийж байгааг тодорхойлох зорилготой.

    ---

    ### Аргачлал
    Саналын хуудас бүрийн хувьд дүүргийн сонгуульд сонгогдсон хоёр нэр дэвшигчийн намыг харьцуулсан:

    - **Нэг нам:** Хоёр нэр дэвшигч хоёулаа нэг намынх
    - **Холимог намууд:** Хоёр нэр дэвшигч өөр өөр намынх

    ---

    ### Үр дүн

    | Дүүргийн сонголтын хэв шинж | Саналын хуудасны эзлэх хувь (%) |
    |---------------------------|--------------------------------:|
    | Нэг нам | **76.52%** |
    | Холимог намууд | 23.48% |

    ---

    ### Тайлбар
    - Сонгогчдын олонх нь (76.52%) дүүргийн хоёр төлөөлөгчөө хоёуланг нь нэг намаас сонгосон нь **дүүргийн түвшинд намын тууштай сонголт маш хүчтэй** байгааг илтгэнэ.
    - Дүүргийн түвшинд намуудыг хольж сонгох үзэгдэл нь хотын түвшний сонголттой харьцуулахад **мэдэгдэхүйц бага** байна.

    ---

    ### Гол дүгнэлт
    Намын чиг баримжаатай сонголт нь хотын сонгуулиас илүү **дүүргийн сонгуульд илүү хүчтэй** илэрч байна. Энэ нь сонгогчид дүүргийн түвшний төлөөллийг намын харьяалалтай илүү нягт холбож үзэж байгааг харуулж байна.

    """)
