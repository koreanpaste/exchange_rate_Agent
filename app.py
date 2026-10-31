from dotenv import load_dotenv
load_dotenv()

import streamlit as st
from langchain.agents import create_agent
from langchain.chat_models import init_chat_model
from tools import get_exchange_rate

st.set_page_config(page_title="환율 조회", page_icon="💱", layout="centered")

SYSTEM_PROMPT = (
    "너는 환율 조회 전문 어시스턴트야. 환율과 관련된 질문에만 답해. "
    "사용자가 나라 이름(미국, 일본 등)이나 통화 이름(달러, 엔 등)만 말해도 "
    "해당 통화 코드(USD, JPY 등)로 바꿔서 get_exchange_rate 도구로 조회해. "
    "기준 통화를 말하지 않으면 그 통화 1단위가 원화(KRW)로 얼마인지 알려줘. "
    "엔화는 100엔 기준 값도 함께 알려줘. "
    "금액이 있으면(예: 100달러) 조회한 환율에 곱해서 계산해. "
    "항상 도구로 조회한 값만 사용하고 추측하지 마. "
    "답변은 한국어로 짧고 읽기 쉽게, 환율은 소수점 둘째 자리까지 쓰고 기준일도 알려줘. "
    "환율과 관련 없는 질문에는 '환율 관련 질문만 답변할 수 있어요.'라고만 말해."
)

@st.cache_resource
def load_agent():
    model = init_chat_model("gpt-5.4-mini")
    return create_agent(model, tools=[get_exchange_rate], system_prompt=SYSTEM_PROMPT)

agent = load_agent()

AVATARS = {"user": "🙂", "assistant": "💱"}

if "messages" not in st.session_state:
    st.session_state.messages = []

# ---------- 사이드바 ----------
clicked = None
with st.sidebar:
    st.header("💱 환율 조회")
    st.caption("나라나 통화 이름만 말해도 원화(KRW) 기준으로 알려줘요.")
    st.markdown("**이렇게 물어보세요**")
    for ex in ["미국", "일본", "유로", "100달러는 얼마야?"]:
        if st.button(ex, use_container_width=True):
            clicked = ex
    st.divider()
    if st.button("🗑️ 대화 지우기", use_container_width=True):
        st.session_state.messages = []
        st.rerun()
    st.caption("하루 한 번 갱신되는 기준 환율이에요. (출처: Frankfurter)")

# ---------- 본문 ----------
st.title("💱 환율 조회 서비스")

prompt = st.chat_input("예: 미국, 일본, 100유로는 얼마?") or clicked

if not st.session_state.messages and not prompt:
    st.info("👋 나라나 통화 이름을 입력해보세요. 예: **미국**, **일본**, **100유로는 얼마야?**")

for m in st.session_state.messages:
    with st.chat_message(m["role"], avatar=AVATARS[m["role"]]):
        st.markdown(m["content"])

if prompt:
    with st.chat_message("user", avatar=AVATARS["user"]):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("assistant", avatar=AVATARS["assistant"]):
        with st.spinner("환율 조회 중..."):
            try:
                response = agent.invoke({"messages": st.session_state.messages})
                answer = response["messages"][-1].content
            except Exception as e:
                answer = f"⚠️ 오류가 발생했어요: {e}"
        st.markdown(answer)
    st.session_state.messages.append({"role": "assistant", "content": answer})