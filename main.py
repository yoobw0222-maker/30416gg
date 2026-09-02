import streamlit as st
import random
import time

# 웹 앱 제목
st.title("🎯 행운의 룰렛 추첨기")

# 설명 문구
st.write("룰렛에 넣을 항목들을 쉼표(,)로 구분해서 입력해 주세요.")

# 사용자 입력 받기
items_input = st.text_input("항목 입력", "자장면, 짬뽕, 볶음밥, 탕수육")

# 입력된 문자열을 리스트로 변환
items = [item.strip() for item in items_input.split(",") if item.strip()]

# 돌리기 버튼
if st.button("룰렛 돌리기! 🎰"):
    if not items:
        st.warning("최소 한 개 이상의 항목을 입력해 주세요.")
    else:
        # 돌아가는 애니메이션 효과 연출
        with st.spinner("돌아가는 중..."):
            time.sleep(1.5)  # 1.5초 대기
        
        # 무작위 선택
        winner = random.choice(items)
        
        # 결과 출력
        st.balloons()  # 축하 효과 Animation
        st.success(f"🎉 당첨 결과: **{winner}**")
