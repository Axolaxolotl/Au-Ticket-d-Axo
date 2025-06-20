import discord
from discord.ext import commands
import asyncio
from datetime import datetime
from bot.views import TicketManagementView

class TicketSystem:
    def __init__(self, bot, config):
        self.bot = bot
        self.config = config
    
    async def create_ticket(self, interaction: discord.Interaction, reason: str):
        """Créer un nouveau ticket"""
        guild = interaction.guild
        user = interaction.user
        
        # Vérifier si l'utilisateur a déjà un ticket ouvert
        user_tickets = self.config.db.get_user_open_tickets(user.id)
        
        if user_tickets:
            embed = discord.Embed(
                title="⚠️ Ticket déjà ouvert",
                description="Vous avez déjà un ticket ouvert. Veuillez fermer votre ticket actuel avant d'en créer un nouveau.",
                color=discord.Color.orange()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        # Créer le salon de ticket
        try:
            # Définir les permissions
            overwrites = {
                guild.default_role: discord.PermissionOverwrite(read_messages=False),
                user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
                guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True, manage_messages=True)
            }
            
            # Ajouter les permissions pour les rôles administrateurs
            settings = self.config.load_settings()
            admin_roles = settings.get("admin_roles", ["Admin", "Modérateur", "Staff"])
            for role in guild.roles:
                if role.name in admin_roles:
                    overwrites[role] = discord.PermissionOverwrite(read_messages=True, send_messages=True, manage_messages=True)
            
            # Créer le salon
            channel_name = f"ticket-{user.name}-{reason.lower().replace(' ', '-')}"
            ticket_channel = await guild.create_text_channel(
                name=channel_name,
                overwrites=overwrites,
                topic=f"Ticket de support pour {user.display_name} - {reason}"
            )
            
            # Sauvegarder les données du ticket dans la base de données
            self.config.db.create_ticket(
                channel_id=ticket_channel.id,
                user_id=user.id,
                guild_id=guild.id,
                reason=reason
            )
            
            # Créer le message d'accueil selon la raison
            await self.send_welcome_message(ticket_channel, user, reason)
            
            # Répondre à l'interaction
            embed = discord.Embed(
                title="✅ Ticket créé",
                description=f"Votre ticket a été créé: {ticket_channel.mention}",
                color=discord.Color.green()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            
        except discord.Forbidden:
            embed = discord.Embed(
                title="❌ Erreur de permissions",
                description="Je n'ai pas les permissions nécessaires pour créer un salon de ticket.",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
        except Exception as e:
            embed = discord.Embed(
                title="❌ Erreur",
                description=f"Une erreur est survenue lors de la création du ticket: {str(e)}",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
    
    async def send_welcome_message(self, channel, user, reason):
        """Envoyer le message d'accueil selon la raison du ticket"""
        
        # Embed principal
        embed = discord.Embed(
            title=f"🎟️ Ticket de support - {reason}",
            description=f"Bonjour {user.mention}, merci d'avoir créé un ticket de support.",
            color=discord.Color.blue(),
            timestamp=datetime.now()
        )
        embed.set_thumbnail(url=user.display_avatar.url)
        
        # Message personnalisé selon la raison
        if reason.lower() == "vérification":
            embed.add_field(
                name="🔐 Processus de vérification",
                value="Pour la vérification tu as 2 options :\n\n"
                      "1️⃣ Une photo de toi avec ton pseudo, nom de compte, nom du serveur et date + vocale\n\n"
                      "2️⃣ Demander un vocale avec l'un des membres des membres faisant partie du STAFF et activité caméra pour nous dire ton pseudo, nom de compte, nom du serveur et date\n\n"
                      "-# (Nous préférons la deuxième options, en cas de doute, nous pouvons te demandé d'écrire autre chose)",
                inline=False
            )
        elif reason.lower() == "questions":
            embed.add_field(
                name="❓ Questions",
                value="Décris nous ta question, nous te répondrons dans les plus brefs délais",
                inline=False
            )
        elif reason.lower() == "achat":
            embed.add_field(
                name="💰 Achat",
                value="Mentionnes la princesse et attends sa réponse, elle te repondra dans les plus bref délais",
                inline=False
            )
        elif reason.lower() == "autre":
            embed.add_field(
                name="🎟️ Autre",
                value="Décris nous ton problème, nous traiterons ta demande au plus vite.",
                inline=False
            )
        else:
            embed.add_field(
                name="🆘 Support",
                value="Décris ton problème nous te répondront dans les meilleurs délais",
                inline=False
            )
        
        embed.add_field(
            name="📞 Contact",
            value="Notre équipe de support vous répondra bientôt. En attendant, n'hésitez pas à fournir tous les détails nécessaires.",
            inline=False
        )
        
        embed.set_footer(text="Support Ticket • Réponse rapide")
        
        # Mentionner les rôles de support
        guild_config = self.config.get_guild_config(interaction.guild.id)
        support_roles = guild_config.get("support_roles", [])
        
        mention_text = ""
        if support_roles:
            mentions = []
            for role_id in support_roles:
                role = interaction.guild.get_role(int(role_id))
                if role:
                    mentions.append(role.mention)
            if mentions:
                mention_text = " ".join(mentions)
        
        # Vue de gestion du ticket
        view = TicketManagementView(self)
        
        # Envoyer le message d'accueil
        await channel.send(embed=embed, view=view)
        
        # Envoyer les mentions séparément si nécessaire
        if mention_text:
            await channel.send(mention_text)
    
    async def close_ticket(self, channel, closed_by):
        """Fermer un ticket"""
        # Fermer le ticket dans la base de données
        ticket = self.config.db.close_ticket(channel.id, closed_by.id)
        
        if ticket:
            
            # Modifier les permissions pour fermer le ticket
            overwrites = channel.overwrites
            for target, overwrite in overwrites.items():
                if isinstance(target, discord.Member) and target.id == tickets_data[channel_id]["user_id"]:
                    overwrite.send_messages = False
                    await channel.set_permissions(target, overwrite=overwrite)
            
            # Message de fermeture
            embed = discord.Embed(
                title="🔒 Ticket fermé",
                description=f"Ce ticket a été fermé par {closed_by.mention}.\n"
                           f"Si vous avez besoin d'aide supplémentaire, créez un nouveau ticket.",
                color=discord.Color.red(),
                timestamp=datetime.now()
            )
            embed.set_footer(text="Ticket fermé")
            
            await channel.send(embed=embed)
    
    async def delete_ticket(self, channel):
        """Supprimer un ticket"""
        tickets_data = self.config.load_tickets()
        channel_id = str(channel.id)
        
        if channel_id in tickets_data:
            # Marquer comme supprimé
            tickets_data[channel_id]["status"] = "deleted"
            tickets_data[channel_id]["deleted_at"] = datetime.now().isoformat()
            self.config.save_tickets(tickets_data)
        
        # Supprimer le salon après un court délai
        await asyncio.sleep(2)
        try:
            await channel.delete()
        except discord.NotFound:
            pass  # Le salon a déjà été supprimé
        except discord.Forbidden:
            print(f"Pas de permission pour supprimer le salon {channel.name}")
    
    async def handle_button_interaction(self, interaction):
        """Gérer les interactions des boutons (fallback si nécessaire)"""
        # Cette méthode est un fallback au cas où on aurait besoin de gérer
        # des interactions de boutons spéciales
        pass
