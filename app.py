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
            너는 형사법 기출문제를 검수하는 똑똑하고 유능한 연구 조교야.
            지금부터 40문제 분량의 문제편과 해설편을 줄 텐데, 전체적인 흐름과 맥락을 파악해서 진짜로 이상한 부분만 나에게 보고해 줘.

            가장 먼저 해설편에 있는 정답표를 보고 누락된 빈칸이 있는지 확인해 줘.
            그리고 문제의 발문과 해설 내용이 앞뒤가 안 맞는 진짜 모순만 찾아내면 돼. 예를 들어 정답표에는 3번이라고 되어있는데 해설은 4번을 정답으로 설명한다거나, 틀린 걸 찾으라는 문제인데 해설은 정답 선지를 맞는 내용이라고 설명하는 경우 말이야.

            앞뒤 논리가 잘 맞고 정상적인 문항은 절대 언급하지 마. 정상이라는 말도 할 필요 없어.
            오직 표에서 누락된 번호랑 진짜로 논리가 어긋나는 문항만 골라서 왜 이상한지 나한테 자연스럽게 설명해 주면 돼.
            """
            
            user_prompt = f"<문제편>\n{question_text}\n\n<해설편>\n{answer_text}"
            
            with st.spinner("텍스트 정합성을 정밀 검토 중입니다..."):
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
