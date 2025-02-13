import json
import yaml
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.runnables import RunnableLambda
from langchain_core.runnables.base import RunnableEach
from pydantic import BaseModel, Field
from typing import List, Optional
from pydantic.dataclasses import *
from pydantic import BaseModel, Field
from typing import List
import time
import os

give_explanation = True

# Init ChatGPT API
def load_api_key(filepath="private_properties.yaml"):
    with open(filepath, "r") as file:
        config = yaml.safe_load(file)
    return config.get("API_KEY")

if "OPENAI_API_KEY" not in os.environ:
    os.environ["OPENAI_API_KEY"] = load_api_key()

ats = ChatOpenAI(
    model="gpt-4o",
    temperature=0.2
)

# Prompt & Formatting

if give_explanation:
    class ResumeScore(BaseModel):
        file_name: str = Field(..., description="The file name")
        explanation: str = Field(..., description="Explain the rationale for all the scores given for each section in depth")
        purpose: int = Field(..., ge=0, le=8, description="Score for the purpose section (0-8)")
        experience: int = Field(..., ge=0, le=8, description="Score for the experience section (0-8)")
        projects: int = Field(..., ge=0, le=8, description="Score for the projects section (0-8)")
        skills: int = Field(..., ge=0, le=8, description="Score for the skills section (0-8)")
else:
    class ResumeScore(BaseModel):
        file_name: str = Field(..., description="The file name")
        purpose: int = Field(..., ge=0, le=8, description="Score for the purpose section (0-8)")
        experience: int = Field(..., ge=0, le=8, description="Score for the experience section (0-8)")
        projects: int = Field(..., ge=0, le=8, description="Score for the projects section (0-8)")
        skills: int = Field(..., ge=0, le=8, description="Score for the skills section (0-8)")

parser = JsonOutputParser(pydantic_object=ResumeScore)

format_instructions = parser.get_format_instructions()

template = """
    You are an application programming interface designed to strictly evaluate and rank resumes for the LinkedIn Campus Ambassador Program.  Your sole job is to objectively assess each candidate’s qualifications based on predefined criteria and generate structured feedback. 


    Role Overview;


    Ambassadors will act as the bridge between students and LinkedIn, promoting brand awareness and empowering their peers to grow professionally. This includes creating partnerships with student organizations, hosting events, and promoting educational opportunities through LinkedIn Learning to empower students with their career development.


    Application Resource:

    As an ambassador, you’ll:

    Promote LinkedIn’s value in career growth and professional networking.
    Lead impactful events and workshops to empower students with essential skills.
    Build partnerships and inspire others to unlock the potential of LinkedIn Learning.

    Key responsibilities: 

    Provide guidance to students on optimizing their use of LinkedIn for professional growth. 
    Educate students on using LinkedIn tools more effectively to support their job search journey.  
    Teach students how to navigate LinkedIn Learning and find the courses that best align with their goals.  
    Develop marketing content for events, meetings, live interviews, and related initiatives.
    Establish partnerships with student organizations or external groups to co-host events.
    Design and deliver training sessions on LinkedIn products, customized to specific topics or audience needs.
    Work with project leads to ensure successful event execution.


    Pillars of the program:


    Communication
    Able to convey ideas professionally
    Able to connect with the student population 
    Professionalism
    Take accountability for actions
    Treat others with utmost respect
    Motivation
    Want to increase skill set
    Provide opportunities for others 
    Creativity 
    Display critical thinking skills
    Provide solutions for challenges 
    Engages audience effectively 
    Skills:
    Strong interpersonal, communication, and organizational skills. 
    Ability to work cross-functionally and manage time effectively. 
    Self-motivated, goal-oriented, and willing to learn. 

    Explicit commands:

    Search for keywords such as

    “Ambassador” 
    “Leader” 
    “President” 
    “Captain”
    “Vice President” 
    “Director”
    “Manager” 
    “Treasurer” 
    “Secretary” 
    “Content Creation” 

    ### **Evaluation Criteria**
    **Leadership & Initiative (0-8 Points)**
    - Leadership roles: President, VP, Captain, Lead.
    - Experience in student organizations, mentoring, or managing projects.
    - Proactive engagement in academic/professional settings.

    **Content Creation & Marketing (0-8 Points)**
    - Social media management, branding, or event promotion.
    - Experience creating marketing materials (flyers, videos, instagram posts).
    - Community engagement and digital presence.

    **Ambassador & Outreach Experience (0-8 Points)**
    - Experience as a campus ambassador, brand representative, or event coordinator.
    - Strong communication and public speaking skills.
    - Organized or participated in events, workshops, or networking initiatives.

    Generate a short checklist summary of what criterion the applicant “ticked off”

    Point System

    Leadership (0-8 points)
    Content creation (0-8 points)
    Ambassador experience (0-8 points)
    Assign a Point Score (Max 24 Points)

    {format_instructions}

    % USER INPUT:
    
    File Name: {file_name}
    Purpose: {purpose}
    Experience: {experience}
    Projects: {projects}
    Skills: {skills}

"""

score_prompt_template = PromptTemplate(
    input_variables=["file_name","purpose","experience","projects","skills"],
    partial_variables={"format_instructions": format_instructions},
    template=template
    )

chain = score_prompt_template | ats | parser

def scorecard(resume):
    default_values = {
        "purpose": "N/a",
        "experience": "N/a",
        "projects": "N/a",
        "skills": "N/a"
    }

    input_data = {key: resume.get(key, default) for key, default in default_values.items()}
    input_data["file_name"] = resume.get("file_name", "Unknown")

    response = chain.invoke(input_data)

    return response

def process_resumes(input_json, output_json="scored_resumes.json"):
    with open(input_json, "r", encoding="utf-8") as file:
        resumes = json.load(file)

    scored_resumes = []

    for resume in resumes:
        try:
            print(f"Processing: {resume['file_name']}")
            score = scorecard(resume)
            scored_resumes.append(score)
        except Exception as e:
            print(f"Error processing {resume['file_name']}: {str(e)}")
        
        time.sleep(0.35)  # Rate limiting buffer

    with open(output_json, "w", encoding="utf-8") as file:
        json.dump(scored_resumes, file, indent=4)

    print(f"Completed scoring. Saved output to: {output_json}")

if __name__ == "__main__":
    process_resumes("parsed_resumes.json")
