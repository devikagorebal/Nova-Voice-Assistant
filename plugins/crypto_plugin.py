"""
plugins/crypto_plugin.py - Sample Cryptocurrency Price Plugin
Demonstrates the dynamic plugin extension system (Part 21).
"""

def init_plugin(app):
    app.append_chat("System", "[Plugin: Crypto Tracker] Initialized successfully.")

def handle_command(app, cmd: str) -> bool:
    clean = cmd.lower().strip()
    if any(k in clean for k in ["bitcoin price", "btc price", "crypto price", "ethereum price"]):
        prices = "Live Crypto Market: Bitcoin (BTC): $94,500 | Ethereum (ETH): $3,450 | Solana (SOL): $210"
        app.append_chat("Jarvis", prices)
        if hasattr(app, "safe_speak"):
            app.safe_speak("Bitcoin is currently trading at ninety-four thousand five hundred dollars.")
        return True
    return False
