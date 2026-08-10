import streamlit as st
from openai import OpenAI

st.set_page_config(
    page_title="ACL 문제검수 시스템", 
    page_icon="✅", 
    layout="wide",
    initial_sidebar_state="expanded"
)

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

    .stButton button {
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
    .stButton button:hover {
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
    question_text = st.text_area("문제편", height=550, label_visibility="collapsed", placeholder="문제 텍스트를 입력하세요...")

with col2:
    st.markdown("<div class='input-label'>해설편</div>", unsafe_allow_html=True)
    answer_text = st.text_area("해설편", height=550, label_visibility="collapsed", placeholder="해설 텍스트를 입력하세요...")

if st.button("검토 시작"):
    if not api_key:
        st.error("좌측 사이드바에 API 키를 입력해주세요.")
    elif not question_text or not answer_text:
        st.error("문제편과 해설편 텍스트를 모두 입력해주세요.")
    else:
        try:
            client = OpenAI(api_key=api_key)
            
            system_prompt = """
            당신은 형사법 기출문제와 해설의 논리적 모순을 잡아내는 꼼꼼한 교정자입니다.
            입력된 텍스트에는 40문제 분량의 문제와 해설이 있습니다. 절대 중간에 생략하거나 뭉뚱그리지 말고 1번부터 40번까지 전부 검토해 주세요.
            
            가장 먼저 해설편의 정답표를 확인해서 빈칸으로 누락된 번호가 있는지 찾아내어 맨 윗줄에 알려주세요.
            그 다음에는 각 문항별로 문제 발문의 요구사항과 해설의 논리가 어긋나는 치명적인 오류만 찾아내면 됩니다.
            예를 들어 발문에서는 가장 적절한 것을 찾으라고 했는데 해설에서는 정답 선지를 틀린 내용 즉 X라고 설명하고 있다면 논리적 오류입니다. 반대로 발문에서 적절하지 않은 것을 찾으라고 했는데 해설에서 정답 선지를 맞는 내용 즉 O라고 설명하고 있어도 오류입니다.
            이런 식으로 정답표의 기호와 해설의 OX 설명 내용 그리고 문제 발문이 엇갈리는 경우만 콕 집어내 주세요.
            
            시간과 토큰을 절약해야 하므로 정상적으로 잘 연결되는 문항들은 절대로 출력하지 마세요. 이상 없다는 말도 쓰지 마세요.
            오직 오류가 발견된 문항만 경광등 기호와 함께 문항 번호를 적고 왜 모순이 발생하는지 그 이유를 구체적으로 적어주시면 됩니다.
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
