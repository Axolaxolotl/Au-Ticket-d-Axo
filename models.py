import os
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime

# Database configuration
DATABASE_URL = os.environ.get('DATABASE_URL')
if not DATABASE_URL:
    DATABASE_URL = "sqlite:///discord_tickets.db"

# SQLAlchemy setup
Base = declarative_base()
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class Guild(Base):
    __tablename__ = 'guilds'
    
    id = Column(String, primary_key=True)  # Discord Guild ID
    name = Column(String, nullable=True)
    ticket_channel_id = Column(String, nullable=True)
    support_roles = Column(Text, nullable=True)  # JSON string of role IDs
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    tickets = relationship("Ticket", back_populates="guild")
    ticket_reasons = relationship("TicketReason", back_populates="guild")

class TicketReason(Base):
    __tablename__ = 'ticket_reasons'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    guild_id = Column(String, ForeignKey('guilds.id'), nullable=False)
    reason = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    guild = relationship("Guild", back_populates="ticket_reasons")

class Ticket(Base):
    __tablename__ = 'tickets'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    channel_id = Column(String, unique=True, nullable=False)  # Discord Channel ID
    user_id = Column(String, nullable=False)  # Discord User ID
    guild_id = Column(String, ForeignKey('guilds.id'), nullable=False)
    reason = Column(String, nullable=False)
    status = Column(String, default='open')  # open, closed, deleted
    created_at = Column(DateTime, default=datetime.utcnow)
    closed_at = Column(DateTime, nullable=True)
    closed_by = Column(String, nullable=True)  # Discord User ID
    deleted_at = Column(DateTime, nullable=True)
    
    # Relationships
    guild = relationship("Guild", back_populates="tickets")

class AdminRole(Base):
    __tablename__ = 'admin_roles'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    role_name = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

def create_tables():
    """Create all tables"""
    Base.metadata.create_all(bind=engine)

def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_default_data():
    """Initialize default data"""
    db = SessionLocal()
    try:
        # Check if admin roles exist
        admin_count = db.query(AdminRole).count()
        if admin_count == 0:
            # Add default admin roles
            default_roles = ["Admin", "Administrateur", "Moderator", "Modérateur", "Owner", "Propriétaire"]
            for role_name in default_roles:
                admin_role = AdminRole(role_name=role_name)
                db.add(admin_role)
            db.commit()
    finally:
        db.close()
