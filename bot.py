import requests
import time
import random

BOT_TOKEN = "8901013849:AAGXWFh0HnYJgvryPa3kZLRH4uvg9sCmlHQ"
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

def send_message(chat_id, text, parse_mode="Markdown"):
    requests.post(f"{API_URL}/sendMessage", json={
        "chat_id": chat_id,
        "text": text,
        "parse_mode": parse_mode,
    })

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

    if text == "/start":
        send_message(chat_id,
            "👋 *Welkom bij Road2Rich Bot!*\n\n"
            "📌 *Commands:*\n"
            "/prijs BTC — Live crypto prijs\n"
            "/market — Crypto overzicht\n"
            "/coins — Beschikbare coins\n"
            "/aandeel TTWO — Live aandelenkoers\n"
            "/aandelen — Alle aandelen overzicht\n"
            "/grapje — Vertel een grapje 😂\n"
            "/help — Dit menu\n\n"
            "Voorbeeld: `/aandeel CRWV`"
        )

    elif text == "/help":
        send_message(chat_id,
            "📌 *Commands:*\n"
            "/prijs BTC — Live crypto prijs\n"
            "/market — Crypto overzicht\n"
            "/coins — Beschikbare coins\n"
            "/aandeel TTWO — Live aandelenkoers\n"
            "/aandelen — Alle aandelen overzicht\n"
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

    elif text.startswith("/prijs"):
        parts = text.split()
        if len(parts) < 2:
            send_message(chat_id, "❌ Gebruik: `/prijs BTC`")
        else:
            symbol = parts[1].upper()
            reply = get_crypto_price(symbol)
            send_message(chat_id, reply)

    else:
        send_message(chat_id,
            "❓ Onbekend commando. Stuur /help voor een overzicht."
        )

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
        except Exception as e:
            print(f"Fout: {e}")
            time.sleep(5)

if __name__ == "__main__":
    main()
