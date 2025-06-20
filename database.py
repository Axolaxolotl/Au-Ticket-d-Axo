from sqlalchemy.orm import sessionmaker
from models import Guild, Ticket, TicketReason, AdminRole, SessionLocal, create_tables, init_default_data
from typing import Dict, List, Optional
from datetime import datetime
import json

class DatabaseManager:
    def __init__(self):
        # Create tables and initialize default data
        create_tables()
        init_default_data()
    
    def get_session(self):
        """Get a new database session"""
        return SessionLocal()
    
    def get_guild_config(self, guild_id: int) -> Dict:
        """Get guild configuration"""
        db = self.get_session()
        try:
            guild = db.query(Guild).filter(Guild.id == str(guild_id)).first()
            if not guild:
                return {}
            
            reasons = db.query(TicketReason).filter(TicketReason.guild_id == str(guild_id)).all()
            reason_list = [reason.reason for reason in reasons]
            
            support_roles = []
            if guild.support_roles:
                try:
                    support_roles = json.loads(guild.support_roles)
                except:
                    support_roles = []
            
            return {
                "ticket_channel_id": guild.ticket_channel_id,
                "ticket_reasons": reason_list,
                "support_roles": support_roles
            }
        finally:
            db.close()
    
    def set_guild_config(self, guild_id: int, config: Dict):
        """Set guild configuration"""
        db = self.get_session()
        try:
            guild = db.query(Guild).filter(Guild.id == str(guild_id)).first()
            if not guild:
                guild = Guild(id=str(guild_id))
                db.add(guild)
            
            if "ticket_channel_id" in config:
                guild.ticket_channel_id = config["ticket_channel_id"]
            
            if "support_roles" in config:
                guild.support_roles = json.dumps(config["support_roles"])
            
            db.commit()
            
            # Update ticket reasons
            if "ticket_reasons" in config:
                db.query(TicketReason).filter(TicketReason.guild_id == str(guild_id)).delete()
                for reason in config["ticket_reasons"]:
                    ticket_reason = TicketReason(guild_id=str(guild_id), reason=reason)
                    db.add(ticket_reason)
                db.commit()
        finally:
            db.close()
    
    def get_all_guilds(self) -> Dict:
        """Get all configured guilds"""
        db = self.get_session()
        try:
            guilds = db.query(Guild).all()
            result = {}
            for guild in guilds:
                config = self.get_guild_config(int(guild.id))
                result[guild.id] = config
            return result
        finally:
            db.close()
    
    def create_ticket(self, channel_id: int, user_id: int, guild_id: int, reason: str):
        """Create a new ticket"""
        db = self.get_session()
        try:
            ticket = Ticket(
                channel_id=str(channel_id),
                user_id=str(user_id),
                guild_id=str(guild_id),
                reason=reason
            )
            db.add(ticket)
            db.commit()
        finally:
            db.close()
    
    def get_ticket(self, channel_id: int) -> Optional[Ticket]:
        """Get ticket by channel ID"""
        db = self.get_session()
        try:
            return db.query(Ticket).filter(Ticket.channel_id == str(channel_id)).first()
        finally:
            db.close()
    
    def get_user_open_tickets(self, user_id: int) -> List[Ticket]:
        """Get all open tickets for a user"""
        db = self.get_session()
        try:
            return db.query(Ticket).filter(
                Ticket.user_id == str(user_id),
                Ticket.status == 'open'
            ).all()
        finally:
            db.close()
    
    def close_ticket(self, channel_id: int, closed_by: int):
        """Close a ticket"""
        db = self.get_session()
        try:
            ticket = db.query(Ticket).filter(Ticket.channel_id == str(channel_id)).first()
            if ticket:
                ticket.status = 'closed'
                ticket.closed_at = datetime.utcnow()
                ticket.closed_by = str(closed_by)
                db.commit()
        finally:
            db.close()
    
    def delete_ticket(self, channel_id: int):
        """Mark ticket as deleted"""
        db = self.get_session()
        try:
            ticket = db.query(Ticket).filter(Ticket.channel_id == str(channel_id)).first()
            if ticket:
                ticket.status = 'deleted'
                ticket.deleted_at = datetime.utcnow()
                db.commit()
        finally:
            db.close()
    
    def get_all_tickets(self) -> Dict:
        """Get all tickets formatted for compatibility"""
        db = self.get_session()
        try:
            tickets = db.query(Ticket).all()
            result = {}
            for ticket in tickets:
                result[ticket.channel_id] = {
                    "user_id": int(ticket.user_id),
                    "guild_id": int(ticket.guild_id),
                    "reason": ticket.reason,
                    "status": ticket.status,
                    "created_at": ticket.created_at.isoformat() if ticket.created_at else None,
                    "closed_at": ticket.closed_at.isoformat() if ticket.closed_at else None,
                    "closed_by": int(ticket.closed_by) if ticket.closed_by else None
                }
            return result
        finally:
            db.close()
    
    def get_admin_roles(self) -> List[str]:
        """Get all admin role names"""
        db = self.get_session()
        try:
            roles = db.query(AdminRole).all()
            return [role.role_name for role in roles]
        finally:
            db.close()
    
    def is_admin_role(self, role_name: str) -> bool:
        """Check if a role is an admin role"""
        return role_name in self.get_admin_roles()
    
    def get_ticket_stats(self) -> Dict:
        """Get ticket statistics"""
        db = self.get_session()
        try:
            total = db.query(Ticket).count()
            open_tickets = db.query(Ticket).filter(Ticket.status == 'open').count()
            closed = db.query(Ticket).filter(Ticket.status == 'closed').count()
            
            return {
                "total": total,
                "open": open_tickets,
                "closed": closed
            }
        finally:
            db.close()
