import os
from dotenv import load_dotenv
from pathlib import Path
import discord
from discord.ext import commands
from openai import OpenAI

# Carrega .env
env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

# Inicializa OpenAI
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Discord intents e bot
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'✅ Bot online como {bot.user}!')

@bot.command()
async def oi(ctx):
    await ctx.send('Oi! Eu sou seu bot 🤖')

@bot.command()
async def perfil(ctx):
    embed = discord.Embed(
        title="👤 Perfil do Usuário",
        description=f"Olá {ctx.author.mention}, aqui estão seus dados!",
        color=discord.Color.blurple()
    )
    embed.set_thumbnail(url=ctx.author.avatar.url if ctx.author.avatar else "")
    embed.add_field(name="Nome", value=ctx.author.name, inline=True)
    embed.add_field(name="ID", value=ctx.author.id, inline=True)
    embed.set_footer(text="Bot do Enzo - Powered by discord.py")
    await ctx.send(embed=embed)

@bot.command()
async def pergunte(ctx, *, pergunta):
    await ctx.send("💭 Pensando...")
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": pergunta}],
            max_tokens=150,
            temperature=0.7,
        )
        resposta = response.choices[0].message.content.strip()
        await ctx.send(f"🤖 {resposta}")
    except Exception as e:
        await ctx.send("⚠️ Ocorreu um erro ao tentar responder.")
        print("Erro:", e)

# AGORA FORA DO BLOCO DE CIMA
@bot.command()
async def imagem(ctx, *, prompt):
    await ctx.send("🎨 Gerando imagem...")

    try:
        response = client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            size="1024x1024",
            quality="standard",
            n=1,
        )
        image_url = response.data[0].url
        await ctx.send(f"🖼️ Aqui está sua imagem:\n{image_url}")
    except Exception as e:
        await ctx.send("❌ Erro ao gerar imagem.")
        print("Erro imagem:", e)


@pergunte.error
async def pergunte_error(ctx, error):
    await ctx.send("❗️Você precisa perguntar algo. Exemplo: `!pergunte O que é Python?`")

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    if 'tudo bem' in message.content.lower():
        await message.channel.send('Tudo ótimo! E você? 😄')
    await bot.process_commands(message)

bot.run(os.getenv("DISCORD_TOKEN"))
