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

---

## 🦅 v2.1 - 멀티 인디케이터

### 지표 (Indicators)

| 지표 | 설명 | 매수 | 매도 |
|------|------|------|------|
| **RSI** | 상대강도지수 | < 30 | > 70 |
| **MACD** | 이평선 수렴확산 | 골든크로스 | 데드크로스 |
| **CCI** | 상품채널지수 | < -100 | > 100 |
| **Stochastic** | 스토캐스틱 | < 20 | > 80 |

### Confluence (신호 일치도)

`3B/1S` = 3개 매수 신호, 1개 매도 신호

- **3+ 일치** → 강한 신호 (LONG/SHORT)
- **2개 일치** → 관찰 필요 (WATCH)
- **0-1개** → 대기 (WAIT)

---

## ☁️ v2.2 - 일목균형표 (Ichimoku Cloud)

### 일목균형표 구성요소

| 요소 | 일본어 | 계산 |
|------|--------|------|
| 전환선 | Tenkan-sen | (9일 고가 + 9일 저가) / 2 |
| 기준선 | Kijun-sen | (26일 고가 + 26일 저가) / 2 |
| 선행스팬A | Senkou A | (전환선 + 기준선) / 2 |
| 선행스팬B | Senkou B | (52일 고가 + 52일 저가) / 2 |

### 신호 해석

| 상태 | 의미 |
|------|------|
| `ABOVE_CLOUD` | 구름 위 = 강세 |
| `BELOW_CLOUD` | 구름 아래 = 약세 |
| `IN_CLOUD` | 구름 안 = 전환 중 |
| `STRONG_BULLISH` | 삼역호전 (구름위 + 양운 + TK골든) |
| `STRONG_BEARISH` | 삼역역전 (구름아래 + 음운 + TK데드) |
