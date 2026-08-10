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
            당신은 기출문제와 해설의 논리적 정합성을 검수하는 최고 수준의 전문 교정자입니다.
            단순한 텍스트 대조를 넘어 각 문항별로 심층적인 단계별 추론을 거쳐 오류를 완벽하게 잡아내십시오.
            입력된 <문제편>과 <해설편>을 대조하여 다음 항목들을 아주 엄격하게 검증하십시오.
            
            1. 정답표 누락 확인: 해설편 상단이나 하단에 제공된 정답표에 빈칸이 있는지 먼저 확인하고 모든 문항의 정답이 제대로 채워져 있는지 대조하십시오.
            2. 문제 발문과 정답의 논리적 일치: 문제에서 적절한 것을 찾는지 적절하지 않은 것을 찾는지 정확히 파악하고 해설편에서 지정된 정답 기호가 이에 논리적으로 부합하는지 철저히 확인하십시오.
            3. 해설 정합성: 해설의 O/X 판단 내용이 문제편 선지 내용과 모순되지 않는지 분석하십시오. 정답 선지에 대한 해설이 발문의 요구사항과 일치하는지 특히 집중해서 검토하십시오.
            4. 형식 정합성: 해설에서 O/X 등 일관된 형식에서 벗어난 표기가 있는지 확인하십시오.
            
            [출력 형식]
            - 정답표 누락이나 전체적인 편집 오류가 있다면 결과 최상단에 강하게 강조하여 서술하십시오.
            - 오류가 전혀 없는 문항: "✅ [N번] 이상 없음"
            - 오류가 발견된 문항: "🚨 [N번] 오류 발견" 제목과 함께 어떤 논리적 모순이나 빈칸이 발생했는지 구체적인 이유와 수정 방향을 서술하십시오.
            """
            
            user_prompt = f"<문제편>\n{question_text}\n\n<해설편>\n{answer_text}"
            
            with st.spinner("최고 성능 추론 모델로 텍스트 정합성을 정밀 검토 중입니다..."):
                response = client.chat.completions.create(
                    model="o3-mini", 
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ]
                )
            
            st.success("검토 완료!")
            st.markdown(response.choices[0].message.content)
            
        except Exception as e:
            st.error(f"오류가 발생했습니다: {e}")
