import os
import json
from dotenv import load_dotenv
from extract_text import extract_and_clean
from jd_function import call_llama_70b as extract_jd_data
from resume_function import call_llama_70b as extract_resume_data
from embed_out import run_matching_pipeline

def main():
    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("Error: OPENAI_API_KEY missing in your environment/ .env file.")
        return

    pdf_path = "./resume/1.pdf"
    print(f"Step 1: Extracting text from {pdf_path}...")
    try:
        extracted_text = extract_and_clean(pdf_path)
    except Exception as e:
        print(f"Failed to extract text: {e}")
        return

    print("Step 2: Parsing Resume text via LLM...")
    resume_string_output = extract_resume_data(api_key, extracted_text)

    job_description = """We are actively seeking a results-driven product leader for our core data team. Experience level: Senior AI Product Manager with 6 years experience. Required skills: LLMs, RAG, Prompt Engineering, Python, SQL, A/B Testing. Preferred skills: LangChain, LlamaIndex, GCP, AWS, OKRs. Education eligibility: B.Tech in Computer Science & Engineering. The ideal candidate will have a proven track record of launching and scaling AI-powered products, driving user engagement, and implementing responsible AI frameworks."""
    print("Step 3: Parsing Job Description via LLM...")
    jd_string_output = extract_jd_data(api_key, job_description)

    print("Step 4: Converting outputs to JSON...")
    try:
        jd_json = json.loads(jd_string_output)
        resume_json = json.loads(resume_string_output)
    except json.JSONDecodeError as e:
        print(f"Error: The LLM did not return valid JSON. {e}")
        return

    print("Step 5: Running FAISS matching pipeline...")
    final_result = run_matching_pipeline(jd_json, resume_json)

    print("\n" + "="*40)
    print("FINAL MATCHING RESULT")
    print("="*40)
    print(json.dumps(final_result, indent=4))

if __name__ == "__main__":
    main()