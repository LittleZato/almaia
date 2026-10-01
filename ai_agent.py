import os
from google import genai

class CodingAgent:
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY no está configurada en las variables de entorno.")
        self.client = genai.Client(api_key=self.api_key)
        self.model_name = "gemini-2.5-flash"

    def analyze_repository(self, repo_name: str, file_tree: list, file_contents: dict, prompt: str) -> str:
        context = f"### Repositorio: {repo_name}\n\n### Estructura del Proyecto:\n"
        context += "\n".join([f"- {path}" for path in file_tree]) + "\n\n"
        context += "### Archivos analizados:\n"
        for path, content in file_contents.items():
            context += f"--- Archivo: {path} ---\n{content}\n\n"
        
        system_instruction = (
            "Eres un tutor y agente asistente senior de programación especializado en ingeniería en informática. "
            "Tu objetivo es ayudar al usuario a entender, refactorizar, detectar errores y mejorar su código. "
            "Responde de manera estructurada, clara y con ejemplos de código limpios."
        )
        
        user_message = f"{context}\n\n### Consulta del estudiante:\n{prompt}"
        
        response = self.client.models.generate_content(
            model=self.model_name,
            contents=user_message,
            config={"system_instruction": system_instruction},
        )
        return response.text

# Instancia lista para ser importada por main.py
agent = CodingAgent()