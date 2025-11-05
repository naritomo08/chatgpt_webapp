"""LangGraph 構築モジュール

拡張版: 質問が天気関連かを簡易判定し、天気 API(Open-Meteo) を呼び出して
最新の気温・風速などをシステムメッセージとして挿入した上でモデルへ渡す。

流れ:
 1. entry: classify
 2a. needs_weather=True -> fetch_weather -> model -> END
 2b. needs_weather=False -> model -> END

追加仕様:
 - 対応都市は簡易マッピング (Tokyo, Osaka, Sapporo, Fukuoka, Nagoya)
 - キーワード ("天気", "気温", "weather", "forecast") を含むと天気要求とみなす
 - 失敗時は例外を握りつぶしてフォールバックし、"Weather fetch failed" を含むメッセージを挿入

注意:
 - 本番利用ではレート制限/キャッシュ/位置特定(GeoIPやユーザー指定) を検討
 - ユーザー入力から生の地名抽出などを高度化する際は NER / 正規化辞書 などを導入
"""
from __future__ import annotations

from typing import TypedDict, List, Dict, Any, Optional
from langgraph.graph import StateGraph, END
import requests
import datetime as _dt


class ChatState(TypedDict, total=False):
        """LangGraph の状態

        keys:
            messages: OpenAI 互換 message 配列
            needs_weather: 直近ユーザ質問が天気要求か
            weather_payload: 取得した天気情報文字列
        """
        messages: List[Dict[str, Any]]
        needs_weather: bool
        weather_payload: str


def build_graph(client):
    """OpenAI 互換クライアントを閉包に取り込んだグラフを生成 (天気ツール付き)。"""

    # ---------------- 判定ノード ---------------- #
    WEATHER_KEYWORDS = ["天気", "気温", "weather", "forecast"]

    CITY_MAP = {
        "東京": (35.68, 139.69),
        "tokyo": (35.68, 139.69),
        "大阪": (34.70, 135.50),
        "osaka": (34.70, 135.50),
        "札幌": (43.06, 141.35),
        "sapporo": (43.06, 141.35),
        "名古屋": (35.17, 136.90),
        "nagoya": (35.17, 136.90),
        "福岡": (33.59, 130.40),
        "fukuoka": (33.59, 130.40),
    }

    def classify(state: ChatState) -> ChatState:
        messages = state["messages"]
        last_user: Optional[Dict[str, Any]] = None
        for m in reversed(messages):
            if m.get("role") == "user":
                last_user = m
                break
        text = (last_user or {}).get("content", "")
        lowered = text.lower()
        needs = any(k in text for k in WEATHER_KEYWORDS) or any(k in lowered for k in WEATHER_KEYWORDS)
        # 都市推定 (最初に一致したもの)
        target_city = None
        for key in CITY_MAP.keys():
            if key in lowered or key in text:
                target_city = key
                break
        state["needs_weather"] = needs
        if target_city:
            state["weather_city_key"] = target_city  # type: ignore
        return state

    # ---------------- 天気取得ノード ---------------- #
    def fetch_weather(state: ChatState) -> ChatState:
        if not state.get("needs_weather"):
            return state
        key = state.get("weather_city_key", "東京")  # type: ignore
        lat, lon = CITY_MAP.get(key, CITY_MAP["東京"])
        url = (
            "https://api.open-meteo.com/v1/forecast?latitude="
            f"{lat}&longitude={lon}&current=temperature_2m,relative_humidity_2m,wind_speed_10m"
        )
        try:
            r = requests.get(url, timeout=5)
            r.raise_for_status()
            data = r.json()
            cur = data.get("current", {})
            temp = cur.get("temperature_2m")
            hum = cur.get("relative_humidity_2m")
            wind = cur.get("wind_speed_10m")
            ts = cur.get("time")
            # ISO 時刻を整形
            try:
                if ts:
                    dt = _dt.datetime.fromisoformat(ts.replace("Z", "+00:00"))
                    ts_local = dt.strftime("%Y-%m-%d %H:%M UTC")
                else:
                    ts_local = "N/A"
            except Exception:
                ts_local = ts or "N/A"
            city_label = key.capitalize() if key.isascii() else key
            summary = (
                f"[Weather Data] {city_label}: 気温 {temp}°C 湿度 {hum}% 風速 {wind}m/s (観測時刻 {ts_local}).\n"
                "この情報は Open-Meteo API から取得した速報値です。AI 応答と併せて参考にしてください。"
            )
        except Exception as e:
            summary = f"[Weather Data] 取得失敗: {type(e).__name__}: {e}"
        # system メッセージとして挿入 (モデルが利用しやすいように)
        state["messages"].append({"role": "system", "content": summary})
        state["weather_payload"] = summary
        return state

    # ---------------- モデル呼び出しノード ---------------- #
    def call_model(state: ChatState) -> ChatState:
        messages = state["messages"]
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
        )
        answer = response.choices[0].message.content
        messages.append({"role": "assistant", "content": answer})
        return {"messages": messages}

    # ---------------- グラフ構築 ---------------- #
    graph_builder = StateGraph(ChatState)
    graph_builder.add_node("classify", classify)
    graph_builder.add_node("weather", fetch_weather)
    graph_builder.add_node("model", call_model)
    graph_builder.set_entry_point("classify")

    # 条件付き遷移
    def route_weather(state: ChatState):  # noqa: D401
        return "weather" if state.get("needs_weather") else "model"

    graph_builder.add_conditional_edges(
        "classify",
        route_weather,
        {"weather": "weather", "model": "model"},
    )
    # weather -> model -> END
    graph_builder.add_edge("weather", "model")
    graph_builder.add_edge("model", END)
    return graph_builder.compile()


__all__ = ["build_graph", "ChatState"]
