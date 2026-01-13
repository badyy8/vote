import streamlit as st
import pandas as pd
import plotly.express as px
from data_loader import load_data

df = load_data()

# ======================================================
# Хот – Дүүргийн намын уялдаа холбоо
# ======================================================
tab1,tab2 = st.tabs(['Хот – Дүүргийн намын уялдаа холбоо', 'Нэг намд 6/6 санал өгсөн сонгогчид'])

with tab1:
    city_party_cols = ["party_1", "party_2", "party_3", "party_4"]

    # Дүүргийн намыг эхний нэр дэвшигчийн намаар тодорхойлох
    district_party = df["district_party_1"]

    # Хотын сонголт дүүргийн намтай давхцаж байгаа эсэх
    city_district_alignment = df[city_party_cols].eq(
        district_party, axis=0
    ).any(axis=1)

    # Нэгтгэсэн үзүүлэлт
    alignment_dist = (
        city_district_alignment
        .value_counts()
        .rename(index={True: "Уялдсан", False: "Уялдаагүй"})
        .reset_index()
    )

    alignment_dist.columns = [
        "Хот–Дүүргийн намын уялдаа",
        "Саналын хуудасны тоо"
    ]

    # Calculate total for percentage labels
    total_alignment = alignment_dist["Саналын хуудасны тоо"].sum()
    max_alignment = alignment_dist["Саналын хуудасны тоо"].max()
    alignment_dist["Хувь (%)"] = (
        alignment_dist["Саналын хуудасны тоо"] / total_alignment  * 100
    )

    fig = px.bar(
        alignment_dist,
        x="Хот–Дүүргийн намын уялдаа",
        y="Саналын хуудасны тоо",
        text="Саналын хуудасны тоо",
        custom_data=["Хувь (%)"],
        title="<b>Хот - Дүүргийн намын уялдаа холбоо</b><br><sup>Дүүрэгт сонгосон нам нь Хотын сонголтод багтсан эсэх</sup>",
        template="plotly_white",
        color="Хот–Дүүргийн намын уялдаа",
        color_discrete_map={
            "Уялдсан": "#27ae60",   # Green for Alignment (Positive)
            "Уялдаагүй": "#e74c3c" # Red for No Alignment (Negative)
        }
    )

    fig.update_traces(
        # Show both count and percentage
        texttemplate='<b>%{text}</b><br>%{customdata:.1f}%',
        #customdata=(alignment_dist["Саналын хуудасны тоо"] / total_alignment * 100),
        textposition='outside',
        cliponaxis=False,
        marker_line_width=1.5,
        marker_line_color="black",
        opacity=0.85
    )

    fig.update_layout(
        xaxis_title="<b>Уялдааны төлөв</b>",
        yaxis_title="<b>Саналын хуудасны тоо</b>",
        bargap=0.4,
        showlegend=False,
        margin=dict(t=90, b=50, l=50, r=50),
        # Add headroom for labels
        yaxis=dict(range=[0, max_alignment * 1.25], showgrid=True, gridcolor='#f0f0f0'),
        font=dict(family="Arial", size=14)
    )

    st.subheader('Сонгууль хоорондын намын уялдаа холбоо (Хот <-> Дүүрэг)')
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("""

        ### Зорилго
        Энэхүү шинжилгээ нь сонгогчид нийслэл болон дүүргийн **сонгуулийн хооронд намын сонголтдоо хэр тууштай байгааг** судална. 

        Өөрөөр хэлбэл:
        > *Сонгогчид хотын сонгуульд дэмжсэн намаа дүүргийн сонгуульд үргэлжлүүлэн дэмжиж байна уу?*

        ---

        ### Аргачлал
        Саналын хуудас бүрд:
        - **Дүүргийн нам**-ыг дүүргийн эхний нэр дэвшигчийн намаар (`district_party_1`) тодорхойлов.
        - Хэрэв хотын сонгуульд сонгосон дөрвөн нэр дэвшигчийн **дор хаяж нэг нь** дүүргийн сонголттой ижил намынх байвал тухайн саналын хуудсыг **"Уялдсан"** гэж үзнэ.
        - Бусад тохиолдолд **"Уялдаагүй"** гэж үзнэ.

        ---

        ### Үр дүн

        | Уялдааны төлөв | Саналын хуудасны эзлэх хувь (%) |
        |----------------|--------------------------------:|
        | Уялдсан | **85.81%** |
        | Уялдаагүй | 14.19% |

        ---

        ### Тайлбар
        Үр дүнгээс харахад **сонгууль хоорондын намын сонголт маш өндөр уялдаатай** байна:

        - **Саналын хуудасны 85-аас илүү хувь** нь хот болон дүүргийн намын сонголт хоорондоо таарч байгаа нь сонгогчид намын чиг баримжаагаа сонгуулийн төрөл харгалзахгүй **тууштай хадгалж** байгааг харуулж байна.
        - Зөвхөн **14.19%** тохиолдолд хот болон дүүргийн сонголтын хооронд намын зөрүү ажиглагдсан нь өөр өөр намыг хольж сонгох үзэгдэл харьцангуй ховор байгааг илтгэнэ.

        ---

        ### Гол дүгнэлт
        Хотын сонгуульд нэр дэвшигчдийг хольж сонгох тохиолдол ажиглагддаг ч сонгогчид **сонгууль хооронд өндөр тууштай байдал** үзүүлж байна. 
        Дүүргийн төлөөлөгчөө сонгохдоо ихэнх сонгогчид хотын сонгуулиар аль хэдийн дэмжсэн намынхаа хүнийг сонгож байна.

        ---

        """)

with tab2:
    # ======================================================
    # TAB: Нэг намд 7/7 санал өгсөн сонгогчид
    # ======================================================

    city_party_cols = ["party_1", "party_2", "party_3", "party_4"]

    # 1. Хотын сонгууль: зөвхөн 1 нам
    df["city_single_party"] = df[city_party_cols].nunique(axis=1) == 1

    # 2. Дүүргийн сонгууль: зөвхөн 1 нам (аль хэдийн 2 хүн)
    df["district_single_party"] = df["district_party_1"] == df["district_party_2"]

    # 3. Хот + Дүүрэг ижил нам
    df["same_party_city_district"] = (
        df[city_party_cols[0]] == df["district_party_1"]
    )

    # 4. БҮРЭН НАМЫН ТУУШТАЙ СОНГОЛТ (7/7)
    df["seven_of_seven_same_party"] = (
        df["city_single_party"]
        & df["district_single_party"]
        & df["same_party_city_district"]
    )

    # --------------------------------------------------
    # Aggregate
    # --------------------------------------------------
    loyalty_dist = (
        df["seven_of_seven_same_party"]
        .value_counts()
        .rename(index={True: "7/7 Нэг нам", False: "Бусад"})
        .reset_index()
    )

    loyalty_dist.columns = ["Саналын хэв шинж", "Саналын хуудасны тоо"]
    

    total_votes = loyalty_dist["Саналын хуудасны тоо"].sum()
    max_votes = loyalty_dist["Саналын хуудасны тоо"].max()

    loyalty_dist["Хувь (%)"] = (
        loyalty_dist["Саналын хуудасны тоо"] / total_votes * 100
    )


    # --------------------------------------------------
    # Plot
    # --------------------------------------------------
    fig = px.bar(
        loyalty_dist,
        x="Саналын хэв шинж",
        y="Саналын хуудасны тоо",
        text="Саналын хуудасны тоо",
        custom_data=["Хувь (%)"],
        title=(
            "<b>Нэг намд 6/6 санал өгсөн сонгогчид</b><br>"
            "<sup>Хот (4) + Дүүрэг (2) = Бүрэн намын тууштай байдал</sup>"
        ),
        template="plotly_white",
        color="Саналын хэв шинж",
        color_discrete_map={
            "6/6 Нэг нам": "#2ecc71",
            "Бусад": "#e74c3c"
        }
    )

    fig.update_traces(
        texttemplate="<b>%{text}</b><br>%{customdata:.1f}%",
        textposition="outside",
        cliponaxis=False,
        marker_line_width=1.5,
        marker_line_color="black",
        opacity=0.9
    )

    fig.update_layout(
        xaxis_title=None,
        yaxis_title="<b>Саналын хуудасны тоо</b>",
        bargap=0.4,
        showlegend=False,
        margin=dict(t=90, b=50, l=50, r=50),
        yaxis=dict(
            range=[0, max_votes * 1.25],
            showgrid=True,
            gridcolor="#f0f0f0"
        )
    )

    st.subheader("Бүрэн намын тууштай байдал (6/6)")
    st.plotly_chart(fig, use_container_width=True)


    # ======================================================
    # Donut chart: Party share among 6/6 loyal voters
    # ======================================================

    # Filter only fully loyal ballots
    loyal_df = df[df["seven_of_seven_same_party"]].copy()

    # Party distribution (party_1 is enough — all are same)
    party_dist = (
        loyal_df["party_1"]
        .value_counts()
        .reset_index()
    )

    party_dist.columns = ["Нам", "Саналын хуудасны тоо"]

    # Calculate percentage
    party_dist["Хувь (%)"] = (
        party_dist["Саналын хуудасны тоо"]
        / party_dist["Саналын хуудасны тоо"].sum()
        * 100
    ).round(2)

    # Donut plot
    fig_donut = px.pie(
        party_dist,
        names="Нам",
        values="Саналын хуудасны тоо",
        hole=0.5,
        title=(
            "<b>6/6 Нэг намд өгсөн саналын намын хуваарилалт</b><br>"
            "<sup>Бүрэн намын тууштай сонгогчид</sup>"
        ),
        color_discrete_sequence=px.colors.qualitative.Set2
    )

    fig_donut.update_traces(
        textinfo="percent+label",
        pull=[0.03] * len(party_dist),
        marker=dict(line=dict(color="white", width=2))
    )

    fig_donut.update_layout(
        showlegend=True,
        legend_title_text="Нам",
        margin=dict(t=90, b=40, l=40, r=40)
    )

    st.subheader("6/6 Намын тууштай санал: Намын эзлэх хувь")
    st.plotly_chart(fig_donut, use_container_width=True)