import os
import shutil
import json
import parserScript
import atsScriptApi

########### PARAMS ############

INPUT_DIR = atsScriptApi.load_config(entry="INPUT_DIR")
OUTPUT_DIR = "outputs"
OUTPUT_FILE = f"{OUTPUT_DIR}/scored_resumes.json"
FOR_REVIEW_DIR = f"{INPUT_DIR}/for_review"
FOR_REVIEW_FILE = f"{OUTPUT_DIR}/for_review.json"

###############################


def clear_output_folder(folder_path):
    print(f"Clearing old outputs from /{OUTPUT_DIR}")
    if os.path.exists(folder_path):
        for filename in os.listdir(folder_path):
            file_path = os.path.join(folder_path, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.remove(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print(f'Failed to delete {file_path}. Reason: {e}')
    else:
        print(f'The folder {folder_path} does not exist.')

def sort_resumes():
    print(f"Sorting resumes for review. They will be stored in {FOR_REVIEW_DIR}")
    with open(f'{OUTPUT_FILE}', 'r') as file:
        resume_data = json.load(file)
    
    if not os.path.exists(FOR_REVIEW_DIR):
        os.mkdir(FOR_REVIEW_DIR)

    sorted_resumes = []
    sorted_resumes_not_found = []

    for resume in resume_data:
        total_score = resume.get('purpose', 0) + resume.get('experience', 0) + resume.get('projects', 0) + resume.get('skills', 0)
        if total_score > 8:
            source_path = os.path.join(INPUT_DIR, resume['file_name'])
            destination_path = os.path.join(FOR_REVIEW_DIR, resume['file_name'])
            
            if os.path.exists(source_path):
                shutil.move(source_path, destination_path)
                print(f"Moved {resume['file_name']} to {FOR_REVIEW_DIR}")
                sorted_resumes.append(resume)
            else:
                print(f"File not found: {resume['file_name']}")
                sorted_resumes_not_found.append(resume)
                sorted_resumes.append(resume)

    
    with open(FOR_REVIEW_FILE, "w", encoding="utf-8") as file:
        json.dump(sorted_resumes, file, indent=4)
    with open(f"{OUTPUT_DIR}/for_review_not_found.json", "w", encoding="utf-8") as file:
        json.dump(sorted_resumes_not_found, file, indent=4)
    
    print(f"Sorted {len(sorted_resumes)} for review in {FOR_REVIEW_DIR}. {len(sorted_resumes_not_found)} resume(s) couldn't be found nor moved")

    return None


if __name__ == "__main__":
    clear_output_folder("outputs")
    parserScript.parse_resumes(INPUT_DIR)
    atsScriptApi.process_resumes(f"{OUTPUT_DIR}/parsed_resumes.json",OUTPUT_FILE)
    sort_resumes()


