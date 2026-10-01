import os
from typing import List, Optional
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from ai_agent import CodingAgent
from github_service import GitHubService

load_dotenv()

app = FastAPI(
    title="Agente IA de Programación",
    description="API para analizar repositorios y obtener asistencia en código."
)

try:
    github_service = GitHubService()
    agent = CodingAgent()
except Exception as e:
    print(f"Advertencia: {e}. Configura tus variables de entorno.")

class AnalysisRequest(BaseModel):
    repo_name: str
    prompt: str
    target_files: Optional[List[str]] = None

@app.get("/")
def health_check():
    return {"status": "online", "message": "Agente de IA activo."}

@app.get("/repos")
def get_user_repos():
    try:
        return {"repositories": github_service.list_repositories()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/analyze")
def analyze_repo(request: AnalysisRequest):
    try:
        file_tree = github_service.get_repo_structure(request.repo_name)
        file_contents = {}
        files_to_read = request.target_files or [f for f in file_tree if f.endswith((".py", ".js", ".java", ".cpp", ".html"))][:5]
        
        for path in files_to_read:
            file_contents[path] = github_service.read_file_content(request.repo_name, path)
            
        answer = agent.analyze_repository(
            repo_name=request.repo_name,
            file_tree=file_tree,
            file_contents=file_contents,
            prompt=request.prompt,
        )
        return {"repo_name": request.repo_name, "files_analyzed": list(file_contents.keys()), "response": answer}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port)
