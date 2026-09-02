import streamlit as st
import streamlit.components.v1 as components
import re

st.title("🎯 아무거나 룰렛")

# 사용자 입력 받기
items_input = st.text_input(
    "항목 및 확률 입력 (쉼표로 구분)", 
    "1등(2%), 2등(5%), 3등(10%), 4등(20%), 꽝(63%)"
)

# 텍스트 파싱 함수
def parse_items(input_str):
    raw_items = [item.strip() for item in input_str.split(",") if item.strip()]
    if not raw_items:
        return []

    parsed = []
    specified_sum = 0
    unspecified_count = 0

    for item in raw_items:
        match = re.search(r'^(.*?)\s*\((\d+(?:\.\d+)?)\%\)$', item)
        if match:
            name = match.group(1).strip()
            prob = float(match.group(2))
            parsed.append({"name": name, "prob": prob, "specified": True})
            specified_sum += prob
        else:
            parsed.append({"name": item, "prob": None, "specified": False})
            unspecified_count += 1

    if unspecified_count > 0:
        remaining_prob = max(0.0, 100.0 - specified_sum)
        default_prob = remaining_prob / unspecified_count
        for item in parsed:
            if not item["specified"]:
                item["prob"] = default_prob
    
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
                width: 440px;
                height: 440px;
                margin-top: 10px;
            }}
            .pointer {{
                position: absolute;
                top: 0px;
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
                <canvas id="wheel" width="440" height="440"></canvas>
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

            const arcs = weights.map(w => w * 2 * Math.PI);
            const centerX = 220;
            const centerY = 220;
            const radius = 140; // 룰렛 원 반지름

            let currentAngle = 0;
            let isSpinning = false;

            function drawWheel() {{
                ctx.clearRect(0, 0, 440, 440);
                let startAngle = currentAngle;

                // 1. 룰렛 조각 그리기
                for (let i = 0; i < numItems; i++) {{
                    const arc = arcs[i];
                    const endAngle = startAngle + arc;

                    ctx.beginPath();
                    ctx.fillStyle = colors[i % colors.length];
                    ctx.moveTo(centerX, centerY);
                    ctx.arc(centerX, centerY, radius, startAngle, endAngle);
                    ctx.fill();
                    ctx.stroke();

                    startAngle = endAngle;
                }}

                // 2. 텍스트 및 외부 지시선 그리기
                startAngle = currentAngle;
                for (let i = 0; i < numItems; i++) {{
                    const arc = arcs[i];
                    const midAngle = startAngle + arc / 2;

                    // 큰 조각: 내부에 텍스트 작성
                    if (arc >= 0.25) {{
                        ctx.save();
                        ctx.fillStyle = "#ffffff";
                        ctx.font = "bold 13px sans-serif";
                        ctx.translate(centerX + Math.cos(midAngle) * (radius * 0.65), centerY + Math.sin(midAngle) * (radius * 0.65));
                        ctx.rotate(midAngle + Math.PI / 2);
                        
                        let text = names[i];
                        if (text.length > 10) text = text.substring(0, 8) + "..";
                        
                        ctx.fillText(text, -ctx.measureText(text).width / 2, 0);
                        ctx.restore();
                    }} 
                    // 작은 조각: 외부로 지시선을 빼서 텍스트 작성
                    else {{
                        const lineStartX = centerX + Math.cos(midAngle) * (radius - 5);
                        const lineStartY = centerY + Math.sin(midAngle) * (radius - 5);
                        const lineEndX = centerX + Math.cos(midAngle) * (radius + 25);
                        const lineEndY = centerY + Math.sin(midAngle) * (radius + 25);

                        // 지시선 그리기
                        ctx.beginPath();
                        ctx.strokeStyle = "#333333";
                        ctx.lineWidth = 1.5;
                        ctx.moveTo(lineStartX, lineStartY);
                        ctx.lineTo(lineEndX, lineEndY);
                        ctx.stroke();

                        // 텍스트 그리기
                        ctx.save();
                        ctx.fillStyle = "#333333";
                        ctx.font = "bold 11px sans-serif";
                        
                        // 텍스트 위치 정렬 (좌/우 방향에 맞춤)
                        const isRightSide = Math.cos(midAngle) >= 0;
                        ctx.textAlign = isRightSide ? "left" : "right";
                        
                        const textX = lineEndX + (isRightSide ? 5 : -5);
                        const textY = lineEndY + 4;

                        ctx.fillText(names[i], textX, textY);
                        ctx.restore();
                    }}

                    startAngle += arc;
                }}
            }}

            function spin() {{
                if (isSpinning) return;
                isSpinning = true;
                document.getElementById('spinBtn').disabled = true;
                document.getElementById('result').innerText = "두근두근... 룰렛이 돌고 있습니다!";

                const duration = 10000;
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
    
    components.html(html_code, height=530)
