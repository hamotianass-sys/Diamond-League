"""نسخة مجانية بدون API: streamlit run app_free.py"""
import pandas as pd
import streamlit as st
from tools import DF, get_winner, get_ranking, guild_total_points, guild_history, top_guilds_by_points

st.set_page_config(page_title="دوري دايموند", page_icon="💎")
st.markdown("<style>html{direction:rtl}</style>", unsafe_allow_html=True)
st.title("💎 دوري نقابات دايموند")

seasons = sorted(int(s) for s in DF.season.unique())
guilds = sorted(DF.groupby("key").guild.first().tolist())

t1, t2, t3, t4, t5 = st.tabs(["🏆 الفائز", "📊 ترتيب نسخة", "🔢 نقاط نقابة", "📜 تاريخ نقابة", "🥇 الأفضل"])

with t1:
    s = st.selectbox("اختر النسخة", seasons, key="w")
    r = get_winner(s)
    st.success(f"بطل النسخة {s}: {r['winner']} ({r['points']} نقطة)")

with t2:
    s = st.selectbox("اختر النسخة", seasons, key="r")
    d = pd.DataFrame(get_ranking(s)["ranking"]).rename(columns={"rank": "المركز", "guild": "النقابة", "points": "النقاط"})
    st.dataframe(d, hide_index=True, use_container_width=True)

with t3:
    g = st.selectbox("اختر النقابة", guilds, key="g1")
    r = guild_total_points(g)
    st.metric("مجموع النقاط", r["total_points"])
    st.write(f"شاركت في {r['seasons_played']} نسخة: {r['seasons']}")

with t4:
    g = st.selectbox("اختر النقابة", guilds, key="g2")
    r = guild_history(g)
    st.write(f"عدد مرات الفوز: {r['wins']}")
    d = pd.DataFrame(r["history"]).rename(columns={"season": "النسخة", "rank": "المركز", "points": "النقاط"})
    st.dataframe(d, hide_index=True, use_container_width=True)

with t5:
    n = st.slider("عدد النقابات", 3, 15, 5)
    d = pd.DataFrame(top_guilds_by_points(n)["top"]).rename(columns={"guild": "النقابة", "total": "مجموع النقاط", "seasons": "عدد النسخ"})
    st.dataframe(d, hide_index=True, use_container_width=True)
