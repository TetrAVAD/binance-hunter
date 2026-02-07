#!/usr/bin/env python3
"""
🦅 Binance Hunter v2.0 - 세력 패턴 감지 업그레이드
Based on: 세력의 이해 - 잡코인 펌핑 메커니즘
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

def calculate_volume_analysis(klines):
    """
    거래량 분석 - 세력 활동 감지
    """
    if len(klines) < 20:
        return {"volume_ratio": 1, "volume_trend": "NORMAL", "whale_alert": False}
    
    volumes = [float(k[5]) for k in klines]
    recent_vol = sum(volumes[-5:]) / 5  # 최근 5봉 평균
    avg_vol = sum(volumes[-20:]) / 20    # 20봉 평균
    
    volume_ratio = round(recent_vol / avg_vol, 2) if avg_vol > 0 else 1
    
    # 거래량 급증 감지 (세력 활동 신호)
    if volume_ratio > 3:
        volume_trend = "EXPLOSIVE"  # 폭발적 증가 - 펌핑/덤핑 가능성
        whale_alert = True
    elif volume_ratio > 2:
        volume_trend = "SURGE"      # 급증 - 주의
        whale_alert = True
    elif volume_ratio > 1.5:
        volume_trend = "RISING"     # 상승 중
        whale_alert = False
    elif volume_ratio < 0.5:
        volume_trend = "DEAD"       # 거래량 고갈 - 매집 가능성
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
    """
    박스권 감지 - 세력의 개미 훈련 구간
    """
    if len(klines) < lookback:
        return {"in_box": False, "box_top": 0, "box_bottom": 0, "breakout": None}
    
    highs = [float(k[2]) for k in klines[-lookback:]]
    lows = [float(k[3]) for k in klines[-lookback:]]
    closes = [float(k[4]) for k in klines[-lookback:]]
    
    box_top = max(highs[:-1])  # 최근 1봉 제외한 최고점
    box_bottom = min(lows[:-1])
    current_price = closes[-1]
    
    box_range = box_top - box_bottom
    box_percent = (box_range / box_bottom * 100) if box_bottom > 0 else 0
    
    # 박스권 판단 (변동폭 10% 이내)
    in_box = box_percent < 10
    
    # 돌파 감지
    breakout = None
    if current_price > box_top * 1.02:  # 2% 이상 상향 돌파
        breakout = "UP"
    elif current_price < box_bottom * 0.98:  # 2% 이상 하향 돌파
        breakout = "DOWN"
    
    return {
        "in_box": in_box,
        "box_top": round(box_top, 4),
        "box_bottom": round(box_bottom, 4),
        "box_percent": round(box_percent, 1),
        "breakout": breakout
    }

def detect_whale_phase(rsi, volume_trend, breakout, price_change_24h):
    """
    세력 사이클 단계 감지
    1. ACCUMULATION (매집) - 낮은 거래량, 낮은 가격
    2. MARKUP (펌핑) - 거래량 증가, 가격 상승
    3. DISTRIBUTION (설거지) - 높은 거래량, 고점 부근
    4. MARKDOWN (하락) - 거래량 감소, 가격 하락
    """
    if volume_trend == "DEAD" and rsi < 40:
        return "ACCUMULATION"  # 🟢 매집 구간 - 세력이 모으는 중
    elif volume_trend in ["SURGE", "EXPLOSIVE"] and breakout == "UP":
        return "MARKUP"  # 🟡 펌핑 중 - 주의해서 참여
    elif volume_trend in ["SURGE", "EXPLOSIVE"] and rsi > 70:
        return "DISTRIBUTION"  # 🔴 설거지 구간 - 위험!
    elif rsi > 65 and price_change_24h < -5:
        return "MARKDOWN"  # ⚫ 하락 구간
    else:
        return "NEUTRAL"

def analyze(symbol):
    """Main analysis function with whale detection"""
    # Fetch data
    klines_1d = get_klines(symbol, "1d", 50)
    klines_4h = get_klines(symbol, "4h", 50)
    klines_15m = get_klines(symbol, "15m", 50)
    ticker = get_ticker(symbol)
    
    if not klines_15m or not ticker:
        return {"error": "Failed to fetch data"}
    
    # Basic metrics
    price = float(ticker.get("lastPrice", 0))
    price_change_24h = float(ticker.get("priceChangePercent", 0))
    
    # RSI calculation
    closes_1d = [float(k[4]) for k in klines_1d]
    closes_4h = [float(k[4]) for k in klines_4h]
    closes_15m = [float(k[4]) for k in klines_15m]
    
    rsi_1d = calculate_rsi(closes_1d)
    rsi_4h = calculate_rsi(closes_4h)
    rsi_15m = calculate_rsi(closes_15m)
    rsi_avg = round((rsi_1d + rsi_4h + rsi_15m) / 3, 1)
    
    # Volume analysis (세력 활동 감지)
    vol_analysis = calculate_volume_analysis(klines_4h)
    
    # Box range detection (박스권 감지)
    box_analysis = detect_box_range(klines_4h)
    
    # Whale phase detection (세력 사이클 단계)
    whale_phase = detect_whale_phase(
        rsi_avg, 
        vol_analysis["volume_trend"],
        box_analysis["breakout"],
        price_change_24h
    )
    
    # Trend determination
    ema_20 = sum(closes_4h[-20:]) / 20 if len(closes_4h) >= 20 else price
    if price > ema_20 * 1.02:
        trend = "BULLISH"
    elif price < ema_20 * 0.98:
        trend = "BEARISH"
    else:
        trend = "NEUTRAL"
    
    # === 개선된 시그널 로직 ===
    action = "WAIT"
    signal_reason = ""
    risk_level = "NORMAL"
    
    # 🔴 위험 시그널 (최우선)
    if whale_phase == "DISTRIBUTION":
        action = "🚨 DANGER"
        signal_reason = "세력 설거지 구간! 매수 금지"
        risk_level = "HIGH"
    
    # 🟡 박스권 돌파 시그널
    elif box_analysis["breakout"] == "UP" and vol_analysis["volume_ratio"] > 2:
        action = "⚠️ BREAKOUT"
        signal_reason = f"박스권 상향돌파 + 거래량 {vol_analysis['volume_ratio']}배"
        risk_level = "MEDIUM"
    
    # 🟢 매집 구간 감지
    elif whale_phase == "ACCUMULATION":
        action = "👀 WATCH"
        signal_reason = "세력 매집 가능성 - 관찰 필요"
        risk_level = "LOW"
    
    # 기존 RSI 로직 (보조)
    elif rsi_avg < 35 and trend == "BULLISH":
        action = "🟢 LONG"
        signal_reason = f"RSI 과매도 + 상승추세"
        risk_level = "MEDIUM"
    elif rsi_avg > 65 and trend == "BEARISH":
        action = "🔴 SHORT"
        signal_reason = f"RSI 과매수 + 하락추세"
        risk_level = "MEDIUM"
    else:
        action = "⏸️ WAIT"
        signal_reason = "명확한 시그널 없음"
    
    return {
        "symbol": symbol,
        "price": price,
        "change_24h": f"{price_change_24h:+.1f}%",
        "trend": trend,
        "rsi": {
            "15m": rsi_15m,
            "4h": rsi_4h,
            "1d": rsi_1d,
            "avg": rsi_avg
        },
        "volume": {
            "ratio": vol_analysis["volume_ratio"],
            "trend": vol_analysis["volume_trend"],
            "whale_alert": vol_analysis["whale_alert"]
        },
        "box_range": {
            "in_box": box_analysis["in_box"],
            "breakout": box_analysis["breakout"],
            "top": box_analysis["box_top"],
            "bottom": box_analysis["box_bottom"]
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
