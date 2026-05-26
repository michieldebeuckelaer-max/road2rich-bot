import requests
import time

BOT_TOKEN = "8901013849:AAGXWFh0HnYJgvryPa3kZLRH4uvg9sCmlHQ"
API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"

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
            "/prijs BTC — Live prijs van een coin\n"
            "/market — Overzicht van top coins\n"
            "/coins — Alle beschikbare coins\n"
            "/help — Dit menu\n\n"
            "Voorbeeld: `/prijs SOL`"
        )

    elif text == "/help":
        send_message(chat_id,
            "📌 *Commands:*\n"
            "/prijs BTC — Live prijs van een coin\n"
            "/market — Overzicht van top coins\n"
            "/coins — Alle beschikbare coins\n"
        )

    elif text == "/coins":
        coins = ", ".join(CRYPTO_IDS.keys())
        send_message(chat_id, f"✅ *Beschikbare coins:*\n`{coins}`")

    elif text == "/market":
        reply = get_portfolio(list(CRYPTO_IDS.keys()))
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
