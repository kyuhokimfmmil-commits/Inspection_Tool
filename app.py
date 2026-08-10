if st.button("검토 시작"):
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
