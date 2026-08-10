import streamlit as st
from openai import OpenAI

# 1. 페이지 기본 설정 (아이콘을 사과 모양으로 변경)
st.set_page_config(page_title="ACL 문제검수 시스템", page_icon="✅", layout="wide")

# 2. 애플 감성 커스텀 CSS 주입
st.markdown("""
    <style>
    /* 기본 폰트 설정 (Apple SD Gothic Neo, Pretendard 등 깔끔한 산세리프 폰트 강제 적용) */
    * {
        font-family: 'Pretendard', -apple-system, BlinkMacSystemFont, "Apple SD Gothic Neo", "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    }
    
    /* 메인 배경(아주 밝은 웜그레이) 및 텍스트 색상 */
    .stApp {
        background-color: #FBFBFD; 
        color: #1D1D1F;
    }

    /* 상단 기본 메뉴 및 푸터 등 불필요한 요소 숨기기 */
    header {visibility: hidden;}
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}

    /* 메인 로고 및 서브타이틀 타이포그래피 */
    .apple-logo {
        text-align: center;
        font-weight: 700;
        font-size: 38px;
        letter-spacing: -0.015em;
        color: #1D1D1F;
        margin-top: 1rem;
        margin-bottom: 0.2rem;
    }
    .apple-subtitle {
        text-align: center;
        font-weight: 400;
        font-size: 20px;
        color: #86868B; /* 애플 특유의 세컨더리 텍스트 컬러 */
        letter-spacing: -0.01em;
        margin-bottom: 3.5rem;
    }

    /* 텍스트 에어리어 (모서리 둥글게, 그림자, 포커스 효과) */
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
        border-color: #007AFF; /* 애플 블루 */
        box-shadow: 0 0 0 4px rgba(0, 122, 255, 0.1); /* 맥OS 포커스 링 효과 */
    }

    /* 버튼 스타일링 (알약 모양, 그라데이션 없음, 깔끔한 그림자) */
    .stButton button {
        background-color: #007AFF;
        color: white;
        border-radius: 980px; /* 완전한 둥근 모서리 */
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
    
    /* 라벨 텍스트 스타일링 */
    .input-label {
        font-weight: 600; 
        font-size: 15px;
        margin-bottom: 8px; 
        color: #1D1D1F;
    }
    </style>
""", unsafe_allow_html=True)

# 3. 사이드바 (미니멀하게 구성)
with st.sidebar:
    st.markdown("<h3 style='color: #1D1D1F; font-weight: 600;'>Settings</h3>", unsafe_allow_html=True)
    api_key = st.text_input("OpenAI API Key", type="password", placeholder="sk-...")
    st.caption("API 키는 서버에 저장되지 않으며 즉시 폐기됩니다.")

# 4. 헤더 렌더링 (기본 st.title 대신 HTML 클래스 사용)
st.markdown("<div class='apple-logo'>ACL Communication</div>", unsafe_allow_html=True)
st.markdown("<div class='apple-subtitle'>문제검수 시스템</div>", unsafe_allow_html=True)

# 5. 메인 레이아웃 (좌우 분할)
col1, col2 = st.columns(2, gap="large") # gap을 넓게 주어 여백의 미 강조

with col1:
    st.markdown("<div class='input-label'>문제편</div>", unsafe_allow_html=True)
    # label_visibility="collapsed"를 통해 기본 라벨을 숨기고 위의 커스텀 라벨 사용
    question_text = st.text_area("문제편", height=550, label_visibility="collapsed", placeholder="문제 텍스트를 입력하세요...")

with col2:
    st.markdown("<div class='input-label'>해설편</div>", unsafe_allow_html=True)
    answer_text = st.text_area("해설편", height=550, label_visibility="collapsed", placeholder="해설 텍스트를 입력하세요...")

# 6. 실행 버튼 및 백엔드 로직
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
