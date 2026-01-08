from vision_extractor import extract_tasks_from_image

def process_image(image_path: str) -> list[dict]:
    """
    Process image using LangChain + Gemini Vision
    
    Input: Image path
    Output: List of tasks
    """
    print(f" Processing image: {image_path}")
    try :
        tasks = extract_tasks_from_image(image_path)
        return tasks
    except Exception as e:
        print(f"error {e}")
        return []
