import os
import discord
import aiohttp
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
API_URL = os.getenv("API_URL", "https://almaia-gwnt.onrender.com")

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

def split_text(text: str, max_length: int = 1900):
    """Divide respuestas largas en fragmentos seguros para Discord."""
    chunks = []
    while len(text) > max_length:
        split_index = text.rfind("\n", 0, max_length)
        if split_index == -1:
            split_index = max_length
        chunks.append(text[:split_index])
        text = text[split_index:]
    chunks.append(text)
    return chunks

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"🤖 Bot iniciado con éxito como {bot.user}")

@bot.tree.command(name="repos", description="Muestra la lista de tus repositorios de GitHub.")
async def repos(interaction: discord.Interaction):
    await interaction.response.defer()
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{API_URL}/repos") as resp:
                if resp.status == 200:
                    data = await resp.json()
                    lista_repos = data.get("repositories", [])
                    if not lista_repos:
                        await interaction.followup.send("📁 No se encontraron repositorios.")
                        return
                    
                    repos_formatted = "\n".join([f"• `{r}`" for r in lista_repos])
                    mensaje = f"**📁 Repositorios disponibles en tu GitHub:**\n{repos_formatted}"
                    
                    for chunk in split_text(mensaje):
                        await interaction.followup.send(chunk)
                else:
                    await interaction.followup.send(f"❌ Error en el backend: Código HTTP {resp.status}")
    except Exception as e:
        await interaction.followup.send(f"❌ Error de conexión con Render: `{str(e)}`")

@bot.tree.command(name="analizar", description="Analiza tu código de GitHub con la IA.")
@app_commands.describe(
    repo="Nombre de tu repositorio en GitHub (ej: almaia)",
    pregunta="Consulta o instrucción sobre el código"
)
async def analizar(interaction: discord.Interaction, repo: str, pregunta: str):
    await interaction.response.defer()
    payload = {"repo_name": repo, "prompt": pregunta}

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(f"{API_URL}/analyze", json=payload) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    respuesta_ia = data.get("analysis", "Sin respuesta disponible.")

                    header = f"🔍 **Análisis de `{repo}`**\n> *Pregunta: {pregunta}*\n\n"
                    full_response = header + respuesta_ia
                    
                    for chunk in split_text(full_response):
                        await interaction.followup.send(chunk)
                else:
                    await interaction.followup.send(f"❌ Error HTTP {resp.status} al procesar el análisis.")
    except Exception as e:
        await interaction.followup.send(f"❌ Error de comunicación: `{str(e)}`")

if __name__ == "__main__":
    bot.run(DISCORD_TOKEN)