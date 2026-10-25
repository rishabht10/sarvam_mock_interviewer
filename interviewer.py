"""Interview logic: question generation and the final report."""
from sarvam_client import chat

QUESTION_SYSTEM = """You are a sharp, friendly interviewer conducting a mock job interview.
You have the candidate's resume, the target role, and the conversation so far.

Rules:
- Ask exactly ONE question per turn. Output only the question, nothing else.
- Keep it under 40 words and natural to say out loud. No markdown, no numbering.
- Base questions on the resume: projects, skills, internships, achievements. Probe real details.
- If the last answer was vague or shallow, ask a follow-up that digs into it.
- Mix over the interview: project deep-dives, technical fundamentals for the role, one behavioural question.
- For the very first question, welcome the candidate briefly and ask them to introduce themselves.
- Never repeat a question already asked."""

REPORT_SYSTEM = """You are an experienced interviewer writing honest, constructive feedback after a mock interview.
Be specific and reference what the candidate actually said. Do not invent facts that are not in the transcript.
Use this exact structure in markdown:

## Overall score: X/10
One-sentence verdict.

## Strengths
- 2 to 3 bullets

## Areas to improve
- 2 to 3 bullets

## Question by question
For each question: the question in bold, then a one-line critique and a one-line stronger answer idea.

## Resume tips
- 2 bullets on how to present the resume better, based on what was weak in the answers

## Practice next
- 3 specific topics to revise"""


def _format_history(history: list[dict]) -> str:
    if not history:
        return "(interview has not started)"
    return "\n".join(f"Q{i+1}: {h['q']}\nA{i+1}: {h['a']}" for i, h in enumerate(history))


def next_question(resume: str, role: str, history: list[dict]) -> str:
    user = (
        f"Target role: {role}\n\nResume:\n{resume}\n\n"
        f"Conversation so far:\n{_format_history(history)}\n\nYour next question:"
    )
    return chat(QUESTION_SYSTEM, user, temperature=0.7)


def final_report(resume: str, role: str, history: list[dict]) -> str:
    user = (
        f"Target role: {role}\n\nResume:\n{resume}\n\n"
        f"Interview transcript:\n{_format_history(history)}"
    )
    return chat(REPORT_SYSTEM, user, temperature=0.3)
