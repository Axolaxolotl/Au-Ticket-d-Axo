import os
import asyncio
import threading
from flask import Flask, render_template, request, jsonify
from datetime import datetime
import json

# Import du bot Discord
from main import bot, config, ticket_system, main as bot_main

app = Flask(__name__)

# Variable globale pour le statut du bot
bot_status = {"connected": False, "guilds": 0, "last_update": None}

def update_bot_status():
    """Mettre à jour le statut du bot"""
    global bot_status
    try:
        if bot and bot.is_ready():
            bot_status = {
                "connected": True,
                "guilds": len(bot.guilds),
                "last_update": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
        else:
            bot_status = {
                "connected": False,
                "guilds": 0,
                "last_update": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
    except Exception as e:
        bot_status = {
            "connected": False,
            "guilds": 0,
            "last_update": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "error": str(e)
        }

@app.route('/')
def index():
    """Page d'accueil"""
    update_bot_status()
    return render_template('index.html', bot_status=bot_status)

@app.route('/dashboard')
def dashboard():
    """Tableau de bord administrateur"""
    update_bot_status()
    
    # Récupérer les statistiques
    tickets_data = config.load_tickets()
    settings = config.load_settings()
    
    stats = {
        "total_tickets": len(tickets_data),
        "open_tickets": len([t for t in tickets_data.values() if t.get("status") == "open"]),
        "closed_tickets": len([t for t in tickets_data.values() if t.get("status") == "closed"]),
        "guilds_configured": len(settings.get("guilds", {}))
    }
    
    return render_template('dashboard.html', 
                         bot_status=bot_status, 
                         stats=stats,
                         guilds=settings.get("guilds", {}))

@app.route('/tickets')
def tickets():
    """Page des tickets"""
    tickets_data = config.load_tickets()
    
    # Trier les tickets par date de création (plus récents en premier)
    sorted_tickets = sorted(tickets_data.items(), 
                          key=lambda x: x[1].get("created_at", ""), 
                          reverse=True)
    
    return render_template('tickets.html', tickets=sorted_tickets)

@app.route('/api/bot-status')
def api_bot_status():
    """API pour obtenir le statut du bot"""
    update_bot_status()
    return jsonify(bot_status)

@app.route('/api/stats')
def api_stats():
    """API pour obtenir les statistiques"""
    tickets_data = config.load_tickets()
    settings = config.load_settings()
    
    stats = {
        "total_tickets": len(tickets_data),
        "open_tickets": len([t for t in tickets_data.values() if t.get("status") == "open"]),
        "closed_tickets": len([t for t in tickets_data.values() if t.get("status") == "closed"]),
        "guilds_configured": len(settings.get("guilds", {})),
        "last_ticket": None
    }
    
    # Obtenir le dernier ticket créé
    if tickets_data:
        latest_ticket = max(tickets_data.values(), key=lambda x: x.get("created_at", ""))
        stats["last_ticket"] = {
            "reason": latest_ticket.get("reason"),
            "created_at": latest_ticket.get("created_at"),
            "status": latest_ticket.get("status")
        }
    
    return jsonify(stats)

@app.route('/health')
def health():
    """Point de santé pour Render"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "bot_connected": bot.is_ready() if bot else False,
        "web_app": "running"
    })

def run_bot():
    """Démarrer le bot Discord dans un thread séparé"""
    try:
        asyncio.run(bot_main())
    except Exception as e:
        print(f"Erreur lors du démarrage du bot: {e}")

def run_web_app():
    """Démarrer l'application web"""
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False, threaded=True)

if __name__ == '__main__':
    # Démarrer le bot Discord dans un thread séparé
    bot_thread = threading.Thread(target=run_bot, daemon=True)
    bot_thread.start()
    
    # Attendre un peu pour que le bot se connecte
    import time
    time.sleep(3)
    
    # Démarrer l'application web
    run_web_app()