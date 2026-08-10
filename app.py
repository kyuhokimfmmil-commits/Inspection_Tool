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

header_col1, header_col2 = st.columns([1, 3.5])

with header_col1:
    st.image("acl_logo.png", use_container_width=True)

with header_col2:
    st.markdown("""
        <div style="padding-top: 35px; padding-left: 10px;">
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
            당신은 형사법 기출문제와 해설의 논리적 정합성을 검수하는 전문 교정자입니다.
            법리적 타당성 검토보다는 텍스트 간의 기계적인 대조 작업과 형식 오류 탐지에 집중하십시오.
            입력된 <문제편>과 <해설편>을 대조하여 다음을 엄격하게 검증하십시오.
            
            1. 정답 일치 여부: 문제 발문(옳은/옳지 않은/개수 등)과 선지, 해설의 정답 기호가 완벽히 일치하는지.
            2. 해설 정합성: 해설의 O/X 판단 내용이 선지 내용과 모순되지 않는지.
            3. 판례 인용: 대법원 판례 번호와 판시 내용이 선지 맥락에 맞게 배치되었는지 (순서 뒤바뀜 등 탐지).
            
            [출력 형식]
            - 오류가 없는 문항: "✅ [N번] 이상 없음"
            - 오류가 발견된 문항: "🚨 [N번] 오류 발견" 제목과 함께 구체적인 수정 방향을 리스트로 제시.
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
