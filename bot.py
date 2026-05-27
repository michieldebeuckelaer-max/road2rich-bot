import requests
import time
import random
import io
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime

import os

BOT_TOKEN = os.environ.get("BOT_TOKEN")
API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"

GRAPJES = [
    "Waarom vertrouwen beleggers nooit op atomen?\n\nOmdat ze alles verzinnen! 😂",
    "Hoe noem je een Bitcoin die slecht slaapt?\n\nEen crypto-nacht! 😴",
    "Waarom ging de crypto-investeerder naar de dokter?\n\nZijn portfolio was in de dip! 📉😂",
    "Wat zegt een rijke Bitcoin tegen een arme altcoin?\n\n'Sorry, ik heb geen kleingeld!' 🤣",
    "Waarom zijn crypto-traders zulke goede musici?\n\nZe kennen alle highs en lows! 🎵📈",
    "Hoe noem je iemand die al zijn geld in Dogecoin stopt?\n\nEen optimist! 🐕😂",
    "Wat is het verschil tussen een pizza en een crypto-trader?\n\nEen pizza kan een gezin onderhouden! 🍕😅",
    "Waarom deed de Bitcoin-miner mee aan de marathon?\n\nHij wilde de block chain breken! 🏃😂",
    "Wat zei de ene wallet tegen de andere?\n\n'Jij bent leeg, maar ik heb ook niet veel te bieden!' 👛😂",
    "Hoe noem je een beer in de crypto-wereld?\n\nEen bear market... maar dan eentje die echt bijt! 🐻📉",
]

MY_STOCKS = ["ABCL", "SSLV.L", "TTWO", "CCJ", "CRWV"]

def get_stock_price(symbol):
    symbol = symbol.upper()
    try:
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?interval=1d&range=2d"
        res = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
        data = res.json()
        result = data["chart"].get("result")
        if not result:
            return f"❌ Aandeel `{symbol}` niet gevonden. Controleer de ticker!"
        meta = result[0]["meta"]
        price = meta.get("regularMarketPrice", 0)
        prev = meta.get("chartPreviousClose", price)
        change = ((price - prev) / prev * 100) if prev else 0
        currency = meta.get("currency", "USD")
        name = meta.get("shortName", symbol)
        arrow = "📈" if change >= 0 else "📉"
        sign = "+" if change >= 0 else ""
        return (
            f"{arrow} *{name} ({symbol})*\n"
            f"💰 Prijs: `{currency} {price:,.2f}`\n"
            f"📊 24h: `{sign}{change:.2f}%`\n"
            f"🏦 Markt: `{meta.get('exchangeName', '?')}`"
        )
    except Exception as e:
        return f"❌ Fout bij ophalen van {symbol}: {e}"

def get_all_stocks():
    lines = ["📋 *Mijn Aandelen*\n"]
    for symbol in MY_STOCKS:
        try:
            url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?interval=1d&range=2d"
            res = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
            data = res.json()
            meta = data["chart"]["result"][0]["meta"]
            price = meta.get("regularMarketPrice", 0)
            prev = meta.get("chartPreviousClose", price)
            change = ((price - prev) / prev * 100) if prev else 0
            currency = meta.get("currency", "USD")
            arrow = "🟢" if change >= 0 else "🔴"
            sign = "+" if change >= 0 else ""
            lines.append(f"{arrow} *{symbol}* {currency} {price:,.2f} `({sign}{change:.2f}%)`")
        except:
            lines.append(f"⚪ *{symbol}* — niet beschikbaar")
    return "\n".join(lines)

CRYPTO_IDS = {
    "BTC": "bitcoin",
    "ETH": "ethereum",
    "SOL": "solana",
    "XRP": "ripple",
    "DOGE": "dogecoin",
    "BNB": "binancecoin",
    "ADA": "cardano",
    "AVAX": "avalanche-2",
}

def send_message(chat_id, text, parse_mode="Markdown", reply_markup=None):
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": parse_mode,
    }
    if reply_markup:
        payload["reply_markup"] = reply_markup
    requests.post(f"{API_URL}/sendMessage", json=payload)

def send_photo(chat_id, image_bytes, caption=""):
    requests.post(f"{API_URL}/sendPhoto", files={
        "photo": ("chart.png", image_bytes, "image/png"),
    }, data={"chat_id": chat_id, "caption": caption, "parse_mode": "Markdown"})

RANGE_MAP = {
    "1w": ("7d", "1w", "1d"),
    "1m": ("1mo", "1 maand", "1d"),
    "3m": ("3mo", "3 maanden", "1d"),
    "6m": ("6mo", "6 maanden", "1wk"),
    "1j": ("1y", "1 jaar", "1wk"),
}

def get_trend_chart(symbol, range_key="1m"):
    symbol = symbol.upper()
    yahoo_range, label, interval = RANGE_MAP.get(range_key, ("1mo", "1 maand", "1d"))
    try:
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?interval={interval}&range={yahoo_range}"
        res = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
        data = res.json()
        result = data["chart"].get("result")
        if not result:
            return None, f"❌ `{symbol}` niet gevonden."
        meta = result[0]["meta"]
        timestamps = result[0].get("timestamp", [])
        closes = result[0]["indicators"]["quote"][0].get("close", [])
        # Filter None values
        pairs = [(t, p) for t, p in zip(timestamps, closes) if p is not None]
        if not pairs:
            return None, f"❌ Geen data voor `{symbol}`."
        timestamps, closes = zip(*pairs)
        name = meta.get("shortName", symbol)
        currency = meta.get("currency", "USD")
        dates = [datetime.fromtimestamp(t) for t in timestamps]
        prices = list(closes)
        positive = prices[-1] >= prices[0]
        color = "#00e676" if positive else "#ff1744"
        fig, ax = plt.subplots(figsize=(8, 4))
        fig.patch.set_facecolor("#1a1a2e")
        ax.set_facecolor("#1a1a2e")
        ax.plot(dates, prices, color=color, linewidth=2)
        ax.fill_between(dates, prices, min(prices), alpha=0.15, color=color)
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%d %b"))
        ax.tick_params(colors="white", labelsize=8)
        for spine in ax.spines.values():
            spine.set_edgecolor("#333")
        ax.set_title(f"{name} ({symbol}) — {label}", color="white", fontsize=12, pad=10)
        ax.set_ylabel(currency, color="white", fontsize=9)
        plt.tight_layout()
        buf = io.BytesIO()
        plt.savefig(buf, format="png", facecolor=fig.get_facecolor())
        buf.seek(0)
        plt.close()
        change = ((prices[-1] - prices[0]) / prices[0] * 100) if prices[0] else 0
        sign = "+" if change >= 0 else ""
        caption = f"📊 *{name} ({symbol})* — {label}\n💰 Nu: `{currency} {prices[-1]:,.2f}` | Verandering: `{sign}{change:.2f}%`"
        return buf.read(), caption
    except Exception as e:
        return None, f"❌ Fout bij grafiek: {e}"



def get_crypto_price(symbol):
    symbol = symbol.upper()
    coin_id = CRYPTO_IDS.get(symbol)
    if not coin_id:
        return f"❌ Onbekende coin: `{symbol}`\nBeschikbaar: {', '.join(CRYPTO_IDS.keys())}"
    try:
        res = requests.get(
            f"https://api.coingecko.com/api/v3/coins/markets",
            params={
                "vs_currency": "usd",
                "ids": coin_id,
                "price_change_percentage": "24h",
            },
            timeout=10,
        )
        data = res.json()[0]
        price = data["current_price"]
        change = data["price_change_percentage_24h"]
        high = data["high_24h"]
        low = data["low_24h"]
        arrow = "📈" if change >= 0 else "📉"
        sign = "+" if change >= 0 else ""

        if price < 1:
            price_str = f"${price:.6f}"
        else:
            price_str = f"${price:,.2f}"

        return (
            f"{arrow} *{data['name']} ({symbol})*\n"
            f"💰 Prijs: `{price_str}`\n"
            f"📊 24h: `{sign}{change:.2f}%`\n"
            f"🔼 Hoog: `${high:,.2f}`\n"
            f"🔽 Laag: `${low:,.2f}`"
        )
    except Exception as e:
        return f"❌ Fout bij ophalen: {e}"

def get_portfolio(symbols):
    ids = ",".join([CRYPTO_IDS[s.upper()] for s in symbols if s.upper() in CRYPTO_IDS])
    if not ids:
        return "❌ Geen geldige coins."
    try:
        res = requests.get(
            "https://api.coingecko.com/api/v3/coins/markets",
            params={"vs_currency": "usd", "ids": ids, "price_change_percentage": "24h"},
            timeout=10,
        )
        data = res.json()
        lines = ["📋 *Market Overzicht*\n"]
        for coin in data:
            change = coin["price_change_percentage_24h"]
            arrow = "🟢" if change >= 0 else "🔴"
            sign = "+" if change >= 0 else ""
            price = coin["current_price"]
            price_str = f"${price:.6f}" if price < 1 else f"${price:,.2f}"
            lines.append(f"{arrow} *{coin['symbol'].upper()}* {price_str} `({sign}{change:.2f}%)`")
        return "\n".join(lines)
    except Exception as e:
        return f"❌ Fout: {e}"

def handle_message(message):
    chat_id = message["chat"]["id"]
    text = message.get("text", "").strip()

    if not text:
        return

    # Fix voor groepsgesprekken: verwijder @botname uit commands
    if text.startswith("/"):
        text = text.split("@")[0]

    if text == "/start":
        send_message(chat_id,
            "👋 *Welkom bij Road2Rich Bot!*\n\n"
            "📌 *Commands:*\n"
            "/prijs BTC — Live crypto prijs\n"
            "/market — Crypto overzicht\n"
            "/coins — Beschikbare coins\n"
            "/aandeel TTWO — Live aandelenkoers\n"
            "/aandelen — Alle aandelen overzicht\n"
            "/trend AAPL — 30d grafiek van aandeel\n"
            "/grapje — Vertel een grapje 😂\n"
            "/help — Dit menu\n\n"
            "Voorbeeld: `/trend CRWV`"
        )

    elif text == "/help":
        send_message(chat_id,
            "📌 *Commands:*\n"
            "/prijs BTC — Live crypto prijs\n"
            "/market — Crypto overzicht\n"
            "/coins — Beschikbare coins\n"
            "/aandeel TTWO — Live aandelenkoers\n"
            "/aandelen — Alle aandelen overzicht\n"
            "/trend AAPL — 30d grafiek van aandeel\n"
            "/grapje — Vertel een grapje 😂\n"
        )

    elif text == "/grapje":
        grapje = random.choice(GRAPJES)
        send_message(chat_id, f"😂 *Grapje van de dag:*\n\n{grapje}")

    elif text == "/coins":
        coins = ", ".join(CRYPTO_IDS.keys())
        send_message(chat_id, f"✅ *Beschikbare coins:*\n`{coins}`")

    elif text == "/market":
        reply = get_portfolio(list(CRYPTO_IDS.keys()))
        send_message(chat_id, reply)

    elif text == "/aandelen":
        reply = get_all_stocks()
        send_message(chat_id, reply)

    elif text.startswith("/aandeel"):
        parts = text.split()
        if len(parts) < 2:
            send_message(chat_id, "❌ Gebruik: `/aandeel TTWO`")
        else:
            symbol = parts[1].upper()
            reply = get_stock_price(symbol)
            send_message(chat_id, reply)

    elif text.startswith("/trend"):
        parts = text.split()
        if len(parts) < 2:
            send_message(chat_id, "❌ Gebruik: `/trend AAPL`")
        else:
            symbol = parts[1].upper()
            keyboard = {
                "inline_keyboard": [[
                    {"text": "1 week", "callback_data": f"trend_{symbol}_1w"},
                    {"text": "1 maand", "callback_data": f"trend_{symbol}_1m"},
                    {"text": "3 maanden", "callback_data": f"trend_{symbol}_3m"},
                ], [
                    {"text": "6 maanden", "callback_data": f"trend_{symbol}_6m"},
                    {"text": "1 jaar", "callback_data": f"trend_{symbol}_1j"},
                ]]
            }
            send_message(chat_id, f"📊 Welke tijdspanne voor *{symbol}*?", reply_markup=keyboard)

    elif text.startswith("/prijs"):
        parts = text.split()
        if len(parts) < 2:
            send_message(chat_id, "❌ Gebruik: `/prijs BTC`")
        else:
            symbol = parts[1].upper()
            reply = get_crypto_price(symbol)
            send_message(chat_id, reply)

    else:
        if text.startswith("/"):
            send_message(chat_id, "❓ Onbekend commando. Stuur /help voor een overzicht.")

def handle_callback(callback):
    query_id = callback["id"]
    chat_id = callback["message"]["chat"]["id"]
    data = callback.get("data", "")
    # Acknowledge the button press
    requests.post(f"{API_URL}/answerCallbackQuery", json={"callback_query_id": query_id})
    if data.startswith("trend_"):
        parts = data.split("_")
        symbol = parts[1]
        range_key = parts[2]
        send_message(chat_id, f"⏳ Grafiek laden voor `{symbol}`...")
        img, caption = get_trend_chart(symbol, range_key)
        if img:
            send_photo(chat_id, img, caption)
        else:
            send_message(chat_id, caption)

def main():
    print("🚀 Road2Rich Bot gestart!")
    offset = None
    while True:
        try:
            params = {"timeout": 30}
            if offset:
                params["offset"] = offset
            res = requests.get(f"{API_URL}/getUpdates", params=params, timeout=35)
            updates = res.json().get("result", [])
            for update in updates:
                offset = update["update_id"] + 1
                if "message" in update:
                    handle_message(update["message"])
                elif "callback_query" in update:
                    handle_callback(update["callback_query"])
        except Exception as e:
            print(f"Fout: {e}")
            time.sleep(5)
        except Exception as e:
            print(f"Fout: {e}")
            time.sleep(5)

if __name__ == "__main__":
    main()
