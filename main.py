import os
import traceback
from typing import List, Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# Mantén tus importaciones originales de servicio
from agent_service import agent
from github_service import GitHubService

github_service = GitHubService()

app = FastAPI(
    title="Agente IA de Programación",
    description="API para analizar repositorios y obtener asistencia en código.",
    version="0.1.0"
)

class AnalysisRequest(BaseModel):
    repo_name: str
    prompt: str
    target_files: Optional[List[str]] = None

@app.get("/", name="Health Check")
def health_check():
    return {"status": "online", "message": "Agente de IA activo."}

@app.get("/repos", name="Get User Repos")
def get_user_repos():
    try:
        repos = github_service.get_user_repositories()
        return {"repositories": repos}
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"{type(e).__name__}: {e}")

@app.post("/analyze", name="Analyze Repo")
def analyze_repo(request: AnalysisRequest):
    try:
        file_tree = github_service.get_repo_structure(request.repo_name)
        file_contents = {}
        files_to_read = request.target_files or [
            f for f in file_tree if f.endswith((".py", ".js", ".java", ".cpp", ".html", ".md", ".json"))
        ][:5]

        for path in files_to_read:
            file_contents[path] = github_service.read_file_content(request.repo_name, path)

        answer = agent.analyze_repository(
            repo_name=request.repo_name,
            file_tree=file_tree,
            file_contents=file_contents,
            prompt=request.prompt,
        )
        
        return {
            "repo_name": request.repo_name,
            "files_analyzed": list(file_contents.keys()),
            "analysis": answer,  # Sincronizado con bot.py
        }
    except Exception as e:
        traceback.print_exc()  # Imprime el traceback exacto en los logs de Render
        raise HTTPException(status_code=500, detail=f"{type(e).__name__}: {e}")