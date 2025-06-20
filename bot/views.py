import discord
from discord.ext import commands
from typing import List

class TicketPanelView(discord.ui.View):
    def __init__(self, ticket_system, reasons: List[str]):
        super().__init__(timeout=None)
        self.ticket_system = ticket_system
        
        # Créer le sélecteur avec les raisons
        select = TicketSelect(ticket_system, reasons)
        self.add_item(select)

class TicketSelect(discord.ui.Select):
    def __init__(self, ticket_system, reasons: List[str]):
        self.ticket_system = ticket_system
        
        # Définir les options du sélecteur
        options = []
        emoji_map = {
            "Vérification": "🔐",
            "Questions": "❓",
            "Achat": "💰", 
            "Autre": "🎟️"
        }
        
        for reason in reasons:
            emoji = emoji_map.get(reason, "🎟️")
            options.append(discord.SelectOption(
                label=reason,
                description=f"Créer un ticket pour {reason.lower()}",
                emoji=emoji,
                value=reason
            ))
        
        super().__init__(
            placeholder="Sélectionnez la raison de votre ticket...",
            min_values=1,
            max_values=1,
            options=options,
            custom_id="ticket_select"
        )
    
    async def callback(self, interaction: discord.Interaction):
        selected_reason = self.values[0]
        await self.ticket_system.create_ticket(interaction, selected_reason)

class TicketManagementView(discord.ui.View):
    def __init__(self, ticket_system):
        super().__init__(timeout=None)
        self.ticket_system = ticket_system
    
    @discord.ui.button(label="Fermer le ticket", style=discord.ButtonStyle.danger, emoji="🔒")
    async def close_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Vérifier les permissions
        if not self.ticket_system.config.is_admin(interaction.user):
            embed = discord.Embed(
                title="❌ Accès refusé",
                description="Seuls les administrateurs peuvent fermer les tickets.",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        await self.ticket_system.close_ticket(interaction.channel, interaction.user)
        
        embed = discord.Embed(
            title="✅ Ticket fermé",
            description="Ce ticket a été fermé.",
            color=discord.Color.green()
        )
        await interaction.response.send_message(embed=embed)
    
    @discord.ui.button(label="Supprimer le ticket", style=discord.ButtonStyle.danger, emoji="🗑️")
    async def delete_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Vérifier les permissions
        if not self.ticket_system.config.is_admin(interaction.user):
            embed = discord.Embed(
                title="❌ Accès refusé",
                description="Seuls les administrateurs peuvent supprimer les tickets.",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        # Confirmation avant suppression
        confirm_embed = discord.Embed(
            title="⚠️ Confirmation de suppression",
            description="Êtes-vous sûr de vouloir supprimer ce ticket ? Cette action est irréversible.",
            color=discord.Color.orange()
        )
        
        confirm_view = ConfirmDeleteView(self.ticket_system)
        await interaction.response.send_message(embed=confirm_embed, view=confirm_view, ephemeral=True)

class ConfirmDeleteView(discord.ui.View):
    def __init__(self, ticket_system):
        super().__init__(timeout=60)
        self.ticket_system = ticket_system
    
    @discord.ui.button(label="Confirmer la suppression", style=discord.ButtonStyle.danger, emoji="✅")
    async def confirm_delete(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.ticket_system.delete_ticket(interaction.channel)
        # Le canal sera supprimé, donc pas besoin de répondre
    
    @discord.ui.button(label="Annuler", style=discord.ButtonStyle.secondary, emoji="❌")
    async def cancel_delete(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(
            title="✅ Suppression annulée",
            description="Le ticket n'a pas été supprimé.",
            color=discord.Color.green()
        )
        await interaction.response.edit_message(embed=embed, view=None)
