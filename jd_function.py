import json
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
import os
from dotenv import load_dotenv

load_dotenv()
SYSTEM_PROMPT = """You are a strict job description parser. Output ONLY valid JSON. Never infer, guess, assume or add anything.

{{
  "required_skills": ["skill1", "skill2"] or null,
  "preferred_skills": ["skill1"] or null,
  "experience_level": "exact text" or null,
  "education_eligibility": "exact text" or null
}}

Rules (follow exactly):
- Skills must be short clean phrases (max 5 words). Split comma lists into separate items.
- Never copy full sentences or bullet points.
- If a field is not explicitly stated → return null.
- Copy wording 100% exactly.
- No other text in the response.
"""

def call_llama_70b(api_key: str, job_description: str):
    llm = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0,
        api_key=api_key
    )

    prompt = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT),
        ("human", "{job_description}")
    ])

    chain = prompt | llm

    response = chain.invoke({
        "job_description": job_description
    })

    return response.content

if __name__ == "__main__":
    api_key = os.getenv("OPENAI_API_KEY")

    sample_jd = "We are seeking a Python developer with experience in REST APIs, Machine Learning, and SQL. Required skills: Python, FastAPI, SQL. Preferred: Docker, AWS."
    result = call_llama_70b(api_key, sample_jd)
    print("Extracted result:\n")
    print(result)