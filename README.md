# 🦅 Binance Hunter

**"Don't just trade. Hunt."**

AI-powered Binance trading analysis tool with multi-timeframe RSI, MACD, and Bollinger Bands analysis.

## ✨ Features

- ⚡ **Multi-Timeframe Analysis:** Daily, 4H, and 15-minute timeframes
- 📊 **Technical Indicators:** RSI, MACD, Bollinger Bands, EMA
- 🎯 **Smart Signals:** Automated LONG/SHORT/WAIT recommendations
- 🛡️ **Risk Management:** ATR-based Stop Loss & Take Profit
- 💎 **Fee Discount:** Optimized for lowest trading fees

## 🚀 Quick Start

```bash
# Clone the repo
git clone https://github.com/TetrAVAD/binance-hunter.git
cd binance-hunter

# Install dependencies
pip install requests

# Run analysis
python3 scripts/analyze.py BTCUSDT
```

## 📈 Example Output

```json
{
  "symbol": "BTCUSDT",
  "price": 70152.04,
  "trend": "BULLISH",
  "rsi": 42.3,
  "action": "WAIT",
  "entry": null,
  "sl": null,
  "tp": null
}
```

## 🎯 Signal Logic

| Condition | Action |
|-----------|--------|
| RSI < 35 + Uptrend | 🟢 LONG |
| RSI > 65 + Downtrend | 🔴 SHORT |
| Otherwise | ⏸️ WAIT |

## 💰 Get Started with Binance

New to Binance? Sign up with this link for **discounted trading fees**:

👉 **[Sign up for Binance](https://accounts.binance.com/register?ref=GRO_28502_YLP17)** 👈

## 📦 For OpenClaw Users

This is also available as an OpenClaw skill. Copy to your skills folder:

```bash
cp -r binance-hunter ~/.openclaw/skills/
```

## ⚠️ Disclaimer

This tool is for educational purposes only. Cryptocurrency trading involves significant risk. Always do your own research and never trade with money you can't afford to lose.

## 📄 License

MIT License - Free to use and modify.
