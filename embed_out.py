from sentence_transformers import SentenceTransformer
import faiss
import numpy as np

model = SentenceTransformer("all-MiniLM-L6-v2")

level_score_map = {
    "advanced": 1.0,
    "medium": 0.6,
    "low": 0.2
}

def build_faiss_index(text_list):
    embeddings = model.encode(text_list)
    embeddings = np.array(embeddings).astype("float32")

    faiss.normalize_L2(embeddings)
    dimension = embeddings.shape[1]

    index = faiss.IndexFlatIP(dimension)
    index.add(embeddings)

    return index, text_list


def search_faiss(query, index, text_list):
    query_embedding = model.encode([query]).astype("float32")
    faiss.normalize_L2(query_embedding)

    scores, indices = index.search(query_embedding, k=1)

    best_match = text_list[indices[0][0]]
    score = scores[0][0]  

    return best_match, score


def get_level(score):
    if score > 0.75:
        return "advanced"
    elif score > 0.5:
        return "medium"
    else:
        return "low"


def prepare_jd_indexes(jd_json):
    required_skills = jd_json.get("required_skills") or []
    preferred_skills = jd_json.get("preferred_skills") or []

    jd_skills = required_skills + preferred_skills

    jd_exp = [jd_json.get("experience_level")] if jd_json.get("experience_level") else []
    jd_edu = [jd_json.get("education_eligibility")] if jd_json.get("education_eligibility") else []

    skill_index, skill_texts = build_faiss_index(jd_skills) if jd_skills else (None, [])
    exp_index, exp_texts = build_faiss_index(jd_exp) if jd_exp else (None, [])
    edu_index, edu_texts = build_faiss_index(jd_edu) if jd_edu else (None, [])

    return {
        "skills": (skill_index, skill_texts),
        "experience": (exp_index, exp_texts),
        "education": (edu_index, edu_texts)
    }

def match_skills(resume_json, jd_indexes):
    index, texts = jd_indexes["skills"]
    results = []

    if index is None:
        return results

    resume_skills = [
        (s.get("name", "").lower().strip(), s.get("evidence", ""))
        for s in resume_json.get("skills", [])
    ]

    if not resume_skills:
        for jd_skill in texts:
            results.append({
                "skill": jd_skill,
                "matched_with": None,
                "level": "low",
                "evidence": "Not found"
            })
        return results

    resume_names = [s[0] for s in resume_skills]
    resume_index, resume_texts = build_faiss_index(resume_names)

    for jd_skill in texts:
        match, score = search_faiss(jd_skill, resume_index, resume_texts)

        evidence = next(
            (ev for name, ev in resume_skills if name == match),
            ""
        )

        results.append({
            "skill": jd_skill,
            "matched_with": match,
            "level": get_level(score),
            "score": float(score),
            "evidence": evidence or "Weak / inferred"
        })

    return results


def match_experience(resume_json, jd_indexes):
    index, texts = jd_indexes["experience"]
    results = []

    if index is None:
        return results

    resume_exp = [
        (
            f"{exp.get('role', '')} {exp.get('duration_years', '')} years",
            exp.get("evidence", "")
        )
        for exp in resume_json.get("experience", [])
    ]

    if not resume_exp:
        for jd_exp in texts:
            results.append({
                "requirement": jd_exp,
                "matched_with": None,
                "level": "low",
                "evidence": "Not found"
            })
        return results

    resume_texts_only = [e[0] for e in resume_exp]
    resume_index, _ = build_faiss_index(resume_texts_only)

    for jd_exp in texts:
        match, score = search_faiss(jd_exp, resume_index, resume_texts_only)

        evidence = next(
            (ev for txt, ev in resume_exp if txt == match),
            ""
        )

        results.append({
            "requirement": jd_exp,
            "matched_with": match,
            "level": get_level(score),
            "score": float(score),
            "evidence": evidence or "Weak / inferred"
        })

    return results


def match_education(resume_json, jd_indexes):
    index, texts = jd_indexes["education"]
    results = []

    if index is None:
        return results

    resume_edu = [
        (
            f"{edu.get('degree', '')} {edu.get('field', '')}",
            edu.get("evidence", "")
        )
        for edu in resume_json.get("education", [])
    ]

    if not resume_edu:
        for jd_edu in texts:
            results.append({
                "requirement": jd_edu,
                "matched_with": None,
                "level": "low",
                "evidence": "Not found"
            })
        return results

    resume_texts_only = [e[0] for e in resume_edu]
    resume_index, _ = build_faiss_index(resume_texts_only)

    for jd_edu in texts:
        match, score = search_faiss(jd_edu, resume_index, resume_texts_only)

        evidence = next(
            (ev for txt, ev in resume_edu if txt == match),
            ""
        )

        results.append({
            "requirement": jd_edu,
            "matched_with": match,
            "level": get_level(score),
            "score": float(score),
            "evidence": evidence or "Weak / inferred"
        })

    return results

def compute_category_score(matches):
    if not matches:
        return None 

    total = 0
    count = 0

    for item in matches:
        level = item.get("level", "low")

        if level in ["advanced", "medium"]:
            total += level_score_map.get(level, 0)
            count += 1

    if count == 0:
        return 0.0 
    return total / count


def compute_final_score(final_json):
    skills_score = compute_category_score(final_json.get("skills", []))
    exp_score = compute_category_score(final_json.get("experience", []))
    edu_score = compute_category_score(final_json.get("education", []))

    total_weight = 0.0
    final_score = 0.0

    if skills_score is not None:
        final_score += 0.5 * skills_score
        total_weight += 0.5
        
    if exp_score is not None:
        final_score += 0.3 * exp_score
        total_weight += 0.3
        
    if edu_score is not None:
        final_score += 0.2 * edu_score
        total_weight += 0.2

    if total_weight == 0.0:
        return 0.0

    base_percentage = (final_score / total_weight) * 100

    missed_count = 0
    missed_count += sum(1 for s in final_json.get("skills", []) if s.get("level") == "low")
    missed_count += sum(1 for e in final_json.get("experience", []) if e.get("level") == "low")
    missed_count += sum(1 for ed in final_json.get("education", []) if ed.get("level") == "low")

    penalty_per_miss = 1.5 
    total_penalty = missed_count * penalty_per_miss
    
    total_penalty = min(total_penalty, 15.0)
    final_percentage = max(base_percentage - total_penalty, 0.0)
    return round(final_percentage, 2)

def run_matching_pipeline(jd_json, resume_json):
    jd_indexes = prepare_jd_indexes(jd_json)

    final_output = {
        "skills": match_skills(resume_json, jd_indexes),
        "experience": match_experience(resume_json, jd_indexes),
        "education": match_education(resume_json, jd_indexes)
    }

    final_output["final_score"] = compute_final_score(final_output)

    return final_output