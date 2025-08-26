
from datetime import datetime
from typing import List, Dict, Any, Tuple
import gradio as gr
import pandas as pd
import os

# -----------------------------
# Core logic
# -----------------------------

def _bucket(score: int) -> str:
    """Map score to discrete personalization buckets."""
    if score >= 100:
        return "100+"
    elif score >= 90:
        return "90-99"
    elif score >= 80:
        return "80-89"
    else:
        return "<80"

def _plan_by_bucket(bucket: str) -> Dict[str, Any]:
    """Return a weekly plan template and daily tasks based on score bucket."""
    # High-level weekly focus per bucket (generic, source-agnostic best practices)
    weekly_focus = {
        "100+": [
            "Full-length mock tests (timed) 2x/week",
            "Speaking drills with recording & self-review",
            "Advanced academic vocabulary consolidation",
            "Refine Writing Task 1/2 structures under time"
        ],
        "90-99": [
            "Targeted Reading strategy practice (skimming/scanning)",
            "Daily Speaking prompts with 60-sec responses",
            "Listening note-taking for lectures & conversations",
            "Writing with clear thesis + example paragraphs"
        ],
        "80-89": [
            "Grammar refreshers on common TOEFL errors",
            "Reading: paragraph main idea & inference practice",
            "Listening: short dialogues & key-point capture",
            "Speaking: 3-sentence structured responses"
        ],
        "<80": [
            "Understand TOEFL format & scoring basics",
            "Foundation vocabulary (15/day) with spaced review",
            "Short listening clips with transcript support",
            "Simple paragraph writing & feedback checklist"
        ],
    }

    # 7-day daily tasks template
    daily_templates = {
        "100+": [
            "Reading: 1 long passage (timed) + error log",
            "Listening: 1 lecture + 1 conversation (timed)",
            "Speaking: 2 prompts (record, self-critique)",
            "Writing: Task 2 essay (25 min) outline + body",
            "Vocabulary: 20 academic words + retrieval practice",
            "Mock: mini test (Reading+Listening) (timed)",
            "Review: wrong answers & patterns; light speaking"
        ],
        "90-99": [
            "Reading: main idea & inference (1 passage)",
            "Listening: note-taking practice (1 lecture)",
            "Speaking: 1 independent prompt (record)",
            "Writing: intro+thesis+1 example paragraph",
            "Vocabulary: 15 words; quiz yourself",
            "Mock: section mix (30–45 min)",
            "Review & plan next week"
        ],
        "80-89": [
            "Grammar set: tenses, subject-verb agreement",
            "Reading: 1 short passage (slow + annotate)",
            "Listening: 1 short convo (pause & repeat)",
            "Speaking: 3-sentence prompt (intro-reason-example)",
            "Writing: short paragraph (topic, support, concluding)",
            "Vocabulary: 12 words; flashcards",
            "Weekly review: error list update"
        ],
        "<80": [
            "Learn test sections & timing basics",
            "Vocabulary: 15 everyday words + examples",
            "Listening: short clip + read transcript",
            "Reading: 1 short text; underline keywords",
            "Speaking: describe a picture (30s)",
            "Writing: 5-sentence paragraph (topic/support)",
            "Review & light mock (un-timed)"
        ],
    }

    return {
        "weekly_focus": weekly_focus[bucket],
        "daily": daily_templates[bucket]
    }

def generate_plan(score_input: str, focus_area: str = "Balanced") -> str:
    """Generate a personalized 7-day plan based on target score and optional focus area."""
    # Validate numeric score
    try:
        score = int(score_input)
    except Exception:
        return "Please enter your target score as a number (e.g., 90)."

    b = _bucket(score)
    plan = _plan_by_bucket(b)

    # Lightweight focus tweak
    adjustments = {
        "Balanced": "",
        "Reading": " Emphasize Reading tasks; add 5–10 extra minutes to reading activities.",
        "Listening": " Emphasize Listening tasks; repeat audio segments once for deeper note-taking.",
        "Speaking": " Emphasize Speaking tasks; add one extra speaking prompt on Days 3 & 7.",
        "Writing": " Emphasize Writing tasks; add a 10-minute outline drill on Days 4 & 5.",
        "Vocabulary": " Emphasize Vocabulary; add spaced-recall mini-quizzes daily."
    }

    header = [
        f"🎯 Target Score: {score}  (Bucket: {b})",
        f"🧭 Focus: {focus_area}",
        "📅 Weekly Focus:"
    ]
    weekly_lines = [f"- {item}" for item in plan["weekly_focus"]]

    days = []
    for idx, task in enumerate(plan["daily"], start=1):
        tweak = adjustments.get(focus_area, "")
        days.append(f"Day {idx}: {task}{tweak}")

    out = "\n".join(header + weekly_lines + ["", "🗓️ 7-Day Plan:"] + days)
    return out

# -----------------------------
# Success criteria self-tests
# -----------------------------

def run_self_tests() -> str:
    """
    Run simple checks that correspond to success criteria:
    1) Functionality: returns a plan for valid numeric inputs
    2) Personalization: different scores yield different buckets and different plans
    3) Robustness: handles non-numeric input with a clear message
    4) Consistency: daily plan has 7 days
    5) Basic usability: response is non-empty and contains key headers
    """
    logs = []
    passed = True

    # 1) Functionality
    for s in [75, 85, 92, 104]:
        txt = generate_plan(str(s))
        ok = ("7-Day Plan" in txt) and ("Target Score" in txt)
        logs.append(f"[Functionality] score={s}: {'PASS' if ok else 'FAIL'}")
        passed = passed and ok

    # 2) Personalization
    a = generate_plan("82")
    b = generate_plan("95")
    c = generate_plan("105")
    pers_ok = ("Bucket: 80-89" in a) and ("Bucket: 90-99" in b) and ("Bucket: 100+" in c)
    logs.append(f"[Personalization] different buckets detected: {'PASS' if pers_ok else 'FAIL'}")
    passed = passed and pers_ok

    # 3) Robustness
    r = generate_plan("ninety")
    robust_ok = "Please enter your target score as a number" in r
    logs.append(f"[Robustness] non-numeric input message: {'PASS' if robust_ok else 'FAIL'}")
    passed = passed and robust_ok

    # 4) Consistency: count 7 days
    sample = generate_plan("90")
    days_ok = all(f"Day {i}:" in sample for i in range(1, 8))
    logs.append(f"[Consistency] 7 days present: {'PASS' if days_ok else 'FAIL'}")
    passed = passed and days_ok

    # 5) Basic usability: contains headers
    head_ok = ("Weekly Focus:" in sample) and ("Target Score" in sample) and ("Focus:" in sample)
    logs.append(f"[Usability] headers included: {'PASS' if head_ok else 'FAIL'}")
    passed = passed and head_ok

    summary = "OVERALL: PASS ✅" if passed else "OVERALL: CHECK NEEDED ⚠️"
    return summary + "\n" + "\n".join(logs)

# -----------------------------
# Feedback logging
# -----------------------------

FEEDBACK_PATH = "feedback.csv"

def save_feedback(score: str, helpful: int, clarity: int, comments: str) -> str:
    """Append user feedback to CSV."""
    row = {
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "target_score_input": score,
        "helpful_rating_1to5": helpful,
        "clarity_rating_1to5": clarity,
        "comments": comments.strip()
    }
    df = pd.DataFrame([row])
    if os.path.exists(FEEDBACK_PATH):
        df.to_csv(FEEDBACK_PATH, mode="a", header=False, index=False)
    else:
        df.to_csv(FEEDBACK_PATH, index=False)
    return "Thanks! Your feedback was saved."

# -----------------------------
# Gradio UI
# -----------------------------

with gr.Blocks(title="TOEFL Study Coach") as demo:
    gr.Markdown("# 🧠 TOEFL Study Coach\nGet a 7-day study plan tailored to your target score.")

    with gr.Tab("Get My Plan"):
        score_in = gr.Textbox(label="Enter your target TOEFL score (e.g., 90)")
        focus_in = gr.Dropdown(
            label="Pick an optional focus area",
            choices=["Balanced", "Reading", "Listening", "Speaking", "Writing", "Vocabulary"],
            value="Balanced"
        )
        btn = gr.Button("Generate My 7-Day Plan")
        plan_out = gr.Textbox(label="Your Personalized Plan", lines=22)
        btn.click(fn=generate_plan, inputs=[score_in, focus_in], outputs=plan_out)

    with gr.Tab("Run Success Tests"):
        test_btn = gr.Button("Run Self-Tests")
        test_out = gr.Textbox(label="Test Results", lines=12)
        test_btn.click(fn=run_self_tests, inputs=None, outputs=test_out)

    with gr.Tab("Feedback"):
        gr.Markdown("Help improve the tool by rating your experience.")
        fb_score = gr.Textbox(label="(Optional) Your target score input")
        fb_helpful = gr.Slider(1, 5, step=1, value=5, label="How helpful was the plan? (1–5)")
        fb_clarity = gr.Slider(1, 5, step=1, value=5, label="How clear was the plan? (1–5)")
        fb_comments = gr.Textbox(label="Comments / Suggestions", lines=3, placeholder="What should be improved?")
        fb_btn = gr.Button("Submit Feedback")
        fb_status = gr.Textbox(label="Status", interactive=False)
        fb_btn.click(fn=save_feedback, inputs=[fb_score, fb_helpful, fb_clarity, fb_comments], outputs=fb_status)

    gr.Markdown("> Tip: Use the **Run Success Tests** tab to check if the app meets basic success criteria (functionality, personalization, robustness, consistency, usability).")

if __name__ == "__main__":
    demo.launch('share=True')