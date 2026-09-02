import streamlit as st
import streamlit.components.v1 as components

# 웹 앱 제목 변경
st.title("🎯 아무거나 룰렛")

# 사용자 입력 받기
items_input = st.text_input("항목 입력 (쉼표로 구분)", "자장면, 짬뽕, 볶음밥, 탕수육, 초밥, 피자")

# 입력된 문자열을 리스트로 변환
items = [item.strip() for item in items_input.split(",") if item.strip()]

if len(items) < 2:
    st.warning("최소 2개 이상의 항목을 입력해 주세요.")
else:
    # HTML/JS 커스텀 룰렛 컴포넌트 생성
    html_code = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            .roulette-container {{
                display: flex;
                flex-direction: column;
                align-items: center;
                font-family: sans-serif;
            }}
            .wheel-wrapper {{
                position: relative;
                width: 320px;
                height: 320px;
                margin-top: 10px;
            }}
            .pointer {{
                position: absolute;
                top: -10px;
                left: 50%;
                transform: translateX(-50%);
                width: 0;
                height: 0;
                border-left: 15px solid transparent;
                border-right: 15px solid transparent;
                border-top: 25px solid red;
                z-index: 10;
            }}
            canvas {{
                border-radius: 50%;
                box-shadow: 0 4px 10px rgba(0,0,0,0.2);
            }}
            button {{
                margin-top: 20px;
                padding: 10px 24px;
                font-size: 16px;
                font-weight: bold;
                background-color: #FF4B4B;
                color: white;
                border: none;
                border-radius: 8px;
                cursor: pointer;
            }}
            button:disabled {{
                background-color: #ccc;
                cursor: not-allowed;
            }}
            #result {{
                margin-top: 15px;
                font-size: 20px;
                font-weight: bold;
                color: #2E7D32;
                height: 30px;
            }}
        </style>
    </head>
    <body>
        <div class="roulette-container">
            <div class="wheel-wrapper">
                <div class="pointer"></div>
                <canvas id="wheel" width="320" height="320"></canvas>
            </div>
            <!-- 버튼 문구 변경 -->
            <button id="spinBtn" onclick="spin()">룰렛 돌리기! 🎰</button>
            <div id="result"></div>
        </div>

        <script>
            const items = {items};
            const canvas = document.getElementById('wheel');
            const ctx = canvas.getContext('2d');
            const numItems = items.length;
            const arc = (2 * Math.PI) / numItems;
            
            const colors = ['#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF', '#FF9F40', '#E7E9ED', '#76D7C4'];

            let currentAngle = 0;
            let isSpinning = false;

            function drawWheel() {{
                ctx.clearRect(0, 0, 320, 320);
                for (let i = 0; i < numItems; i++) {{
                    const angle = currentAngle + i * arc;
                    ctx.beginPath();
                    ctx.fillStyle = colors[i % colors.length];
                    ctx.moveTo(160, 160);
                    ctx.arc(160, 160, 150, angle, angle + arc);
                    ctx.fill();
                    ctx.stroke();

                    ctx.save();
                    ctx.fillStyle = "#ffffff";
                    ctx.font = "bold 14px sans-serif";
                    ctx.translate(160 + Math.cos(angle + arc / 2) * 100, 160 + Math.sin(angle + arc / 2) * 100);
                    ctx.rotate(angle + arc / 2 + Math.PI / 2);
                    ctx.fillText(items[i], -ctx.measureText(items[i]).width / 2, 0);
                    ctx.restore();
                }}
            }}

            function spin() {{
                if (isSpinning) return;
                isSpinning = true;
                document.getElementById('spinBtn').disabled = true;
                document.getElementById('result').innerText = "두근두근... 룰렛이 돌고 있습니다!";

                const duration = 10000; // 10초 유지
                const startAngle = currentAngle;
                
                const randomAngle = Math.random() * 2 * Math.PI;
                const totalRotation = (10 * 2 * Math.PI) + randomAngle;
                
                const startTime = performance.now();

                function animate(currentTime) {{
                    const elapsed = currentTime - startTime;
                    if (elapsed < duration) {{
                        const progress = elapsed / duration;
                        const easeOut = 1 - Math.pow(1 - progress, 3); 
                        currentAngle = startAngle + (totalRotation * easeOut);
                        drawWheel();
                        requestAnimationFrame(animate);
                    }} else {{
                        currentAngle = startAngle + totalRotation;
                        drawWheel();
                        isSpinning = false;
                        document.getElementById('spinBtn').disabled = false;
                        
                        const normalizedAngle = (2 * Math.PI - (currentAngle % (2 * Math.PI))) % (2 * Math.PI);
                        const adjustedAngle = (normalizedAngle + Math.PI / 2) % (2 * Math.PI);
                        const winningIndex = Math.floor(adjustedAngle / arc) % numItems;
                        
                        document.getElementById('result').innerText = "🎉 당첨 결과: " + items[winningIndex];
                    }}
                }}

                requestAnimationFrame(animate);
            }}

            drawWheel();
        </script>
    </body>
    </html>
    """
    
    components.html(html_code, height=480)
