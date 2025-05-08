import os
import datetime
from flask import Flask, redirect, request, session, render_template, url_for
from requests_oauthlib import OAuth2Session
from dotenv import load_dotenv
from threading import Thread
import discord
from discord.ext import commands

# Permite HTTP para OAuth2 localmente
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

# Carrega .env
load_dotenv()
CLIENT_ID = os.getenv("DISCORD_CLIENT_ID")
CLIENT_SECRET = os.getenv("DISCORD_CLIENT_SECRET")
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
REDIRECT_URI = "http://127.0.0.1:5000/callback"
API_BASE_URL = "https://discord.com/api"
AUTH_URL = f"{API_BASE_URL}/oauth2/authorize"
TOKEN_URL = f"{API_BASE_URL}/oauth2/token"
SCOPE = ["identify"]

# Flask
app = Flask(__name__)
app.secret_key = os.urandom(24)

# Bot Discord
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True
bot = commands.Bot(command_prefix='!', intents=intents)

# OAuth2
def make_session(token=None, state=None):
    return OAuth2Session(
        client_id=CLIENT_ID,
        token=token,
        state=state,
        redirect_uri=REDIRECT_URI,
        scope=SCOPE
    )

# Rotas
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/login")
def login():
    discord_session = make_session()
    auth_url, state = discord_session.authorization_url(AUTH_URL)
    session["oauth_state"] = state
    return redirect(auth_url)

@app.route("/callback")
def callback():
    discord_session = make_session(state=session.get("oauth_state"))
    token = discord_session.fetch_token(
        TOKEN_URL,
        client_secret=CLIENT_SECRET,
        authorization_response=request.url
    )
    session["oauth_token"] = token
    user = discord_session.get(f"{API_BASE_URL}/users/@me").json()
    session["user"] = user
    return redirect(url_for("dashboard"))

@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect(url_for("home"))

    user = session["user"]
    avatar_url = f"https://cdn.discordapp.com/avatars/{user['id']}/{user['avatar']}.png" if user.get("avatar") else ""
    guilds_count = len(bot.guilds)
    total_members = sum(g.member_count or 0 for g in bot.guilds)

    return render_template("dashboard.html",
        user=user,
        username=user["username"],
        user_id=user["id"],
        avatar_url=avatar_url,
        stats={"guilds": guilds_count, "members": total_members},
        datetime=datetime
    )

@app.route("/comandos")
def comandos():
    if "user" not in session:
        return redirect(url_for("home"))
    return render_template("comandos.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))

# Bot em paralelo
def run_bot():
    @bot.event
    async def on_ready():
        print(f"✅ Bot online: {bot.user}")
    bot.run(DISCORD_TOKEN)

# Start
if __name__ == "__main__":
    Thread(target=run_bot).start()
    app.run(debug=True, use_reloader=False)
