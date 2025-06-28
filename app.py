import os
import asyncio
from main import bot, setup

async def start_bot():
    setup()  # configure les commandes slash
    token = os.getenv('DISCORD_TOKEN', 'YOUR_BOT_TOKEN_HERE')
    if token == 'YOUR_BOT_TOKEN_HERE':
        print("⚠️  Token Discord non défini dans les variables d’environnement.")
        return
    await bot.start(token)

if __name__ == "__main__":
    asyncio.run(start_bot())

