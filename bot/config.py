from database import DatabaseManager
from typing import Dict, List, Optional

class Config:
    def __init__(self):
        self.db = DatabaseManager()
    
    def load_settings(self) -> Dict:
        """Charger les paramètres de configuration"""
        guilds = self.db.get_all_guilds()
        admin_roles = self.db.get_admin_roles()
        return {
            "guilds": guilds,
            "admin_roles": admin_roles
        }
    
    def save_settings(self, settings: Dict):
        """Sauvegarder les paramètres de configuration"""
        # Cette méthode n'est plus nécessaire avec la base de données
        # mais on la garde pour la compatibilité
        pass
    
    def load_tickets(self) -> Dict:
        """Charger les données des tickets"""
        return self.db.get_all_tickets()
    
    def save_tickets(self, tickets: Dict):
        """Sauvegarder les données des tickets"""
        # Cette méthode n'est plus nécessaire avec la base de données
        # mais on la garde pour la compatibilité
        pass
    
    def get_guild_config(self, guild_id: int) -> Dict:
        """Obtenir la configuration d'un serveur"""
        return self.db.get_guild_config(guild_id)
    
    def set_guild_config(self, guild_id: int, config: Dict):
        """Définir la configuration d'un serveur"""
        self.db.set_guild_config(guild_id, config)
    
    def is_admin(self, member) -> bool:
        """Vérifier si un membre est administrateur"""
        if member.guild_permissions.administrator:
            return True
        
        admin_roles = self.db.get_admin_roles()
        
        for role in member.roles:
            if role.name in admin_roles:
                return True
        
        return False
