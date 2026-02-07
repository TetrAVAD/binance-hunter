#!/usr/bin/env python3
"""
🦅 Binance Hunter v2.1 - 멀티 인디케이터 + 세력 패턴 감지
Indicators: RSI, MACD, CCI, Stochastic
"""

import requests
import json
import sys
from datetime import datetime

def get_klines(symbol, interval, limit=100):
    """Fetch candlestick data from Binance"""
    url = f"https://api.binance.com/api/v3/klines"
    params = {"symbol": symbol, "interval": interval, "limit": limit}
    try:
        r = requests.get(url, params=params, timeout=10)
        return r.json()
    except:
        return []

def get_ticker(symbol):
    """Get 24h ticker data"""
    url = f"https://api.binance.com/api/v3/ticker/24hr"
    params = {"symbol": symbol}
    try:
        r = requests.get(url, params=params, timeout=10)
        return r.json()
    except:
        return {}

def calculate_ema(data, period):
    """Calculate EMA"""
    if len(data) < period:
        return data[-1] if data else 0
    multiplier = 2 / (period + 1)
    ema = sum(data[:period]) / period
    for price in data[period:]:
        ema = (price - ema) * multiplier + ema
    return ema

def calculate_sma(data, period):
    """Calculate SMA"""
    if len(data) < period:
        return sum(data) / len(data) if data else 0
    return sum(data[-period:]) / period

def calculate_rsi(closes, period=14):
    """Calculate RSI"""
    if len(closes) < period + 1:
        return 50
    deltas = [closes[i] - closes[i-1] for i in range(1, len(closes))]
    gains = [d if d > 0 else 0 for d in deltas]
    losses = [-d if d < 0 else 0 for d in deltas]
    avg_gain = sum(gains[-period:]) / period
    avg_loss = sum(losses[-period:]) / period
    if avg_loss == 0:
        return 100
    rs = avg_gain / avg_loss
    return round(100 - (100 / (1 + rs)), 1)

def calculate_macd(closes, fast=12, slow=26, signal=9):
    """
    Calculate MACD
    Returns: macd_line, signal_line, histogram
    """
    if len(closes) < slow + signal:
        return 0, 0, 0
    
    ema_fast = calculate_ema(closes, fast)
    ema_slow = calculate_ema(closes, slow)
    macd_line = ema_fast - ema_slow
    
    # Calculate MACD for signal line
    macd_values = []
    for i in range(slow, len(closes) + 1):
        ef = calculate_ema(closes[:i], fast)
        es = calculate_ema(closes[:i], slow)
        macd_values.append(ef - es)
    
    signal_line = calculate_ema(macd_values, signal) if len(macd_values) >= signal else macd_line
    histogram = macd_line - signal_line
    
    return round(macd_line, 4), round(signal_line, 4), round(histogram, 4)

def calculate_cci(highs, lows, closes, period=20):
    """
    Calculate CCI (Commodity Channel Index)
    CCI = (Typical Price - SMA) / (0.015 * Mean Deviation)
    """
    if len(closes) < period:
        return 0
    
    # Typical Price = (High + Low + Close) / 3
    tp = [(highs[i] + lows[i] + closes[i]) / 3 for i in range(len(closes))]
    
    # SMA of Typical Price
    tp_sma = calculate_sma(tp, period)
    
    # Mean Deviation
    mean_dev = sum(abs(tp[i] - tp_sma) for i in range(-period, 0)) / period
    
    if mean_dev == 0:
        return 0
    
    cci = (tp[-1] - tp_sma) / (0.015 * mean_dev)
    return round(cci, 1)

def calculate_stochastic(highs, lows, closes, k_period=14, d_period=3):
    """
    Calculate Stochastic Oscillator
    %K = (Current Close - Lowest Low) / (Highest High - Lowest Low) * 100
    %D = SMA of %K
    """
    if len(closes) < k_period:
        return 50, 50
    
    # Calculate %K values
    k_values = []
    for i in range(k_period - 1, len(closes)):
        lowest_low = min(lows[i - k_period + 1:i + 1])
        highest_high = max(highs[i - k_period + 1:i + 1])
        
        if highest_high == lowest_low:
            k_values.append(50)
        else:
            k = ((closes[i] - lowest_low) / (highest_high - lowest_low)) * 100
            k_values.append(k)
    
    k_current = k_values[-1] if k_values else 50
    d_current = calculate_sma(k_values, d_period) if len(k_values) >= d_period else k_current
    
    return round(k_current, 1), round(d_current, 1)

def calculate_volume_analysis(klines):
    """거래량 분석 - 세력 활동 감지"""
    if len(klines) < 20:
        return {"volume_ratio": 1, "volume_trend": "NORMAL", "whale_alert": False}
    
    volumes = [float(k[5]) for k in klines]
    recent_vol = sum(volumes[-5:]) / 5
    avg_vol = sum(volumes[-20:]) / 20
    
    volume_ratio = round(recent_vol / avg_vol, 2) if avg_vol > 0 else 1
    
    if volume_ratio > 3:
        volume_trend = "EXPLOSIVE"
        whale_alert = True
    elif volume_ratio > 2:
        volume_trend = "SURGE"
        whale_alert = True
    elif volume_ratio > 1.5:
        volume_trend = "RISING"
        whale_alert = False
    elif volume_ratio < 0.5:
        volume_trend = "DEAD"
        whale_alert = False
    else:
        volume_trend = "NORMAL"
        whale_alert = False
    
    return {
        "volume_ratio": volume_ratio,
        "volume_trend": volume_trend,
        "whale_alert": whale_alert
    }

def detect_box_range(klines, lookback=20):
    """박스권 감지"""
    if len(klines) < lookback:
        return {"in_box": False, "box_top": 0, "box_bottom": 0, "breakout": None}
    
    highs = [float(k[2]) for k in klines[-lookback:]]
    lows = [float(k[3]) for k in klines[-lookback:]]
    closes = [float(k[4]) for k in klines[-lookback:]]
    
    box_top = max(highs[:-1])
    box_bottom = min(lows[:-1])
    current_price = closes[-1]
    
    box_range = box_top - box_bottom
    box_percent = (box_range / box_bottom * 100) if box_bottom > 0 else 0
    
    in_box = box_percent < 10
    
    breakout = None
    if current_price > box_top * 1.02:
        breakout = "UP"
    elif current_price < box_bottom * 0.98:
        breakout = "DOWN"
    
    return {
        "in_box": in_box,
        "box_top": round(box_top, 4),
        "box_bottom": round(box_bottom, 4),
        "box_percent": round(box_percent, 1),
        "breakout": breakout
    }

def detect_whale_phase(rsi, volume_trend, breakout, price_change_24h):
    """세력 사이클 단계 감지"""
    if volume_trend == "DEAD" and rsi < 40:
        return "ACCUMULATION"
    elif volume_trend in ["SURGE", "EXPLOSIVE"] and breakout == "UP":
        return "MARKUP"
    elif volume_trend in ["SURGE", "EXPLOSIVE"] and rsi > 70:
        return "DISTRIBUTION"
    elif rsi > 65 and price_change_24h < -5:
        return "MARKDOWN"
    else:
        return "NEUTRAL"

def get_indicator_signal(name, value, overbought, oversold):
    """Get signal from indicator"""
    if value >= overbought:
        return "OVERBOUGHT"
    elif value <= oversold:
        return "OVERSOLD"
    else:
        return "NEUTRAL"

def analyze(symbol):
    """Main analysis function with multiple indicators"""
    # Fetch data
    klines_1d = get_klines(symbol, "1d", 50)
    klines_4h = get_klines(symbol, "4h", 50)
    klines_15m = get_klines(symbol, "15m", 50)
    ticker = get_ticker(symbol)
    
    if not klines_4h or not ticker:
        return {"error": "Failed to fetch data"}
    
    # Extract OHLCV
    highs_4h = [float(k[2]) for k in klines_4h]
    lows_4h = [float(k[3]) for k in klines_4h]
    closes_4h = [float(k[4]) for k in klines_4h]
    closes_1d = [float(k[4]) for k in klines_1d]
    closes_15m = [float(k[4]) for k in klines_15m]
    highs_15m = [float(k[2]) for k in klines_15m]
    lows_15m = [float(k[3]) for k in klines_15m]
    
    # Basic metrics
    price = float(ticker.get("lastPrice", 0))
    price_change_24h = float(ticker.get("priceChangePercent", 0))
    
    # === INDICATORS ===
    
    # RSI (14)
    rsi_4h = calculate_rsi(closes_4h)
    rsi_15m = calculate_rsi(closes_15m)
    rsi_1d = calculate_rsi(closes_1d)
    
    # MACD (12, 26, 9)
    macd_line, macd_signal, macd_hist = calculate_macd(closes_4h)
    macd_cross = "BULLISH" if macd_line > macd_signal else "BEARISH"
    
    # CCI (20)
    cci_4h = calculate_cci(highs_4h, lows_4h, closes_4h)
    cci_15m = calculate_cci(highs_15m, lows_15m, closes_15m)
    
    # Stochastic (14, 3)
    stoch_k, stoch_d = calculate_stochastic(highs_4h, lows_4h, closes_4h)
    stoch_cross = "BULLISH" if stoch_k > stoch_d else "BEARISH"
    
    # === INDICATOR SIGNALS ===
    rsi_signal = get_indicator_signal("RSI", rsi_4h, 70, 30)
    cci_signal = get_indicator_signal("CCI", cci_4h, 100, -100)
    stoch_signal = get_indicator_signal("Stoch", stoch_k, 80, 20)
    
    # === CONFLUENCE SCORE ===
    # Count bullish/bearish signals
    bullish_count = 0
    bearish_count = 0
    
    # RSI
    if rsi_4h < 30: bullish_count += 1
    elif rsi_4h > 70: bearish_count += 1
    
    # MACD
    if macd_cross == "BULLISH" and macd_hist > 0: bullish_count += 1
    elif macd_cross == "BEARISH" and macd_hist < 0: bearish_count += 1
    
    # CCI
    if cci_4h < -100: bullish_count += 1
    elif cci_4h > 100: bearish_count += 1
    
    # Stochastic
    if stoch_k < 20 and stoch_cross == "BULLISH": bullish_count += 1
    elif stoch_k > 80 and stoch_cross == "BEARISH": bearish_count += 1
    
    # Volume analysis
    vol_analysis = calculate_volume_analysis(klines_4h)
    
    # Box range detection
    box_analysis = detect_box_range(klines_4h)
    
    # Whale phase detection
    whale_phase = detect_whale_phase(
        rsi_4h, 
        vol_analysis["volume_trend"],
        box_analysis["breakout"],
        price_change_24h
    )
    
    # Trend
    ema_20 = calculate_ema(closes_4h, 20)
    if price > ema_20 * 1.02:
        trend = "BULLISH"
    elif price < ema_20 * 0.98:
        trend = "BEARISH"
    else:
        trend = "NEUTRAL"
    
    # === FINAL SIGNAL ===
    action = "⏸️ WAIT"
    signal_reason = ""
    risk_level = "NORMAL"
    confluence = f"{bullish_count}B/{bearish_count}S"
    
    # Priority 1: Whale danger
    if whale_phase == "DISTRIBUTION":
        action = "🚨 DANGER"
        signal_reason = "세력 설거지 구간! 매수 금지"
        risk_level = "HIGH"
    
    # Priority 2: Breakout with volume
    elif box_analysis["breakout"] == "UP" and vol_analysis["volume_ratio"] > 2:
        action = "⚠️ BREAKOUT"
        signal_reason = f"박스권 상향돌파 + 거래량 {vol_analysis['volume_ratio']}배"
        risk_level = "MEDIUM"
    
    # Priority 3: Strong confluence (3+ indicators agree)
    elif bullish_count >= 3 and trend != "BEARISH":
        action = "🟢 LONG"
        signal_reason = f"다중지표 매수 신호 ({confluence})"
        risk_level = "MEDIUM"
    elif bearish_count >= 3 and trend != "BULLISH":
        action = "🔴 SHORT"
        signal_reason = f"다중지표 매도 신호 ({confluence})"
        risk_level = "MEDIUM"
    
    # Priority 4: Accumulation watch
    elif whale_phase == "ACCUMULATION":
        action = "👀 WATCH"
        signal_reason = "세력 매집 가능성 - 관찰 필요"
        risk_level = "LOW"
    
    # Priority 5: Moderate confluence (2 indicators)
    elif bullish_count >= 2 and bearish_count == 0:
        action = "👀 WATCH"
        signal_reason = f"매수 관심 ({confluence})"
        risk_level = "LOW"
    elif bearish_count >= 2 and bullish_count == 0:
        action = "👀 WATCH"
        signal_reason = f"매도 관심 ({confluence})"
        risk_level = "LOW"
    else:
        signal_reason = f"명확한 시그널 없음 ({confluence})"
    
    return {
        "symbol": symbol,
        "price": price,
        "change_24h": f"{price_change_24h:+.1f}%",
        "trend": trend,
        "indicators": {
            "rsi": {"4h": rsi_4h, "15m": rsi_15m, "signal": rsi_signal},
            "macd": {"line": macd_line, "signal": macd_signal, "hist": macd_hist, "cross": macd_cross},
            "cci": {"4h": cci_4h, "15m": cci_15m, "signal": cci_signal},
            "stoch": {"k": stoch_k, "d": stoch_d, "cross": stoch_cross, "signal": stoch_signal}
        },
        "confluence": confluence,
        "volume": {
            "ratio": vol_analysis["volume_ratio"],
            "trend": vol_analysis["volume_trend"],
            "whale_alert": vol_analysis["whale_alert"]
        },
        "box_range": {
            "in_box": box_analysis["in_box"],
            "breakout": box_analysis["breakout"]
        },
        "whale_phase": whale_phase,
        "action": action,
        "signal_reason": signal_reason,
        "risk_level": risk_level,
        "timestamp": datetime.utcnow().isoformat()
    }

if __name__ == "__main__":
    symbol = sys.argv[1] if len(sys.argv) > 1 else "BTCUSDT"
    if not symbol.endswith("USDT"):
        symbol = symbol.upper() + "USDT"
    result = analyze(symbol)
    print(json.dumps(result, indent=2, ensure_ascii=False))
