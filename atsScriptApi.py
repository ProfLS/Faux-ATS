import openai
import json
import yaml
from pydantic import BaseModel, Field
from typing import List
import time


# Load API Key from YAML file
def load_api_key(filepath="private_properties.yaml"):
    with open(filepath, "r") as file:
        config = yaml.safe_load(file)
    return config.get("API_KEY")


# Define Pydantic Model for Resume Scores
class ResumeScore(BaseModel):
    file_name: str
    purpose: int = Field(..., ge=0, le=8)
    experience: int = Field(..., ge=0, le=8)
    projects: int = Field(..., ge=0, le=8)
    skills: int = Field(..., ge=0, le=8)


# Define Function to Call OpenAI API
def get_resume_scores(resume):
    prompt = f"""
    Evaluate the following resume sections on a scale of 0-8 based on their quality, relevance, and impact:
    
    Resume:
    - File Name: {resume['file_name']}
    - Purpose: {resume.get('purpose', '')}
    - Experience: {resume.get('experience', '')}
    - Projects: {resume.get('projects', '')}
    - Skills: {resume.get('skills', '')}
    
    Return a JSON object in this format:
    {{
      "file_name": "{resume['file_name']}",
      "purpose": <integer between 0-8>,
      "experience": <integer between 0-8>,
      "projects": <integer between 0-8>,
      "skills": <integer between 0-8>
    }}
    """

    response = openai.ChatCompletion.create(
        model="gpt-4-turbo",
        messages=[{"role": "system", "content": "You are an AI assistant that evaluates resumes based on given criteria."},
                  {"role": "user", "content": prompt}],
        temperature=0.2
    )

    json_response = json.loads(response["choices"][0]["message"]["content"])
    
    # Validate response using Pydantic
    return ResumeScore(**json_response).dict()


# Main function to process resumes
def process_resumes(input_json, output_json="resume_scores.json"):
    with open(input_json, "r") as file:
        resumes = json.load(file)

    api_key = load_api_key()
    openai.api_key = api_key

    scored_resumes = []

    for resume in resumes:
        try:
            print(f"Processing: {resume['file_name']}")
            score = get_resume_scores(resume)
            scored_resumes.append(score)
        except Exception as e:
            print(f"Error processing {resume['file_name']}: {str(e)}")
        time.sleep(1)  # Rate limiting buffer

    with open(output_json, "w") as file:
        json.dump(scored_resumes, file, indent=4)

    print(f"Scoring complete. Results saved to {output_json}")


if __name__ == "__main__":
    process_resumes("parsed_resumes.json") 
