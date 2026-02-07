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

---

## 🦅 v2.0 - 세력 패턴 감지

### 새로운 기능

```bash
python3 scripts/analyze_v2.py BTCUSDT
```

#### 거래량 분석
- `volume_ratio`: 평균 대비 거래량 비율
- `volume_trend`: DEAD / NORMAL / RISING / SURGE / EXPLOSIVE

#### 박스권 감지
- `in_box`: 박스권 여부
- `breakout`: UP / DOWN / null

#### 세력 사이클 단계 (whale_phase)
| 단계 | 의미 | 행동 |
|------|------|------|
| `ACCUMULATION` | 세력 매집 중 | 👀 관찰 |
| `MARKUP` | 펌핑 중 | ⚠️ 주의 |
| `DISTRIBUTION` | 설거지 중 | 🚨 매수 금지 |
| `MARKDOWN` | 하락 중 | ⏸️ 대기 |

### 시그널 종류
- `🟢 LONG` - 롱 진입
- `🔴 SHORT` - 숏 진입  
- `⚠️ BREAKOUT` - 박스권 돌파
- `🚨 DANGER` - 위험 구간
- `👀 WATCH` - 관찰 필요
- `⏸️ WAIT` - 대기
