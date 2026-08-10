import streamlit as st
import streamlit.components.v1 as components
from openai import OpenAI

st.set_page_config(
    page_title="ACL 문제검수 시스템", 
    page_icon="✅", 
    layout="wide",
    initial_sidebar_state="expanded"
)

if 'q_input' not in st.session_state:
    st.session_state.q_input = ""
if 'a_input' not in st.session_state:
    st.session_state.a_input = ""

def reset_inputs():
    st.session_state.q_input = ""
    st.session_state.a_input = ""

st.markdown("""
    <style>
    * {
        font-family: 'Pretendard', -apple-system, BlinkMacSystemFont, "Apple SD Gothic Neo", "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    }
    
    .stApp {
        background-color: #FBFBFD; 
        color: #1D1D1F;
    }

    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}

    .stTextArea textarea {
        background-color: #FFFFFF;
        border: 1px solid #D2D2D7;
        border-radius: 12px;
        padding: 16px;
        font-size: 15px;
        line-height: 1.6;
        color: #1D1D1F;
        box-shadow: 0 2px 8px rgba(0,0,0,0.02);
        transition: all 0.3s ease;
    }
    .stTextArea textarea:focus {
        border-color: #007AFF;
        box-shadow: 0 0 0 4px rgba(0, 122, 255, 0.1);
    }

    .stButton button[kind="secondary"] {
        background-color: #E5E5EA;
        color: #1D1D1F;
        border-radius: 980px;
        padding: 14px 28px;
        font-size: 17px;
        font-weight: 600;
        border: none;
        box-shadow: 0 2px 8px rgba(0,0,0,0.02);
        transition: all 0.3s ease;
        width: 100%;
        margin-top: 10px;
    }
    .stButton button[kind="secondary"]:hover {
        background-color: #D1D1D6;
        transform: translateY(-1px);
    }

    .stButton button[kind="primary"] {
        background-color: #007AFF;
        color: white;
        border-radius: 980px;
        padding: 14px 28px;
        font-size: 17px;
        font-weight: 600;
        border: none;
        box-shadow: 0 4px 14px rgba(0, 122, 255, 0.3);
        transition: all 0.3s ease;
        width: 100%;
        margin-top: 10px;
    }
    .stButton button[kind="primary"]:hover {
        background-color: #0071E3;
        box-shadow: 0 6px 20px rgba(0, 122, 255, 0.4);
        transform: translateY(-1px);
        color: white;
    }
    
    .input-label {
        font-weight: 600; 
        font-size: 15px;
        margin-bottom: 8px; 
        color: #1D1D1F;
    }

    [data-testid="stImage"] {
        display: flex;
        justify-content: flex-start;
    }
    [data-testid="stImage"] img {
        mix-blend-mode: multiply;
        object-fit: contain;
    }
    </style>
""", unsafe_allow_html=True)

components.html(
    """
    <script>
    const doc = window.parent.document;
    doc.addEventListener('keydown', function(event) {
        if ((event.key === 'c' || event.key === 'C') && event.target.tagName !== 'INPUT' && event.target.tagName !== 'TEXTAREA') {
            event.stopPropagation();
            event.preventDefault();
        }
    }, true);
    </script>
    """,
    height=0,
    width=0,
)

with st.sidebar:
    st.markdown("<h3 style='color: #1D1D1F; font-weight: 600;'>⚙️ Settings</h3>", unsafe_allow_html=True)
    api_key = st.text_input("OpenAI API Key", type="password", placeholder="sk-...")
    st.caption("API 키는 서버에 저장되지 않으며 즉시 폐기됩니다.")

header_col1, header_col2 = st.columns([1, 4], vertical_alignment="center")

with header_col1:
    st.image("acl_logo.png", use_container_width=True)

with header_col2:
    st.markdown("""
        <div style="padding-left: 10px;">
            <div style="font-size: 16px; font-weight: 800; letter-spacing: 0.12em; color: #1D1D1F; margin-bottom: 2px;">
                CONTENT VERIFICATION
            </div>
            <div style="font-size: 34px; font-weight: 800; color: #1D1D1F; letter-spacing: -0.03em;">
                문제 검수 시스템
            </div>
        </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

col1, col2 = st.columns(2, gap="large")

with col1:
    st.markdown("<div class='input-label'>문제편</div>", unsafe_allow_html=True)
    question_text = st.text_area("문제편", height=550, label_visibility="collapsed", placeholder="문제 텍스트를 입력하세요...", key="q_input")

with col2:
    st.markdown("<div class='input-label'>해설편</div>", unsafe_allow_html=True)
    answer_text = st.text_area("해설편", height=550, label_visibility="collapsed", placeholder="해설 텍스트를 입력하세요...", key="a_input")

btn_col1, btn_col2 = st.columns(2, gap="large")

with btn_col1:
    start_review = st.button("검토 시작", type="primary")

with btn_col2:
    st.button("초기화", on_click=reset_inputs, type="secondary")

if start_review:
    if not api_key:
        st.error("좌측 사이드바에 API 키를 입력해주세요.")
    elif not question_text or not answer_text:
        st.error("문제편과 해설편 텍스트를 모두 입력해주세요.")
    else:
        try:
            client = OpenAI(api_key=api_key)
            
            system_prompt = """
            너는 법학 기출문제 원고를 검수하는 최고 수준의 연구 조교야.
            멍청하게 글자만 대조하지 말고, 대한민국 객관식 시험의 '출제 논리'를 완벽하게 이해하고 40문항 전체를 끝까지 검토해.

            [객관식 시험의 절대 논리 - 이것을 모르면 오류를 뱉지 마라]
            1. 발문에서 "적절하지 않은 것", "옳지 않은 것"을 고르라고 했다면?
               -> 정답 선지는 당연히 '틀린 내용'이어야 해. 따라서 해설에서 해당 선지를 "X" 또는 "틀린 지문"이라고 설명하고 있다면 그것은 논리적으로 완벽히 '정상'이야. 절대 오류가 아니야.
            2. 발문에서 "적절한 것", "옳은 것"을 고르라고 했다면?
               -> 정답 선지는 당연히 '맞는 내용'이어야 해. 해설에서 해당 선지를 "O" 또는 "맞는 지문"이라고 설명하면 '정상'이야.
            
            [네가 찾아야 할 '진짜 오류'의 예시]
            - 정답표 누락: 해설편 상/하단 정답표에 1번부터 40번 중 아예 빈칸으로 누락된 번호가 있는 경우.
            - 진짜 논리 모순: "옳지 않은 것"을 찾으라고 했고 정답표에 3번이라고 되어있는데, 해설을 읽어보니 "3번 선지는 맞는 지문(O)이다"라고 설명하고 있는 경우. (앞뒤가 안 맞음)
            - 정답 번호 불일치: 표와 제목에는 정답이 4번이라고 적혀있는데, 상세 해설 텍스트에서는 3번이 정답이라고 딴소리를 하는 경우.

            [검토 및 출력 지시사항]
            - 논리가 완벽하게 들어맞는 정상 문항은 입 밖으로 꺼내지도 마. "이상 없음"이라는 말조차 출력하지 마.
            - 오직 '정답표 누락 번호'와 '진짜 논리 모순이 발생한 문항'만 골라내어 결과물로 보여줘. 내가 직접 찾아냈던 4가지 오류(정답표 빈칸, 6번, 21번, 40번 오류) 수준의 날카로움을 보여줘.
            """
            
            user_prompt = f"<문제편>\n{question_text}\n\n<해설편>\n{answer_text}"
            
            with st.spinner("최상위 모델을 통해 텍스트 정합성을 정밀 검토 중입니다..."):
                response = client.chat.completions.create(
                    model="gpt-4o", 
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    temperature=0.1 
                )
            
            st.success("검토 완료!")
            st.markdown(response.choices[0].message.content)
            
        except Exception as e:
            st.error(f"오류가 발생했습니다: {e}")
