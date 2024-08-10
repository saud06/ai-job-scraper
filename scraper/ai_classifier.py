import os
import re
import time
import json
from typing import Dict, List, Tuple

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")  # Optional fallback

# -------------------------
# Skill patterns & roles
# -------------------------
SKILL_PATTERNS = {
    "Python": r"\bpython\b",
    "JavaScript": r"\bjavascript\b|\bjs\b",
    "TypeScript": r"\btypescript\b|\bts\b",
    "React": r"\breact(\.js)?\b",
    "Node.js": r"\bnode(\.js)?\b",
    "Vue": r"\bvue(\.js)?\b",
    "Django": r"\bdjango\b",
    "Flask": r"\bflask\b",
    "Laravel": r"\blaravel\b",
    "Docker": r"\bdocker\b",
    "Kubernetes": r"\bkubernetes\b|\bk8s\b",
    "SQL": r"\bsql\b|\bpostgres\b|\bmysql\b",
    "NoSQL": r"\bnosql\b|\bmongodb\b|\bredis\b",
    "CI/CD": r"\bci/cd\b|\bci\b\s*/\s*\bcd\b|\bjenkins\b|\bgithub actions\b|\bazure devops\b",
    "Azure": r"\bazure\b",
    "AWS": r"\baws\b|\bamazon web services\b",
    "GCP": r"\bgcp\b|\bgoogle cloud\b",
    "Machine Learning": r"\bmachine learning\b|\bml\b|\bpytorch\b|\btensorflow\b|\bscikit-learn\b",
    "Data Engineering": r"\bdata (engineer|engineering)\b|\bspark\b|\bhadoop\b|\bairflow\b",
}

ROLE_LABELS = ["Backend", "Frontend", "Full-Stack", "Data/ML", "DevOps", "Other"]

# -------------------------
# Skill extraction
# -------------------------
def extract_skills(text: str) -> List[str]:
    text_low = text.lower()
    found = []
    for skill, pattern in SKILL_PATTERNS.items():
        if re.search(pattern, text_low):
            found.append(skill)
    return sorted(set(found))

# -------------------------
# Rule-based classification
# -------------------------
def classify_role_rule_based(text: str) -> Tuple[str, str]:
    skills = extract_skills(text)
    reason = []
    label = "Other"
    if "Machine Learning" in skills:
        label = "Data/ML"; reason.append("mentions ML/AI tools or keywords")
    if "Docker" in skills and ("AWS" in skills or "Azure" in skills or "GCP" in skills):
        label = "DevOps"; reason.append("mentions Docker and cloud provider")
    if "React" in skills or "Vue" in skills:
        label = "Frontend"; reason.append("mentions React/Vue")
    if ("Node.js" in skills or "Django" in skills or "Flask" in skills or "Laravel" in skills) and ("React" in skills or "Vue" in skills):
        label = "Full-Stack"; reason.append("mentions backend + frontend stack")
    if label == "Other" and any(s in skills for s in ["Django", "Flask", "Laravel", "Node.js", "SQL", "NoSQL"]):
        label = "Backend"; reason.append("mentions backend frameworks/databases")
    if not reason:
        reason.append("fallback default")
    return label, "; ".join(reason)

# -------------------------
# AI-based classification (OpenAI v1.0+)
# -------------------------
def classify_role_ai(text: str, retries: int = 3) -> Tuple[str, str]:
    """
    Classify a job description using OpenAI Responses API.
    Returns: (role, reasoning)
    Falls back to rule-based if API key missing or error occurs.
    """
    if OPENAI_API_KEY:
        import openai
        openai.api_key = OPENAI_API_KEY

        prompt = (
            "You are a job classification assistant.\n"
            "Classify the following job description into one of: "
            f"{', '.join(ROLE_LABELS)}. "
            "Then list 5 key skills in JSON format like:\n"
            '{"role": "Data/ML", "skills": ["Python", "Pandas", "SQL", "ML", "TensorFlow"]}\n\n'
            f"Job Description:\n{text[:6000]}"
        )

        for attempt in range(retries):
            try:
                response = openai.responses.create(
                    model="gpt-3.5-turbo",
                    input=prompt,
                    temperature=0
                )

                reply = response.output_text.strip()

                # Parse JSON from AI
                data = json.loads(reply)
                role = data.get("role", "Other")
                skills = data.get("skills", [])
                reason = f"AI-classified with OpenAI: {', '.join(skills[:5])}"
                return role, reason

            except json.JSONDecodeError:
                print(f"OpenAI response JSON decode error, falling back to rule-based.")
                return classify_role_rule_based(text)
            except Exception as e:
                print(f"OpenAI classify error (attempt {attempt+1}): {e}")
                time.sleep(2)

    # fallback to rule-based
    return classify_role_rule_based(text)

# -------------------------
# Annotate a single job
# -------------------------
def annotate_job(job: Dict) -> Dict:
    """
    Adds AI classification and skill tags to a job dict.
    Uses caching: skips AI if job already has ai_class/ai_reasoning.
    """
    if job.get("ai_class") and job.get("ai_reasoning"):
        return job  # already classified

    text = " ".join([job.get("title") or "", job.get("description") or ""])
    label, why = classify_role_ai(text)
    skills = extract_skills(text)

    job["ai_class"] = label
    job["ai_reasoning"] = why
    job["tags"] = skills

    print(f"Annotated job: {job.get('title')} | Role: {label} | Skills: {skills[:5]}")
    return job
