import os
from github import Github, GithubException

class GitHubService:
    def __init__(self, token: str = None):
        self.token = token or os.getenv("GITHUB_TOKEN")
        if not self.token:
            raise ValueError("GITHUB_TOKEN no está configurado en las variables de entorno.")
        self.gh = Github(self.token)

    def list_repositories(self):
        user = self.gh.get_user()
        return [{"name": repo.name, "full_name": repo.full_name, "private": repo.private} for repo in user.get_repos()]

    def get_repo_structure(self, repo_name: str, path: str = "") -> list:
        user = self.gh.get_user()
        repo = user.get_repo(repo_name)
        contents = repo.get_contents(path)
        ignored_dirs = {"node_modules", ".git", "venv", "__pycache__", "dist", "build"}
        file_tree = []
        while contents:
            file_content = contents.pop(0)
            if file_content.type == "dir" and file_content.name not in ignored_dirs:
                contents.extend(repo.get_contents(file_content.path))
            elif file_content.type == "file":
                file_tree.append(file_content.path)
        return file_tree

    def read_file_content(self, repo_name: str, file_path: str) -> str:
        user = self.gh.get_user()
        repo = user.get_repo(repo_name)
        try:
            file_content = repo.get_contents(file_path)
            return file_content.decoded_content.decode("utf-8")
        except Exception as e:
            return f"Error al leer el archivo {file_path}: {str(e)}"
