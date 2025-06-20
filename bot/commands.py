import discord
from discord import app_commands
from discord.ext import commands
from bot.views import TicketPanelView

def setup_commands(bot, config, ticket_system):
    
    @bot.tree.command(name="ticket", description="Configurer le système de tickets (Admin uniquement)")
    @app_commands.describe(
        channel="Le salon où envoyer le message de tickets",
        raisons="Les raisons de tickets séparées par des virgules",
        support_roles="Les rôles à mentionner dans chaque ticket (séparés par des virgules)"
    )
    async def ticket_command(interaction: discord.Interaction, channel: discord.TextChannel, raisons: str = "", support_roles: str = ""):
        """Commande pour configurer le système de tickets"""
        
        # Vérifier les permissions d'administrateur
        if not config.is_admin(interaction.user):
            embed = discord.Embed(
                title="❌ Accès refusé",
                description="Cette commande est réservée aux administrateurs.",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        # Définir les raisons par défaut si aucune n'est fournie
        if not raisons or raisons.strip() == "":
            default_reasons = ["Vérification", "Questions", "Achat", "Autre"]
            raisons_list = default_reasons
        else:
            raisons_list = [r.strip() for r in raisons.split(",") if r.strip()]
        
        # Traiter les rôles de support
        support_role_ids = []
        if support_roles:
            role_names = [r.strip() for r in support_roles.split(",") if r.strip()]
            for role_name in role_names:
                role = discord.utils.get(interaction.guild.roles, name=role_name)
                if role:
                    support_role_ids.append(str(role.id))
        
        # Sauvegarder la configuration
        if interaction.guild:
            guild_config = {
                "ticket_channel_id": channel.id,
                "ticket_reasons": raisons_list,
                "support_roles": support_role_ids
            }
            config.set_guild_config(interaction.guild.id, guild_config)
        
        # Créer l'embed du panneau de tickets
        embed = discord.Embed(
            title="🔥 𝗕𝗼𝘂𝘁𝗶𝗾𝘂𝗲 𝗡𝗦𝗙𝗪  d'Axo - 𝗣𝗹𝗮𝗶𝘀𝗶𝗿𝘀 𝗶𝗻𝘁𝗶𝗺𝗲𝘀 🔥",
            description="❥๑━━━━━━━━━━━━━━━๑❥\nBienvenue, petit(e) coquin(e)… 💋\nIci tu peux craquer pour des contenus et services NSFW personnalisés, ta dose de plaisir sur mesure !\n💌 Pour commander, poser tes questions ou contacter le support tu peux sélectionner la raison pour laquel tu souhaites ouvrir un ticket\nOn est là pour toi, prêt·e à satisfaire toutes tes envies, rapido !\n❥๑━━━━━━━━━━━━━━━๑❥\n⚠️ Interdit aux moins de 18 ans. Respecte les règles, reste sage… ou pas. 😉",
            color=discord.Color.from_rgb(255, 20, 147)
        )
        
        # Créer la vue avec les boutons
        view = TicketPanelView(ticket_system, raisons_list)
        
        # Envoyer le message dans le salon configuré
        try:
            await channel.send(embed=embed, view=view)
            
            # Confirmation à l'administrateur
            success_embed = discord.Embed(
                title="✅ Configuration réussie",
                description=f"Le panneau de tickets a été envoyé dans {channel.mention}",
                color=discord.Color.green()
            )
            success_embed.add_field(
                name="📝 Raisons configurées",
                value="\n".join([f"• {reason}" for reason in raisons_list]),
                inline=False
            )
            await interaction.response.send_message(embed=success_embed, ephemeral=True)
            
        except discord.Forbidden:
            error_embed = discord.Embed(
                title="❌ Erreur de permissions",
                description=f"Je n'ai pas les permissions pour envoyer des messages dans {channel.mention}",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=error_embed, ephemeral=True)
        except Exception as e:
            error_embed = discord.Embed(
                title="❌ Erreur",
                description=f"Une erreur est survenue: {str(e)}",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=error_embed, ephemeral=True)
    
    @bot.tree.command(name="fermer-ticket", description="Fermer un ticket (Admin uniquement)")
    async def close_ticket(interaction: discord.Interaction):
        """Commande pour fermer un ticket"""
        
        if not config.is_admin(interaction.user):
            embed = discord.Embed(
                title="❌ Accès refusé",
                description="Cette commande est réservée aux administrateurs.",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        # Vérifier si nous sommes dans un salon de ticket
        tickets_data = config.load_tickets()
        if not interaction.channel:
            embed = discord.Embed(
                title="❌ Erreur",
                description="Impossible d'identifier le salon.",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
            
        channel_id = str(interaction.channel.id)
        
        if channel_id not in tickets_data:
            embed = discord.Embed(
                title="❌ Erreur",
                description="Cette commande ne peut être utilisée que dans un salon de ticket.",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        await ticket_system.close_ticket(interaction.channel, interaction.user)
        
        embed = discord.Embed(
            title="✅ Ticket fermé",
            description="Ce ticket a été fermé par un administrateur.",
            color=discord.Color.green()
        )
        await interaction.response.send_message(embed=embed)
