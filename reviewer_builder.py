import csv
import json
import sys
import os

def generate_flashcard_app(csv_filepath, output_html="nursing_reviewer.html"):
    if not os.path.exists(csv_filepath):
        print(f"Error: File '{csv_filepath}' not found.")
        return

    cards = []
    with open(csv_filepath, mode='r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Normalize column header keys (handles whitespace/casing variations)
            clean_row = {k.strip().lower(): v.strip() for k, v in row.items() if k}
            
            item_no = clean_row.get('item no.', clean_row.get('item no', clean_row.get('item', '')))
            question = clean_row.get('question', '')
            answer = clean_row.get('answer', '')
            
            if question and answer:
                cards.append({
                    "item_no": item_no,
                    "question": question,
                    "answer": answer
                })

    if not cards:
        print("Error: No valid cards found. Ensure headers are 'item no.', 'question', and 'answer'.")
        return

    cards_json = json.dumps(cards, ensure_ascii=False, indent=2)

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Nursing Board Exam Flashcard Reviewer</title>
    <style>
        :root {{
            --bg-color: #f0f4f8;
            --card-bg: #ffffff;
            --primary: #0284c7;
            --primary-hover: #0369a1;
            --accent-green: #059669;
            --text-dark: #1e293b;
            --text-muted: #64748b;
            --shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 8px 10px -6px rgba(0, 0, 0, 0.1);
            --border-radius: 20px;
        }}

        * {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
            font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, Roboto, sans-serif;
        }}

        body {{
            background-color: var(--bg-color);
            color: var(--text-dark);
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }}

        .container {{
            width: 100%;
            max-width: 680px;
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 20px;
        }}

        .header {{
            text-align: center;
            width: 100%;
        }}

        .header h1 {{
            font-size: 1.75rem;
            color: #0f172a;
            margin-bottom: 6px;
        }}

        .header p {{
            color: var(--text-muted);
            font-size: 0.95rem;
        }}

        .progress-container {{
            width: 100%;
            background: #e2e8f0;
            height: 8px;
            border-radius: 4px;
            overflow: hidden;
            margin-top: 12px;
        }}

        .progress-bar {{
            height: 100%;
            background: var(--primary);
            width: 0%;
            transition: width 0.3s ease;
        }}

        /* 3D Flip Card Effect */
        .flashcard-wrapper {{
            perspective: 1200px;
            width: 100%;
            height: 380px;
            cursor: pointer;
        }}

        .flashcard {{
            width: 100%;
            height: 100%;
            position: relative;
            transform-style: preserve-3d;
            transition: transform 0.6s cubic-bezier(0.4, 0, 0.2, 1);
            box-shadow: var(--shadow);
            border-radius: var(--border-radius);
        }}

        .flashcard.flipped {{
            transform: rotateY(180deg);
        }}

        .card-face {{
            position: absolute;
            inset: 0;
            width: 100%;
            height: 100%;
            backface-visibility: hidden;
            -webkit-backface-visibility: hidden;
            border-radius: var(--border-radius);
            background: var(--card-bg);
            padding: 32px;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            border: 1px solid #e2e8f0;
        }}

        .card-front {{
            border-top: 6px solid var(--primary);
        }}

        .card-back {{
            transform: rotateY(180deg);
            border-top: 6px solid var(--accent-green);
            background: #f8fafc;
        }}

        .badge-row {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-size: 0.85rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }}

        .item-badge {{
            background: #e0f2fe;
            color: var(--primary);
            padding: 4px 12px;
            border-radius: 12px;
        }}

        .type-badge {{
            color: var(--text-muted);
        }}

        .card-body {{
            flex-grow: 1;
            display: flex;
            align-items: center;
            justify-content: center;
            text-align: center;
            padding: 20px 0;
            overflow-y: auto;
        }}

        .card-text {{
            font-size: 1.25rem;
            line-height: 1.6;
            color: #334155;
            font-weight: 500;
        }}

        .card-back .card-text {{
            color: #065f46;
            font-weight: 600;
        }}

        .card-footer-tip {{
            text-align: center;
            font-size: 0.8rem;
            color: #94a3b8;
        }}

        .controls {{
            display: flex;
            gap: 12px;
            width: 100%;
            justify-content: center;
            align-items: center;
            flex-wrap: wrap;
        }}

        .btn {{
            background: #ffffff;
            border: 1px solid #cbd5e1;
            color: #334155;
            padding: 12px 22px;
            border-radius: 12px;
            font-size: 0.95rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s ease;
            box-shadow: 0 1px 2px rgba(0,0,0,0.05);
        }}

        .btn:hover {{
            background: #f1f5f9;
            border-color: #94a3b8;
        }}

        .btn-primary {{
            background: var(--primary);
            color: #ffffff;
            border: none;
        }}

        .btn-primary:hover {{
            background: var(--primary-hover);
        }}

        .counter {{
            font-weight: 600;
            color: var(--text-muted);
            font-size: 0.95rem;
            min-width: 90px;
            text-align: center;
        }}

        @media (max-width: 480px) {{
            .flashcard-wrapper {{
                height: 320px;
            }}
            .card-text {{
                font-size: 1.1rem;
            }}
            .btn {{
                padding: 10px 16px;
                font-size: 0.85rem;
            }}
        }}
    </style>
</head>
<body>

<div class="container">
    <div class="header">
        <h1>🏥 Nursing Board Exam Reviewer</h1>
        <p>Click card or press Spacebar / Enter to flip</p>
        <div class="progress-container">
            <div class="progress-bar" id="progressBar"></div>
        </div>
    </div>

    <!-- Flashcard -->
    <div class="flashcard-wrapper" onclick="flipCard()">
        <div class="flashcard" id="flashcard">
            <!-- Front -->
            <div class="card-face card-front">
                <div class="badge-row">
                    <span class="item-badge" id="itemBadgeFront">Item #1</span>
                    <span class="type-badge">QUESTION</span>
                </div>
                <div class="card-body">
                    <p class="card-text" id="questionText"></p>
                </div>
                <div class="card-footer-tip">Click card to reveal answer 🔄</div>
            </div>
            <!-- Back -->
            <div class="card-face card-back">
                <div class="badge-row">
                    <span class="item-badge" style="background:#d1fae5; color:#059669;" id="itemBadgeBack">Item #1</span>
                    <span class="type-badge" style="color:#059669;">ANSWER</span>
                </div>
                <div class="card-body">
                    <p class="card-text" id="answerText"></p>
                </div>
                <div class="card-footer-tip">Click card to return to question 🔄</div>
            </div>
        </div>
    </div>

    <!-- Controls -->
    <div class="controls">
        <button class="btn" onclick="prevCard()">← Prev</button>
        <span class="counter" id="counterText">0 / 0</span>
        <button class="btn" onclick="nextCard()">Next →</button>
        <button class="btn btn-primary" onclick="shuffleCards()">🔀 Shuffle</button>
    </div>
</div>

<script>
    const originalCards = {cards_json};
    let cards = [...originalCards];
    let currentIndex = 0;
    let isFlipped = false;

    const flashcard = document.getElementById('flashcard');
    const questionText = document.getElementById('questionText');
    const answerText = document.getElementById('answerText');
    const itemBadgeFront = document.getElementById('itemBadgeFront');
    const itemBadgeBack = document.getElementById('itemBadgeBack');
    const counterText = document.getElementById('counterText');
    const progressBar = document.getElementById('progressBar');

    function updateCard() {{
        if (cards.length === 0) return;
        
        if (isFlipped) {{
            flashcard.classList.remove('flipped');
            isFlipped = false;
            setTimeout(renderContent, 200);
        }} else {{
            renderContent();
        }}
    }}

    function renderContent() {{
        const card = cards[currentIndex];
        questionText.textContent = card.question;
        answerText.textContent = card.answer;
        
        const itemLabel = card.item_no ? `Item #${{card.item_no}}` : `Card #${{currentIndex + 1}}`;
        itemBadgeFront.textContent = itemLabel;
        itemBadgeBack.textContent = itemLabel;
        
        counterText.textContent = `${{currentIndex + 1}} / ${{cards.length}}`;
        const progressPct = ((currentIndex + 1) / cards.length) * 100;
        progressBar.style.width = `${{progressPct}}%`;
    }}

    function flipCard() {{
        isFlipped = !isFlipped;
        flashcard.classList.toggle('flipped', isFlipped);
    }}

    function nextCard() {{
        if (cards.length === 0) return;
        currentIndex = (currentIndex + 1) % cards.length;
        updateCard();
    }}

    function prevCard() {{
        if (cards.length === 0) return;
        currentIndex = (currentIndex - 1 + cards.length) % cards.length;
        updateCard();
    }}

    function shuffleCards() {{
        for (let i = cards.length - 1; i > 0; i--) {{
            const j = Math.floor(Math.random() * (i + 1));
            [cards[i], cards[j]] = [cards[j], cards[i]];
        }}
        currentIndex = 0;
        updateCard();
    }}

    document.addEventListener('keydown', (e) => {{
        if (e.key === 'ArrowRight') nextCard();
        if (e.key === 'ArrowLeft') prevCard();
        if (e.key === ' ' || e.key === 'Enter') {{
            e.preventDefault();
            flipCard();
        }}
    }});

    updateCard();
</script>

</body>
</html>
"""

    with open(output_html, "w", encoding="utf-8") as f:
        f.write(html_content)

    print(f"Success! Generated '{output_html}'. Open this file in your web browser.")

if __name__ == "__main__":
    csv_file = sys.argv[1] if len(sys.argv) > 1 else "nursing_questions.csv"
    generate_flashcard_app(csv_file)