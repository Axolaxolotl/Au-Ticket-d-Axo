import discord
from discord.ext import commands
from bot.ticket_system import TicketSystem
from bot.commands import setup_commands
from bot.config import Config

# Configuration des intents
intents = discord.Intents.default()
intents.guilds = True
intents.guild_messages = True

# Création des objets principaux
bot = commands.Bot(command_prefix='!', intents=intents)
config = Config()
ticket_system = TicketSystem(bot, config)

@bot.event
async def on_ready():
    print(f'{bot.user} est connecté et prêt!')
    try:
        synced = await bot.tree.sync()
        print(f"Synchronisé {len(synced)} commande(s)")
    except Exception as e:
        print(f"Erreur lors de la synchronisation: {e}")

def setup():
    setup_commands(bot, config, ticket_system)
