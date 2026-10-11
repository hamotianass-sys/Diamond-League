"""واجهة الدردشة: streamlit run app.py"""
import json
import os
import anthropic
import streamlit as st
from tools import FUNCTIONS, TOOL_SCHEMAS

MODEL = "claude-sonnet-5-5"
SYSTEM = (
    "أنت مساعد متخصص في بيانات دوري نقابات دايموند. "
    "أجب بالعربي وبشكل مختصر. استخدم الأدوات دائماً لجلب أي رقم أو ترتيب أو اسم، ولا تخمّن أبداً. "
    "إذا أعادت الأداة خطأ أو لم تكن النسخة متوفرة، قل ذلك بصراحة."
)

client = anthropic.Anthropic()  # يقرأ المفتاح من ANTHROPIC_API_KEY


def ask(history: list) -> str:
    """يرسل المحادثة لـ Claude وينفذ الأدوات المطلوبة حتى يصل للجواب النهائي."""
    messages = list(history)
    for _ in range(6):  # حد أقصى لدورات الأدوات
        resp = client.messages.create(
            model=MODEL, max_tokens=1000, system=SYSTEM,
            tools=TOOL_SCHEMAS, messages=messages,
        )
        if resp.stop_reason != "tool_use":
            return "".join(b.text for b in resp.content if b.type == "text")
        messages.append({"role": "assistant", "content": resp.content})
        results = []
        for b in resp.content:
            if b.type == "tool_use":
                out = FUNCTIONS[b.name](**b.input)
                results.append({"type": "tool_result", "tool_use_id": b.id,
                                "content": json.dumps(out, ensure_ascii=False)})
        messages.append({"role": "user", "content": results})
    return "تعذّر إكمال الطلب، حاول إعادة صياغة السؤال."


st.set_page_config(page_title="دوري دايموند", page_icon="💎")
st.markdown("<style>html{direction:rtl}</style>", unsafe_allow_html=True)
st.title("💎 مساعد دوري نقابات دايموند")

if "chat" not in st.session_state:
    st.session_state.chat = []

for m in st.session_state.chat:
    with st.chat_message(m["role"]):
        st.write(m["content"])

if q := st.chat_input("اسأل عن أي نسخة أو نقابة..."):
    st.session_state.chat.append({"role": "user", "content": q})
    with st.chat_message("user"):
        st.write(q)
    with st.chat_message("assistant"):
        with st.spinner("..."):
            answer = ask(st.session_state.chat)
        st.write(answer)
    st.session_state.chat.append({"role": "assistant", "content": answer})
