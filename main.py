import discord
from discord.ext import commands
import json
import os
import asyncio
from bot.ticket_system import TicketSystem
from bot.commands import setup_commands
from bot.config import Config

# Configuration du bot
intents = discord.Intents.default()
intents.guilds = True
intents.guild_messages = True

bot = commands.Bot(command_prefix='!', intents=intents)
config = Config()
ticket_system = TicketSystem(bot, config)

@bot.event
async def on_ready():
    print(f'{bot.user} est connecté et prêt!')
    try:
        # Synchroniser les commandes slash
        synced = await bot.tree.sync()
        print(f"Synchronisé {len(synced)} commande(s)")
    except Exception as e:
        print(f"Erreur lors de la synchronisation: {e}")

@bot.event
async def on_interaction(interaction):
    """Gérer les interactions des boutons"""
    if interaction.type == discord.InteractionType.component:
        await ticket_system.handle_button_interaction(interaction)

async def main():
    # Configuration des commandes
    setup_commands(bot, config, ticket_system)
    
    # Démarrer le bot
    token = os.getenv('DISCORD_TOKEN', 'YOUR_BOT_TOKEN_HERE')
    if token == 'YOUR_BOT_TOKEN_HERE':
        print("⚠️  ATTENTION: Veuillez définir la variable d'environnement DISCORD_TOKEN")
        print("   Exemple: export DISCORD_TOKEN='votre_token_ici'")
        return
    
    await bot.start(token)

if __name__ == "__main__":
    asyncio.run(main())
