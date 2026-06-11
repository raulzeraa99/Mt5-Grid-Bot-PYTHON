"""
Dashboard para Grid Bot
API REST para monitorar o Grid Trading
"""

from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import MetaTrader5 as mt5
import logging
import os
from datetime import datetime

app = Flask(__name__)
CORS(app)

# Desabilita logs verbosos do Flask
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

# Bot instance (sera setado externamente)
grid_bot = None

def set_bot_instance(bot):
    """Define instancia do bot"""
    global grid_bot
    grid_bot = bot

@app.route('/')
def home():
    """Redireciona para dashboard"""
    return send_from_directory('templates', 'dashboard_grid.html')

@app.route('/templates/<path:filename>')
def serve_template(filename):
    """Serve arquivos do diretorio templates"""
    return send_from_directory('templates', filename)

@app.route('/api/status')
def get_status():
    """Status geral do bot e conta"""
    try:
        account = grid_bot.get_account_info() if grid_bot else None
        
        if not account:
            return jsonify({'error': 'Bot nao inicializado'}), 500
        
        # Lucro DIARIO (trades fechados hoje)
        daily_profit = grid_bot.get_daily_profit()
        
        # Lucro flutuante (posicoes abertas)
        open_profit = grid_bot.get_total_profit()
        
        positions = grid_bot.get_open_positions()
        
        # Verifica se meta diaria foi atingida
        target_reached = daily_profit >= grid_bot.daily_profit_target
        
        # Drawdown
        max_drawdown = grid_bot.max_drawdown if hasattr(grid_bot, 'max_drawdown') else 0.0
        peak_equity = grid_bot.peak_equity if hasattr(grid_bot, 'peak_equity') else account['equity']
        
        # Flag de posições fechadas
        target_reached_and_closed = grid_bot.target_reached_today if hasattr(grid_bot, 'target_reached_today') else False
        
        return jsonify({
            'balance': account['balance'],
            'equity': account['equity'],
            'profit': account['profit'],
            'daily_profit': daily_profit,
            'open_profit': open_profit,
            'profit_target': grid_bot.daily_profit_target,
            'progress_percent': (daily_profit / grid_bot.daily_profit_target * 100) if grid_bot.daily_profit_target > 0 else 0,
            'target_reached': target_reached,
            'target_reached_and_closed': target_reached_and_closed,
            'max_drawdown': max_drawdown,
            'peak_equity': peak_equity,
            'open_positions': len(positions),
            'max_levels': grid_bot.max_levels,
            'grid_distance': grid_bot.grid_distance,
            'initial_lot': grid_bot.initial_lot,
            'symbol': grid_bot.symbol
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/positions')
def get_positions():
    """Lista posicoes abertas"""
    try:
        positions = grid_bot.get_open_positions() if grid_bot else []
        
        pos_list = []
        for pos in positions:
            pos_list.append({
                'ticket': pos.ticket,
                'type': 'BUY' if pos.type == mt5.POSITION_TYPE_BUY else 'SELL',
                'volume': pos.volume,
                'price_open': pos.price_open,
                'price_current': pos.price_current,
                'tp': pos.tp,
                'profit': pos.profit,
                'comment': pos.comment
            })
        
        return jsonify(pos_list)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/close_all', methods=['POST'])
def close_all():
    """Fecha todas as posicoes"""
    try:
        if not grid_bot:
            return jsonify({'error': 'Bot nao inicializado'}), 500
        
        success = grid_bot.close_all_positions()
        
        if success:
            return jsonify({'success': True, 'message': 'Todas posicoes fechadas'})
        else:
            return jsonify({'success': False, 'message': 'Erro ao fechar posicoes'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/reset', methods=['POST'])
def reset_counters():
    """Reseta contadores do bot (zera tudo)"""
    try:
        if not grid_bot:
            return jsonify({'error': 'Bot nao inicializado'}), 500
        
        grid_bot.reset_now()
        
        return jsonify({'success': True, 'message': 'Contadores resetados com sucesso!'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/market_data')
def get_market_data():
    """Dados de mercado"""
    try:
        if not grid_bot:
            return jsonify({'error': 'Bot nao inicializado'}), 500
        
        bid, ask = grid_bot.get_current_price()
        
        if bid is None:
            return jsonify({'error': 'Erro ao obter precos'}), 500
        
        spread = ask - bid
        
        return jsonify({
            'bid': bid,
            'ask': ask,
            'spread': spread,
            'mid': (bid + ask) / 2
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def run_dashboard(host='0.0.0.0', port=5001):
    """Inicia servidor Flask"""
    app.run(host=host, port=port, debug=False, use_reloader=False)
