import streamlit as st
import streamlit.components.v1 as components
import re

st.title("🎯 아무거나 룰렛")

# 사용자 입력 받기
items_input = st.text_input(
    "항목 및 확률 입력 (쉼표로 구분)", 
    "자장면(40%), 짬뽕(30%), 볶음밥(20%), 탕수육(10%)"
)

# 텍스트 파싱 함수 (항목명과 확률 추출)
def parse_items(input_str):
    raw_items = [item.strip() for item in input_str.split(",") if item.strip()]
    if not raw_items:
        return []

    parsed = []
    specified_sum = 0
    unspecified_count = 0

    for item in raw_items:
        # 항목명(숫자%) 패턴 매칭
        match = re.search(r'^(.*?)\s*\((\d+(?:\.\d+)?)\%\)$', item)
        if match:
            name = match.group(1).strip()
            prob = float(match.group(2))
            parsed.append({"name": name, "prob": prob, "specified": True})
            specified_sum += prob
        else:
            parsed.append({"name": item, "prob": None, "specified": False})
            unspecified_count += 1

    # 확률을 입력하지 않은 항목이 있는 경우 남은 확률을 균등 분배
    if unspecified_count > 0:
        remaining_prob = max(0.0, 100.0 - specified_sum)
        default_prob = remaining_prob / unspecified_count
        for item in parsed:
            if not item["specified"]:
                item["prob"] = default_prob
    
    # 지정 확률 총합이 100%를 넘는 경우 자동 정규화
    total_prob = sum(item["prob"] for item in parsed)
    if total_prob > 0:
        for item in parsed:
            item["weight"] = item["prob"] / total_prob
    else:
        for item in parsed:
            item["weight"] = 1.0 / len(parsed)

    return parsed

parsed_items = parse_items(items_input)

if len(parsed_items) < 2:
    st.warning("최소 2개 이상의 항목을 입력해 주세요.")
else:
    # JavaScript 전달용 데이터 준비
    js_names = [f"{item['name']} ({item['prob']:.1f}%)" for item in parsed_items]
    js_weights = [item["weight"] for item in parsed_items]

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
            <button id="spinBtn" onclick="spin()">룰렛 돌리기! 🎰</button>
            <div id="result"></div>
        </div>

        <script>
            const names = {js_names};
            const weights = {js_weights};
            const numItems = names.length;
            
            const canvas = document.getElementById('wheel');
            const ctx = canvas.getContext('2d');
            const colors = ['#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF', '#FF9F40', '#E7E9ED', '#76D7C4'];

            // 확률 기반 각 각도의 크기 계산 (전체 = 2 * PI)
            const arcs = weights.map(w => w * 2 * Math.PI);

            let currentAngle = 0;
            let isSpinning = false;

            function drawWheel() {{
                ctx.clearRect(0, 0, 320, 320);
                let startAngle = currentAngle;

                for (let i = 0; i < numItems; i++) {{
                    const arc = arcs[i];
                    const endAngle = startAngle + arc;

                    ctx.beginPath();
                    ctx.fillStyle = colors[i % colors.length];
                    ctx.moveTo(160, 160);
                    ctx.arc(160, 160, 150, startAngle, endAngle);
                    ctx.fill();
                    ctx.stroke();

                    // 텍스트 출력 (조각 크기가 일정 이상일 때만 표시)
                    if (arc > 0.08) {{
                        ctx.save();
                        ctx.fillStyle = "#ffffff";
                        ctx.font = "bold 13px sans-serif";
                        const textAngle = startAngle + arc / 2;
                        ctx.translate(160 + Math.cos(textAngle) * 95, 160 + Math.sin(textAngle) * 95);
                        ctx.rotate(textAngle + Math.PI / 2);
                        
                        // 텍스트 자르기 처리
                        let text = names[i];
                        if (text.length > 12) text = text.substring(0, 10) + "..";
                        
                        ctx.fillText(text, -ctx.measureText(text).width / 2, 0);
                        ctx.restore();
                    }}

                    startAngle = endAngle;
                }}
            }}

            function spin() {{
                if (isSpinning) return;
                isSpinning = true;
                document.getElementById('spinBtn').disabled = true;
                document.getElementById('result').innerText = "두근두근... 룰렛이 돌고 있습니다!";

                const duration = 10000; // 10초
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
                        
                        // 12시 방향(화살표) 기준으로 당첨 항목 계산
                        const normalizedAngle = (2 * Math.PI - (currentAngle % (2 * Math.PI))) % (2 * Math.PI);
                        const pointerAngle = (normalizedAngle + Math.PI / 2) % (2 * Math.PI);
                        
                        let accumulatedAngle = 0;
                        let winningIndex = 0;
                        for (let i = 0; i < numItems; i++) {{
                            accumulatedAngle += arcs[i];
                            if (pointerAngle <= accumulatedAngle) {{
                                winningIndex = i;
                                break;
                            }}
                        }}
                        
                        document.getElementById('result').innerText = "🎉 당첨 결과: " + names[winningIndex];
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
