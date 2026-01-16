######-------------페이지 구현---------############

import streamlit as st


st.set_page_config(
    page_title="PIKL",
    page_icon="🥒"
)

st.set_page_config(page_title="설문", page_icon="📝", layout="centered")

st.markdown("""
<style>
/* 상단 Streamlit 헤더 숨김 */
header {visibility: hidden; height: 0px;}

/* 우측 상단 햄버거 메뉴(Deploy/Settings 등) 숨김 */
#MainMenu {visibility: hidden;}

/* 하단 "Made with Streamlit" 같은 푸터 숨김 */
footer {visibility: hidden;}

/* 상단 여백 줄이기 (선택) */
.block-container {padding-top: 1rem;}
</style>
""", unsafe_allow_html=True)


GOOGLE_FORM_URL = "https://forms.gle/43bhQMmmKLGZjswH9"

st.set_page_config(
    page_title="PIKL",
    page_icon="",
    layout="centered",
)

st.title("✨PIKL 사전 예약 이벤트✨")
st.write("""
        건강한 토론장이 되는 사회 공유 서비스
        """)


st.markdown(
    """
- ✅ 우리학교, 우리 학과에서 가장 뜨거운 이슈를 확인해요!
- ✅ 민감한 주제에 대해서도 건강하게 의견을 나눠요!
- ✅ 의견을 공유할 때마다 무럭무럭 자라나는 피클!
"""
)



imgs = [f"PIKL_{i}.png" for i in range(1, 5)]

# 첫 줄
col1, col2 = st.columns(2, gap="small")
with col1:
    st.image(imgs[0], use_column_width=True)
with col2:
    st.image(imgs[1], use_column_width=True)

# 두 번째 줄
col3, col4 = st.columns(2, gap="small")
with col3:
    st.image(imgs[2], use_column_width=True)
with col4:
    st.image(imgs[3], use_column_width=True)

st.divider()


# 버튼을 누르면 새 탭으로 링크 열리는 '링크 버튼'
#st.link_button("시작하기",GOOGLE_FORM_URL , type="primary", use_container_width=True)


import streamlit as st
import pandas as pd
import json
from datetime import datetime, timedelta, timezone

# ======================
# 설정
# ======================
  # ✅ 여기에 구글폼 URL 넣기
KST = timezone(timedelta(hours=9))

# ======================
# 로그 저장 (session_state + 파일 jsonl 둘 다)
# ======================
def append_log(log: dict):
    # 1) 세션 메모리 저장
    if "logs" not in st.session_state:
        st.session_state.logs = []
    st.session_state.logs.append(log)

    # 2) 파일 저장(원치 않으면 아래 try 블록 삭제)
    try:
        with open("logs.jsonl", "a", encoding="utf-8") as f:
            f.write(json.dumps(log, ensure_ascii=False) + "\n")
    except Exception:
        pass

def load_file_logs():
    logs = []
    try:
        with open("logs.jsonl", "r", encoding="utf-8") as f:
            for line in f:
                logs.append(json.loads(line))
    except FileNotFoundError:
        pass
    except Exception:
        pass
    return logs

# ======================
# UI
# ======================
tab1, tab2 = st.tabs(["📌 시작하기", "📊 클릭 기록"])

# 페이지 전환 상태
if "step" not in st.session_state:
    st.session_state.step = "start"   # "start" -> "open_form"

with tab1:
    # 1) 시작 화면
    if st.session_state.step == "start":
        st.subheader("📌사전 예약 시 5회 추가 토론방 생성권 무료 지급!")

        if st.button("받으러 가기", use_container_width=True):
            append_log({
                "ts": datetime.now(KST).isoformat(),
                "type": "click",
                "page": "home",
                "target": "start"
            })

            st.session_state.step = "open_form"
            st.rerun()

    # 2) 구글폼 열기 화면
    elif st.session_state.step == "open_form":
        st.subheader("📄 설문 참여 안내")
        st.success("아래 버튼을 눌러 설문을 진행해주세요. (새 탭으로 열립니다)")

        # 구글폼 열기 클릭도 로그 남기고 싶다면: link_button을 버튼+로그로 분리
        # (link_button 자체는 클릭 이벤트를 파이썬으로 받기 어려워서 아래처럼 구성)
        col1, = st.columns(1)

        with col1:
            # 로그 남기고 -> JS로 새 탭 열기 (팝업차단 거의 없음: 사용자 클릭 이벤트 기반)
            if st.button("👉 구글폼 열기", use_container_width=True):
                append_log({
                    "ts": datetime.now(KST).isoformat(),
                    "type": "click",
                    "page": "open_form",
                    "target": "google_form_open"
                })
                st.components.v1.html(
                    f"""
                    <a id="go" href="{GOOGLE_FORM_URL}" target="_blank"></a>
                    <script>
                      document.getElementById("go").click();
                    </script>
                    """,
                    height=0
                )

        

with tab2:
    st.subheader("📊 클릭 기록")

    # 세션 로그 + 파일 로그 합쳐서 보기 (중복 가능. 필요하면 합치기 로직 추가)
    session_logs = st.session_state.get("logs", [])
    file_logs = load_file_logs()
    logs = session_logs if session_logs else file_logs

    if not logs:
        st.info("아직 클릭 기록이 없습니다.")
    else:
        df = pd.DataFrame(logs)
        if "ts" in df.columns:
            df = df.sort_values("ts", ascending=False)

        st.metric("총 기록 수", len(df))
        st.dataframe(df, use_container_width=True)

