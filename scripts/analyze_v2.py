#!/usr/bin/env python3
"""
🦅 Binance Hunter v2.2 - 멀티 인디케이터 + 일목균형표 + 세력 패턴
Indicators: RSI, MACD, CCI, Stochastic, Ichimoku Cloud
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
    if len(data) < period:
        return data[-1] if data else 0
    multiplier = 2 / (period + 1)
    ema = sum(data[:period]) / period
    for price in data[period:]:
        ema = (price - ema) * multiplier + ema
    return ema

def calculate_sma(data, period):
    if len(data) < period:
        return sum(data) / len(data) if data else 0
    return sum(data[-period:]) / period

def calculate_rsi(closes, period=14):
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
    if len(closes) < slow + signal:
        return 0, 0, 0
    ema_fast = calculate_ema(closes, fast)
    ema_slow = calculate_ema(closes, slow)
    macd_line = ema_fast - ema_slow
    macd_values = []
    for i in range(slow, len(closes) + 1):
        ef = calculate_ema(closes[:i], fast)
        es = calculate_ema(closes[:i], slow)
        macd_values.append(ef - es)
    signal_line = calculate_ema(macd_values, signal) if len(macd_values) >= signal else macd_line
    histogram = macd_line - signal_line
    return round(macd_line, 4), round(signal_line, 4), round(histogram, 4)

def calculate_cci(highs, lows, closes, period=20):
    if len(closes) < period:
        return 0
    tp = [(highs[i] + lows[i] + closes[i]) / 3 for i in range(len(closes))]
    tp_sma = calculate_sma(tp, period)
    mean_dev = sum(abs(tp[i] - tp_sma) for i in range(-period, 0)) / period
    if mean_dev == 0:
        return 0
    cci = (tp[-1] - tp_sma) / (0.015 * mean_dev)
    return round(cci, 1)

def calculate_stochastic(highs, lows, closes, k_period=14, d_period=3):
    if len(closes) < k_period:
        return 50, 50
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

def calculate_ichimoku(highs, lows, closes, tenkan=9, kijun=26, senkou_b=52):
    """
    일목균형표 (Ichimoku Cloud) 계산
    - 전환선 (Tenkan-sen): (9일 최고 + 9일 최저) / 2
    - 기준선 (Kijun-sen): (26일 최고 + 26일 최저) / 2
    - 선행스팬A (Senkou A): (전환선 + 기준선) / 2, 26일 앞에 표시
    - 선행스팬B (Senkou B): (52일 최고 + 52일 최저) / 2, 26일 앞에 표시
    - 후행스팬 (Chikou): 현재 종가를 26일 뒤에 표시
    """
    if len(closes) < senkou_b:
        return None
    
    # 전환선 (Tenkan-sen) - 9일
    tenkan_high = max(highs[-tenkan:])
    tenkan_low = min(lows[-tenkan:])
    tenkan_sen = (tenkan_high + tenkan_low) / 2
    
    # 기준선 (Kijun-sen) - 26일
    kijun_high = max(highs[-kijun:])
    kijun_low = min(lows[-kijun:])
    kijun_sen = (kijun_high + kijun_low) / 2
    
    # 선행스팬A (Senkou Span A) - 현재 기준 (실제는 26일 앞에 표시)
    senkou_span_a = (tenkan_sen + kijun_sen) / 2
    
    # 선행스팬B (Senkou Span B) - 52일 기준
    senkou_b_high = max(highs[-senkou_b:])
    senkou_b_low = min(lows[-senkou_b:])
    senkou_span_b = (senkou_b_high + senkou_b_low) / 2
    
    # 현재 가격
    current_price = closes[-1]
    
    # 구름 상단/하단
    cloud_top = max(senkou_span_a, senkou_span_b)
    cloud_bottom = min(senkou_span_a, senkou_span_b)
    
    # 구름 색상 (A > B면 양운, A < B면 음운)
    cloud_color = "GREEN" if senkou_span_a > senkou_span_b else "RED"
    
    # 가격 vs 구름 위치
    if current_price > cloud_top:
        price_position = "ABOVE_CLOUD"  # 구름 위 = 강세
    elif current_price < cloud_bottom:
        price_position = "BELOW_CLOUD"  # 구름 아래 = 약세
    else:
        price_position = "IN_CLOUD"     # 구름 안 = 중립/전환중
    
    # TK 크로스 (전환선 vs 기준선)
    tk_cross = "BULLISH" if tenkan_sen > kijun_sen else "BEARISH"
    
    # 신호 판단
    if price_position == "ABOVE_CLOUD" and cloud_color == "GREEN" and tk_cross == "BULLISH":
        signal = "STRONG_BULLISH"  # 삼역호전 (강한 매수)
    elif price_position == "BELOW_CLOUD" and cloud_color == "RED" and tk_cross == "BEARISH":
        signal = "STRONG_BEARISH"  # 삼역역전 (강한 매도)
    elif price_position == "ABOVE_CLOUD":
        signal = "BULLISH"
    elif price_position == "BELOW_CLOUD":
        signal = "BEARISH"
    else:
        signal = "NEUTRAL"
    
    return {
        "tenkan_sen": round(tenkan_sen, 2),      # 전환선
        "kijun_sen": round(kijun_sen, 2),        # 기준선
        "senkou_span_a": round(senkou_span_a, 2), # 선행스팬A
        "senkou_span_b": round(senkou_span_b, 2), # 선행스팬B
        "cloud_top": round(cloud_top, 2),
        "cloud_bottom": round(cloud_bottom, 2),
        "cloud_color": cloud_color,             # GREEN/RED
        "price_position": price_position,       # ABOVE/BELOW/IN_CLOUD
        "tk_cross": tk_cross,                   # TK 크로스
        "signal": signal                        # 종합 신호
    }

def calculate_volume_analysis(klines):
    if len(klines) < 20:
        return {"volume_ratio": 1, "volume_trend": "NORMAL", "whale_alert": False}
    volumes = [float(k[5]) for k in klines]
    recent_vol = sum(volumes[-5:]) / 5
    avg_vol = sum(volumes[-20:]) / 20
    volume_ratio = round(recent_vol / avg_vol, 2) if avg_vol > 0 else 1
    if volume_ratio > 3:
        volume_trend, whale_alert = "EXPLOSIVE", True
    elif volume_ratio > 2:
        volume_trend, whale_alert = "SURGE", True
    elif volume_ratio > 1.5:
        volume_trend, whale_alert = "RISING", False
    elif volume_ratio < 0.5:
        volume_trend, whale_alert = "DEAD", False
    else:
        volume_trend, whale_alert = "NORMAL", False
    return {"volume_ratio": volume_ratio, "volume_trend": volume_trend, "whale_alert": whale_alert}

def detect_box_range(klines, lookback=20):
    if len(klines) < lookback:
        return {"in_box": False, "breakout": None}
    highs = [float(k[2]) for k in klines[-lookback:]]
    lows = [float(k[3]) for k in klines[-lookback:]]
    closes = [float(k[4]) for k in klines[-lookback:]]
    box_top = max(highs[:-1])
    box_bottom = min(lows[:-1])
    current_price = closes[-1]
    box_percent = ((box_top - box_bottom) / box_bottom * 100) if box_bottom > 0 else 0
    in_box = box_percent < 10
    breakout = None
    if current_price > box_top * 1.02:
        breakout = "UP"
    elif current_price < box_bottom * 0.98:
        breakout = "DOWN"
    return {"in_box": in_box, "breakout": breakout}

def detect_whale_phase(rsi, volume_trend, breakout, price_change_24h):
    if volume_trend == "DEAD" and rsi < 40:
        return "ACCUMULATION"
    elif volume_trend in ["SURGE", "EXPLOSIVE"] and breakout == "UP":
        return "MARKUP"
    elif volume_trend in ["SURGE", "EXPLOSIVE"] and rsi > 70:
        return "DISTRIBUTION"
    elif rsi > 65 and price_change_24h < -5:
        return "MARKDOWN"
    return "NEUTRAL"

def analyze(symbol):
    klines_1d = get_klines(symbol, "1d", 60)
    klines_4h = get_klines(symbol, "4h", 60)
    klines_15m = get_klines(symbol, "15m", 60)
    ticker = get_ticker(symbol)
    
    if not klines_4h or not ticker:
        return {"error": "Failed to fetch data"}
    
    highs_4h = [float(k[2]) for k in klines_4h]
    lows_4h = [float(k[3]) for k in klines_4h]
    closes_4h = [float(k[4]) for k in klines_4h]
    closes_1d = [float(k[4]) for k in klines_1d]
    closes_15m = [float(k[4]) for k in klines_15m]
    highs_15m = [float(k[2]) for k in klines_15m]
    lows_15m = [float(k[3]) for k in klines_15m]
    highs_1d = [float(k[2]) for k in klines_1d]
    lows_1d = [float(k[3]) for k in klines_1d]
    
    price = float(ticker.get("lastPrice", 0))
    price_change_24h = float(ticker.get("priceChangePercent", 0))
    
    # Indicators
    rsi_4h = calculate_rsi(closes_4h)
    rsi_15m = calculate_rsi(closes_15m)
    macd_line, macd_signal, macd_hist = calculate_macd(closes_4h)
    macd_cross = "BULLISH" if macd_line > macd_signal else "BEARISH"
    cci_4h = calculate_cci(highs_4h, lows_4h, closes_4h)
    stoch_k, stoch_d = calculate_stochastic(highs_4h, lows_4h, closes_4h)
    stoch_cross = "BULLISH" if stoch_k > stoch_d else "BEARISH"
    
    # 일목균형표 (4H 기준)
    ichimoku = calculate_ichimoku(highs_4h, lows_4h, closes_4h)
    
    # 일목균형표 (1D 기준 - 더 신뢰도 높음)
    ichimoku_1d = calculate_ichimoku(highs_1d, lows_1d, closes_1d)
    
    # Confluence count
    bullish_count = 0
    bearish_count = 0
    
    if rsi_4h < 30: bullish_count += 1
    elif rsi_4h > 70: bearish_count += 1
    
    if macd_cross == "BULLISH" and macd_hist > 0: bullish_count += 1
    elif macd_cross == "BEARISH" and macd_hist < 0: bearish_count += 1
    
    if cci_4h < -100: bullish_count += 1
    elif cci_4h > 100: bearish_count += 1
    
    if stoch_k < 20 and stoch_cross == "BULLISH": bullish_count += 1
    elif stoch_k > 80 and stoch_cross == "BEARISH": bearish_count += 1
    
    # 일목균형표 신호 추가
    if ichimoku:
        if ichimoku["signal"] == "STRONG_BULLISH": bullish_count += 2
        elif ichimoku["signal"] == "BULLISH": bullish_count += 1
        elif ichimoku["signal"] == "STRONG_BEARISH": bearish_count += 2
        elif ichimoku["signal"] == "BEARISH": bearish_count += 1
    
    vol_analysis = calculate_volume_analysis(klines_4h)
    box_analysis = detect_box_range(klines_4h)
    whale_phase = detect_whale_phase(rsi_4h, vol_analysis["volume_trend"], box_analysis["breakout"], price_change_24h)
    
    ema_20 = calculate_ema(closes_4h, 20)
    if price > ema_20 * 1.02:
        trend = "BULLISH"
    elif price < ema_20 * 0.98:
        trend = "BEARISH"
    else:
        trend = "NEUTRAL"
    
    # Final Signal
    action = "⏸️ WAIT"
    signal_reason = ""
    risk_level = "NORMAL"
    confluence = f"{bullish_count}B/{bearish_count}S"
    
    if whale_phase == "DISTRIBUTION":
        action = "🚨 DANGER"
        signal_reason = "세력 설거지 구간! 매수 금지"
        risk_level = "HIGH"
    elif box_analysis["breakout"] == "UP" and vol_analysis["volume_ratio"] > 2:
        action = "⚠️ BREAKOUT"
        signal_reason = f"박스권 상향돌파 + 거래량 {vol_analysis['volume_ratio']}배"
        risk_level = "MEDIUM"
    elif ichimoku and ichimoku["signal"] == "STRONG_BULLISH" and bullish_count >= 3:
        action = "🟢 STRONG LONG"
        signal_reason = f"삼역호전 + 다중지표 매수 ({confluence})"
        risk_level = "MEDIUM"
    elif ichimoku and ichimoku["signal"] == "STRONG_BEARISH" and bearish_count >= 3:
        action = "🔴 STRONG SHORT"
        signal_reason = f"삼역역전 + 다중지표 매도 ({confluence})"
        risk_level = "MEDIUM"
    elif bullish_count >= 4:
        action = "🟢 LONG"
        signal_reason = f"다중지표 강한 매수 신호 ({confluence})"
        risk_level = "MEDIUM"
    elif bearish_count >= 4:
        action = "🔴 SHORT"
        signal_reason = f"다중지표 강한 매도 신호 ({confluence})"
        risk_level = "MEDIUM"
    elif whale_phase == "ACCUMULATION":
        action = "👀 WATCH"
        signal_reason = "세력 매집 가능성 - 관찰 필요"
        risk_level = "LOW"
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
    
    result = {
        "symbol": symbol,
        "price": price,
        "change_24h": f"{price_change_24h:+.1f}%",
        "trend": trend,
        "indicators": {
            "rsi": {"4h": rsi_4h, "15m": rsi_15m},
            "macd": {"cross": macd_cross, "hist": macd_hist},
            "cci": cci_4h,
            "stoch": {"k": stoch_k, "d": stoch_d, "cross": stoch_cross}
        },
        "ichimoku": ichimoku,
        "ichimoku_1d": ichimoku_1d,
        "confluence": confluence,
        "volume": vol_analysis,
        "whale_phase": whale_phase,
        "action": action,
        "signal_reason": signal_reason,
        "risk_level": risk_level,
        "timestamp": datetime.utcnow().isoformat()
    }
    return result

if __name__ == "__main__":
    symbol = sys.argv[1] if len(sys.argv) > 1 else "BTCUSDT"
    if not symbol.endswith("USDT"):
        symbol = symbol.upper() + "USDT"
    result = analyze(symbol)
    print(json.dumps(result, indent=2, ensure_ascii=False))
