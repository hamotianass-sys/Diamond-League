"""دوال البحث في بيانات الدوري. كل الأرقام تأتي من data.csv مباشرة."""
import re
import pandas as pd
from pathlib import Path

DF = pd.read_csv(Path(__file__).parent / "data.csv")


def norm(text: str) -> str:
    """توحيد الإملاء العربي حتى لا تتكرر النقابة بأسماء مختلفة."""
    text = str(text).strip()
    text = re.sub(r"[\u064B-\u065F\u0640]", "", text)  # التشكيل والتطويل
    for a, b in {"أ": "ا", "إ": "ا", "آ": "ا", "ى": "ي", "ة": "ه", "ڤ": "ف"}.items():
        text = text.replace(a, b)
    return text.lower()


DF["key"] = DF["guild"].map(norm)


def _find_guild(name: str):
    key = norm(name)
    rows = DF[DF["key"] == key]
    return key if not rows.empty else None


def _season_ok(season: int):
    return season in set(DF["season"])


def get_winner(season: int):
    if not _season_ok(season):
        return {"error": f"لا توجد بيانات للنسخة {season}"}
    r = DF[(DF.season == season) & (DF["rank"] == 1)].iloc[0]
    return {"season": season, "winner": r.guild, "points": int(r.points)}


def get_ranking(season: int, top: int = 20):
    if not _season_ok(season):
        return {"error": f"لا توجد بيانات للنسخة {season}"}
    d = DF[DF.season == season].sort_values("rank").head(top)
    return {"season": season, "ranking": d[["rank", "guild", "points"]].to_dict("records")}


def guild_in_season(guild: str, season: int):
    key = _find_guild(guild)
    if not key:
        return {"error": f"النقابة {guild} غير موجودة في البيانات"}
    d = DF[(DF.key == key) & (DF.season == season)]
    if d.empty:
        return {"error": f"النقابة {guild} لم تظهر في النسخة {season}"}
    r = d.iloc[0]
    return {"guild": r.guild, "season": season, "rank": int(r["rank"]), "points": int(r.points)}


def guild_total_points(guild: str):
    key = _find_guild(guild)
    if not key:
        return {"error": f"النقابة {guild} غير موجودة في البيانات"}
    d = DF[DF.key == key]
    return {
        "guild": d.iloc[0].guild,
        "total_points": int(d.points.sum()),
        "seasons_played": int(len(d)),
        "seasons": sorted(int(s) for s in d.season),
    }


def guild_history(guild: str):
    key = _find_guild(guild)
    if not key:
        return {"error": f"النقابة {guild} غير موجودة في البيانات"}
    d = DF[DF.key == key].sort_values("season")
    return {
        "guild": d.iloc[0].guild,
        "wins": int((d["rank"] == 1).sum()),
        "history": d[["season", "rank", "points"]].to_dict("records"),
    }


def top_guilds_by_points(n: int = 5):
    g = DF.groupby("key").agg(guild=("guild", "first"), total=("points", "sum"),
                              seasons=("season", "count")).sort_values("total", ascending=False)
    return {"top": g.head(n)[["guild", "total", "seasons"]].to_dict("records")}


def data_info():
    return {"seasons_available": sorted(int(s) for s in DF.season.unique())}


FUNCTIONS = {
    "get_winner": get_winner,
    "get_ranking": get_ranking,
    "guild_in_season": guild_in_season,
    "guild_total_points": guild_total_points,
    "guild_history": guild_history,
    "top_guilds_by_points": top_guilds_by_points,
    "data_info": data_info,
}

# وصف الدوال لـ Claude
TOOL_SCHEMAS = [
    {"name": "get_winner", "description": "بطل نسخة معينة من الدوري.",
     "input_schema": {"type": "object", "properties": {"season": {"type": "integer"}}, "required": ["season"]}},
    {"name": "get_ranking", "description": "ترتيب النقابات ونقاطها في نسخة معينة.",
     "input_schema": {"type": "object", "properties": {"season": {"type": "integer"}, "top": {"type": "integer", "description": "عدد المراكز، الافتراضي 20"}}, "required": ["season"]}},
    {"name": "guild_in_season", "description": "مركز ونقاط نقابة في نسخة معينة.",
     "input_schema": {"type": "object", "properties": {"guild": {"type": "string"}, "season": {"type": "integer"}}, "required": ["guild", "season"]}},
    {"name": "guild_total_points", "description": "مجموع نقاط نقابة عبر كل النسخ المتوفرة وعدد النسخ التي شاركت فيها.",
     "input_schema": {"type": "object", "properties": {"guild": {"type": "string"}}, "required": ["guild"]}},
    {"name": "guild_history", "description": "تاريخ نقابة في كل النسخ: المراكز والنقاط وعدد مرات الفوز.",
     "input_schema": {"type": "object", "properties": {"guild": {"type": "string"}}, "required": ["guild"]}},
    {"name": "top_guilds_by_points", "description": "أفضل النقابات حسب مجموع النقاط عبر كل النسخ.",
     "input_schema": {"type": "object", "properties": {"n": {"type": "integer"}}}},
    {"name": "data_info", "description": "النسخ المتوفرة في البيانات.",
     "input_schema": {"type": "object", "properties": {}}},
]
