import streamlit as st
from openai import OpenAI

# 페이지 기본 설정
st.set_page_config(page_title="ACL 기출 및 해설 검수 시스템", page_icon="✅", layout="wide")

# 사이드바: API 키 입력
with st.sidebar:
    st.write("⚙️ 설정")
    api_key = st.text_input("OpenAI API Key를 입력하세요", type="password")

# 메인 헤더
st.title("✅ ACL 기출 및 해설 검수 시스템")
st.write("문제편과 해설편 텍스트를 각각 붙여넣고 하단의 검토 시작 버튼을 눌러주세요.")

# 좌우 화면 분할
col1, col2 = st.columns(2)

with col1:
    question_text = st.text_area("문제편 입력", height=600, placeholder="문제 텍스트를 여기에 붙여넣으세요")

with col2:
    answer_text = st.text_area("해설편 입력", height=600, placeholder="해설 텍스트를 여기에 붙여넣으세요")

# 검토 실행 버튼
if st.button("🔍 검토 시작", use_container_width=True):
    if not api_key:
        st.error("사이드바에 API 키를 입력해주세요.")
    elif not question_text or not answer_text:
        st.error("문제편과 해설편 텍스트를 모두 입력해주세요.")
    else:
        try:
            client = OpenAI(api_key=api_key)
            
            # AI에게 부여할 엄격한 시스템 프롬프트
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
            
            with st.spinner("텍스트 정합성을 정밀 검토 중입니다. 잠시만 기다려주세요..."):
                response = client.chat.completions.create(
                    model="gpt-4o", # 필요시 gpt-4-turbo 등으로 변경 가능
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    temperature=0.1 # 일관된 결과를 위해 온도를 낮춤
                )
            
            st.success("검토 완료!")
            st.markdown(response.choices[0].message.content)
            
        except Exception as e:
            st.error(f"오류가 발생했습니다: {e}")
