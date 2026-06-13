#!/usr/bin/env python3
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from pathlib import Path
import json
import os
import re
import subprocess
import sys
import time
import urllib.error
import urllib.request


ROOT = Path(__file__).resolve().parent
HTML_PATH = ROOT / "agent-network-demo.html"
AGENT_DB_PATH = ROOT / "local-agent-db.json"
ARK_API_URL = "https://ark.cn-beijing.volces.com/api/v3/responses"
ARK_MODEL = "deepseek-v4-pro-260425"
ARK_API_KEY = ""


def ark_api_key():
    return os.environ.get("ARK_API_KEY") or ARK_API_KEY


def save_created_agent(profile, agent):
    if AGENT_DB_PATH.exists():
        try:
            data = json.loads(AGENT_DB_PATH.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            data = {"agents": []}
    else:
        data = {"agents": []}
    data.setdefault("agents", []).append({
        "recordId": f"agent-{int(time.time() * 1000)}",
        "createdAt": int(time.time()),
        "profile": profile,
        "agent": agent,
    })
    AGENT_DB_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

AGENTS = [
    {
        "id": "ran",
        "agent": "Ran.ai",
        "name": "林然",
        "role": "AI 前端工程师",
        "summary": "擅长 React、交互动效、Agent 网络可视化和快速原型。",
        "skills": ["AI 前端", "React", "交互原型", "快速 Demo", "可视化", "多 Agent"],
        "interests": ["黑客松", "教育产品", "Agent 产品"],
        "availability": "今晚可投入 4 小时",
        "style": "任务清晰、快速合并、愿意今晚真人同步",
        "collaboration": ["快节奏", "明确分工", "技术主力", "今晚同步"],
        "base": 58,
        "avatar": "林",
    },
    {
        "id": "maya",
        "agent": "Maya.ai",
        "name": "Maya",
        "role": "教育产品设计师",
        "summary": "擅长教育场景、用户故事、课堂流程和 pitch 叙事。",
        "skills": ["教育产品", "用户研究", "场景设计", "Pitch", "校园场景"],
        "interests": ["AI 教育", "黑客松", "用户增长"],
        "availability": "明早前可交付 3 个核心场景",
        "style": "适合补充产品叙事，不作为技术主力",
        "collaboration": ["产品叙事", "用户研究", "明早交付", "非技术主力"],
        "base": 52,
        "avatar": "M",
    },
    {
        "id": "yi",
        "agent": "Yi.ai",
        "name": "陈亦",
        "role": "多 Agent 后端开发者",
        "summary": "关注 Agent 消息协议、后端模拟层和多 Agent 协作机制。",
        "skills": ["多 Agent", "后端", "协议", "Python", "消息系统"],
        "interests": ["Agent 网络", "技术实验", "黑客松"],
        "availability": "今晚可短会，适合第二阶段加入",
        "style": "偏技术实验，适合搭协议模拟层",
        "collaboration": ["技术实验", "后端支持", "协议设计", "第二阶段"],
        "base": 49,
        "avatar": "亦",
    },
    {
        "id": "sara",
        "agent": "Sara.ai",
        "name": "Sara",
        "role": "品牌视觉设计师",
        "summary": "擅长品牌视觉、演示页、视觉系统和科技感界面。",
        "skills": ["视觉设计", "品牌", "界面设计", "演示页"],
        "interests": ["AI 产品", "设计系统"],
        "availability": "今晚可给视觉建议",
        "style": "适合作为视觉补充候选",
        "collaboration": ["视觉补充", "界面审美", "品牌表达"],
        "base": 38,
        "avatar": "S",
    },
    {
        "id": "noah",
        "agent": "Noah.ai",
        "name": "Noah",
        "role": "Web3 社区运营",
        "summary": "擅长社区增长和活动运营，但与本次技术 demo 需求较远。",
        "skills": ["Web3", "社区", "增长", "活动运营"],
        "interests": ["社区网络", "用户增长"],
        "availability": "本周末可聊",
        "style": "低优先级，不建议现在介入",
        "collaboration": ["社区增长", "活动运营", "异步沟通"],
        "base": 24,
        "avatar": "N",
    },
]

KEYWORD_ALIASES = {
    "AI 前端": ["ai 前端", "前端", "react", "界面", "交互", "可视化"],
    "教育产品": ["教育", "学习", "课堂", "校园"],
    "快速 Demo": ["demo", "原型", "黑客松", "快速"],
    "多 Agent": ["多 agent", "agent 网络", "agent 互联", "协作"],
    "用户增长": ["增长", "传播", "获客"],
    "协议": ["协议", "后端", "消息", "api"],
    "视觉设计": ["视觉", "品牌", "设计"],
}


def norm(text):
    return (text or "").lower()


def extract_keywords(text):
    haystack = norm(text)
    found = []
    for label, aliases in KEYWORD_ALIASES.items():
        if any(alias in haystack for alias in aliases):
            found.append(label)
    return found or ["快速 Demo"]


def alias_hit(label, text):
    haystack = norm(text)
    return any(alias in haystack for alias in KEYWORD_ALIASES.get(label, [label.lower()]))


def coverage_score(required, offered):
    if not required:
        return 0
    offered_text = norm(" ".join(offered))
    hits = 0
    for label in required:
        if label in offered or alias_hit(label, offered_text):
            hits += 1
    return round(hits / len(required) * 100)


def availability_score(demand, agent):
    text = norm(demand)
    availability = norm(agent["availability"])
    if "今晚" in text:
        if "今晚" in availability:
            return 100
        if "明早" in availability:
            return 65
        return 30
    if "明早" in text or "明天" in text:
        if "明早" in availability or "明天" in availability:
            return 95
        return 55
    return 70


def collaboration_score(demand, agent):
    text = norm(demand)
    signals = {
        "快速": ["快节奏", "明确分工", "技术主力", "今晚同步"],
        "demo": ["快节奏", "明确分工", "技术主力", "界面审美"],
        "产品": ["产品叙事", "用户研究", "品牌表达"],
        "后端": ["后端支持", "协议设计", "技术实验"],
        "增长": ["社区增长", "活动运营"],
    }
    wanted = []
    for word, traits in signals.items():
        if word in text:
            wanted.extend(traits)
    if not wanted:
        wanted = ["明确分工"]
    hits = len(set(wanted) & set(agent.get("collaboration", [])))
    return min(100, round(35 + hits * 22))


def score_agent(agent, intent, profile, demand):
    required = intent["keywords"]
    offered = agent["skills"] + agent["interests"]
    skill = coverage_score(required, agent["skills"])
    interest = coverage_score(required, agent["interests"])
    availability = availability_score(demand, agent)
    collaboration = collaboration_score(demand, agent)
    base_quality = min(100, round(agent["base"] / 60 * 100))
    score = round(
        skill * 0.42
        + interest * 0.18
        + availability * 0.20
        + collaboration * 0.14
        + base_quality * 0.06
    )
    missing = [label for label in required if label not in offered and not alias_hit(label, " ".join(offered))]
    return {
        "score": min(98, max(15, score)),
        "breakdown": {
            "skill": skill,
            "interest": interest,
            "availability": availability,
            "collaboration": collaboration,
            "base": base_quality,
        },
        "missing": missing,
    }


def make_intent(demand):
    keywords = extract_keywords(demand)
    scene = "黑客松 48h 原型" if "黑客松" in demand else "合作机会"
    constraint = "今晚可投入、有明确分工" if "今晚" in demand else "先确认可投入时间"
    boundary = "Agent 先沟通，真人后介入"
    output = "候选人、匹配原因、已确认事项、下一步建议"
    return {
        "keywords": keywords,
        "skills": " / ".join(keywords),
        "scene": scene,
        "constraint": constraint,
        "boundary": boundary,
        "output": output,
    }


def build_matches(profile, demand):
    intent = make_intent(demand)
    candidates = []
    for agent in AGENTS:
        scored = score_agent(agent, intent, profile, demand)
        score = scored["score"]
        reasons = []
        if scored["breakdown"]["skill"] >= 70:
            reasons.append("核心技能覆盖需求")
        if scored["breakdown"]["interest"] >= 50:
            reasons.append("兴趣方向与需求一致")
        if scored["breakdown"]["availability"] >= 90:
            reasons.append("满足时间约束")
        if scored["breakdown"]["collaboration"] >= 70:
            reasons.append("协作风格适配")
        if scored["missing"]:
            reasons.append("缺口：" + "、".join(scored["missing"]))
        if not reasons:
            reasons.append("可作为低优先级候选")
        decision = "auto_negotiate" if score >= 70 else "backup" if score >= 50 else "filtered"
        candidates.append({
            **agent,
            "score": score,
            "breakdown": scored["breakdown"],
            "missing": scored["missing"],
            "decision": decision,
            "reasons": reasons,
        })
    candidates.sort(key=lambda item: item["score"], reverse=True)
    ready = [c for c in candidates if c["decision"] == "auto_negotiate"]
    stats = {
        "scanned": len(AGENTS) * 24 + 8,
        "filtered": len([c for c in candidates if c["decision"] == "filtered"]),
        "contacted": len([c for c in candidates if c["decision"] in ("auto_negotiate", "backup")]),
        "ready": len(ready),
    }
    return {
        "intent": intent,
        "weights": {
            "skill": 0.42,
            "interest": 0.18,
            "availability": 0.20,
            "collaboration": 0.14,
            "base": 0.06,
        },
        "candidates": candidates,
        "stats": stats,
    }


def build_no_match_messages(profile, demand, candidate):
    user_name = profile.get("name") or "用户"
    gaps = "、".join(candidate.get("missing") or ["核心需求"])
    return [
        {
            "speaker": "Qin-01",
            "text": f"我代表 {user_name} 发起合作确认。当前需求是：{demand[:72]}。你的匹配分为 {candidate['score']}%，主要缺口是：{gaps}。",
        },
        {
            "speaker": candidate["agent"],
            "text": f"收到。基于 {candidate['name']} 的资料，当前更适合承担「{candidate['style']}」，无法完整覆盖这次合作的关键要求。",
        },
        {
            "speaker": "Qin-01",
            "text": "我会向用户提示不合适，暂不推进真人引荐，避免浪费双方时间。",
        },
    ]


def build_unsuitable_intro(profile, candidate):
    gaps = "、".join(candidate.get("missing") or ["关键能力不匹配"])
    return {
        "candidate": candidate,
        "brief": [
            ["结论", "不合适，暂不建议发起真人沟通。"],
            ["主要原因", f"匹配度 {candidate['score']}%，缺口：{gaps}。"],
            ["候选定位", f"{candidate['name']} 更适合：{candidate['style']}。"],
            ["下一步", "继续查看其他已达成合作意向的候选，或返回修改需求。"],
        ],
        "slots": [],
        "status": "not_suitable",
        "createdAt": int(time.time()),
    }


def negotiate_candidate(profile, demand, candidate, should_call_ai):
    if should_call_ai:
        result = build_messages(profile, demand, [candidate])
    else:
        result = {
            "messages": build_no_match_messages(profile, demand, candidate),
            "source": "rule",
            "model": "matching-rules",
            "error": "",
        }
    accepted = candidate["score"] >= 70 and not any(gap in ("AI 前端", "快速 Demo") for gap in candidate.get("missing", []))
    intro = build_intro(profile, candidate) if accepted else build_unsuitable_intro(profile, candidate)
    return {
        **result,
        "candidateId": candidate["id"],
        "outcome": "agreement" if accepted else "not_suitable",
        "outcomeText": "已达成合作意向，等待用户确认" if accepted else "不合适",
        "intro": intro,
    }


def build_network_match(profile, demand):
    match = build_matches(profile, demand)
    negotiations = {}
    for index, candidate in enumerate(match["candidates"]):
        should_call_ai = candidate["decision"] in ("auto_negotiate", "backup") and index < 3
        negotiations[candidate["id"]] = negotiate_candidate(profile, demand, candidate, should_call_ai)
    match["negotiations"] = negotiations
    match["stats"]["contacted"] = len(negotiations)
    match["stats"]["ready"] = len([item for item in negotiations.values() if item["outcome"] == "agreement"])
    return match


def extract_response_text(data):
    if isinstance(data, dict):
        if isinstance(data.get("output_text"), str):
            return data["output_text"]
        if isinstance(data.get("text"), str):
            return data["text"]
        output = data.get("output")
        if isinstance(output, list):
            parts = []
            for item in output:
                for content in item.get("content", []):
                    if isinstance(content, dict):
                        if isinstance(content.get("text"), str):
                            parts.append(content["text"])
                        elif isinstance(content.get("output_text"), str):
                            parts.append(content["output_text"])
                if isinstance(item.get("text"), str):
                    parts.append(item["text"])
            if parts:
                return "\n".join(parts)
        choices = data.get("choices")
        if isinstance(choices, list) and choices:
            message = choices[0].get("message", {})
            content = message.get("content")
            if isinstance(content, str):
                return content
    return ""


def parse_json_array(text):
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```(?:json)?", "", cleaned).strip()
        cleaned = re.sub(r"```$", "", cleaned).strip()
    start = cleaned.find("[")
    end = cleaned.rfind("]")
    if start != -1 and end != -1 and end > start:
        cleaned = cleaned[start:end + 1]
    parsed = json.loads(cleaned)
    if not isinstance(parsed, list):
        raise ValueError("AI response is not a JSON array")
    messages = []
    for item in parsed:
        speaker = str(item.get("speaker", "")).strip()
        text = str(item.get("text", "")).strip()
        if speaker and text:
            messages.append({"speaker": speaker, "text": text})
    if not messages:
        raise ValueError("AI response contains no valid messages")
    return messages[:8]


def build_ai_prompt(profile, demand, candidate):
    return f"""
你正在为连连AI生成两个 Agent 的自动沟通记录。

请只返回 JSON 数组，不要返回 Markdown，不要解释。数组元素格式：
{{"speaker":"Qin-01","text":"..."}}

角色：
- Qin-01：用户的个人 Agent，代表用户寻找合作伙伴，需要确认对方是否适合、是否有意愿、如何合作。
- {candidate["agent"]}：候选人的个人 Agent，代表候选人回答能力、时间、合作偏好和边界。

用户资料：
{json.dumps(profile, ensure_ascii=False)}

用户需求：
{demand}

候选 Agent 资料：
{json.dumps(candidate, ensure_ascii=False)}

要求：
1. 生成 4 到 6 轮短对话。
2. 语气像 Agent 间专业沟通，不要像销售文案。
3. 必须明确确认：合作意愿、可投入时间、适合承担的角色、风险或缺口、是否建议真人介入。
4. 如果候选分数或缺口显示不完全匹配，要诚实表达，不要强行说完美匹配。
5. 严格围绕“用户需求”原文，不要替换成法律、律师、招聘、投资等原文没有出现的新需求。
6. Qin-01 的第一句话必须复述当前需求中的关键词，例如 AI 前端、教育产品、快速 demo、Agent 互联平台。
""".strip()


def call_ark_messages(profile, demand, candidate):
    api_key = ark_api_key()
    if not api_key:
        return None
    payload = {
        "model": os.environ.get("ARK_MODEL", ARK_MODEL),
        "stream": False,
        "input": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "input_text",
                        "text": build_ai_prompt(profile, demand, candidate),
                    }
                ],
            }
        ],
    }
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    request = urllib.request.Request(
        ARK_API_URL,
        data=body,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            data = json.loads(response.read().decode("utf-8"))
    except urllib.error.URLError:
        data = call_ark_with_curl(api_key, body)
    return parse_json_array(extract_response_text(data))


def call_ark_with_curl(api_key, body):
    result = subprocess.run(
        [
            "curl",
            "-sS",
            "--location",
            ARK_API_URL,
            "--header",
            f"Authorization: Bearer {api_key}",
            "--header",
            "Content-Type: application/json",
            "--data-binary",
            "@-",
        ],
        input=body,
        capture_output=True,
        timeout=45,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.decode("utf-8", "replace") or "curl request failed")
    text = result.stdout.decode("utf-8", "replace")
    try:
        data = json.loads(text)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"Ark returned non-JSON response: {text[:180]}") from exc
    if "error" in data:
        raise RuntimeError(json.dumps(data["error"], ensure_ascii=False))
    return data


def build_fallback_messages(profile, demand, candidates):
    user_name = profile.get("name") or "用户"
    top = candidates[:3]
    messages = [
        {
            "speaker": "Qin-01",
            "text": f"我代表 {user_name} 寻找合作伙伴。需求是：{demand[:72]}。请确认你的用户是否有合作意愿、可投入时间和适合角色。",
        }
    ]
    if top:
        first = top[0]
        messages.append({
            "speaker": first["agent"],
            "text": f"{first['name']}可以参与。{first['availability']}，核心能力是{first['summary']}偏好：{first['style']}。",
        })
        messages.append({
            "speaker": "Qin-01",
            "text": f"建议分工：{user_name} 负责产品叙事、流程和 pitch；{first['name']} 负责可运行界面和核心交互。是否接受 20 分钟真人同步？",
        })
        messages.append({
            "speaker": first["agent"],
            "text": "接受。建议议程：5 分钟目标对齐，10 分钟拆页面，5 分钟确认 demo 台词和交付边界。",
        })
    for candidate in top[1:]:
        messages.append({
            "speaker": candidate["agent"],
            "text": f"{candidate['name']}的角色建议：{candidate['style']}。匹配度 {candidate['score']}%，可作为{'主候选' if candidate['score'] >= 88 else '补充候选'}。",
        })
    return messages[:6]


def build_messages(profile, demand, candidates):
    if candidates:
        try:
            messages = call_ark_messages(profile, demand, candidates[0])
            if messages:
                return {
                    "messages": messages,
                    "source": "ai",
                    "model": os.environ.get("ARK_MODEL", ARK_MODEL),
                    "error": "",
                }
        except Exception as exc:
            sys.stderr.write(f"AI negotiate fallback: {exc}\n")
            return {
                "messages": build_fallback_messages(profile, demand, candidates),
                "source": "fallback",
                "model": os.environ.get("ARK_MODEL", ARK_MODEL),
                "error": str(exc),
            }
    return {
        "messages": build_fallback_messages(profile, demand, candidates),
        "source": "fallback",
        "model": os.environ.get("ARK_MODEL", ARK_MODEL),
        "error": "ARK_API_KEY is not configured" if not ark_api_key() else "",
    }


def build_intro(profile, candidate):
    user_name = profile.get("name") or "用户"
    return {
        "candidate": candidate,
        "brief": [
            ["会议目的", f"确认 {user_name} 是否与 {candidate['name']} 一起推进连连AI黑客松版本。"],
            ["已确认事项", f"{candidate['name']}：{candidate['availability']}；{candidate['style']}。"],
            ["建议分工", f"{user_name} 负责产品叙事、需求流和 pitch；{candidate['name']} 负责 {candidate['role']} 相关交付。"],
            ["会议议程", "5 分钟目标对齐，10 分钟拆页面，5 分钟确认 demo 台词和交付边界。"],
            ["隐私边界", "发送前仍需用户授权，不自动暴露私人联系方式。"],
        ],
        "slots": [
            ["今晚 20:30 - 20:50", "双方 Agent 均确认可行", True],
            ["今晚 22:00 - 22:20", f"{candidate['name']}可行，用户待确认", False],
            ["明早 09:30 - 09:50", "适合加入更多补充候选", False],
        ],
        "status": "ready_for_user_approval",
        "createdAt": int(time.time()),
    }


class Handler(BaseHTTPRequestHandler):
    server_version = "LianLianAI/0.1"

    def log_message(self, fmt, *args):
        sys.stderr.write("%s - %s\n" % (self.address_string(), fmt % args))

    def _send(self, code, content_type, body):
        encoded = body if isinstance(body, bytes) else body.encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(encoded)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(encoded)

    def _json(self, payload, code=200):
        self._send(code, "application/json; charset=utf-8", json.dumps(payload, ensure_ascii=False))

    def _read_json(self):
        length = int(self.headers.get("Content-Length", "0"))
        raw = self.rfile.read(length).decode("utf-8") if length else "{}"
        return json.loads(raw or "{}")

    def do_GET(self):
        if self.path in ("/", "/agent-network-demo.html"):
            self._send(200, "text/html; charset=utf-8", HTML_PATH.read_text(encoding="utf-8"))
        elif self.path == "/api/health":
            self._json({
                "ok": True,
                "arkConfigured": bool(ark_api_key()),
                "model": os.environ.get("ARK_MODEL", ARK_MODEL),
            })
        elif self.path == "/api/agents":
            self._json({"agents": AGENTS})
        else:
            self._json({"error": "not_found"}, 404)

    def do_POST(self):
        try:
            payload = self._read_json()
            if self.path == "/api/profile":
                profile = payload.get("profile", {})
                name = profile.get("name") or "用户"
                tags = profile.get("tags") or []
                agent = {
                    "id": "qin-01",
                    "name": "Qin-01",
                    "owner": name,
                    "memoryCount": 12 + len(tags),
                    "permissions": ["pre_negotiate", "rank_candidates", "draft_intro"],
                    "privacy": "contact_requires_user_approval",
                }
                save_created_agent(profile, agent)
                self._json({
                    "agent": agent
                })
            elif self.path == "/api/match":
                profile = payload.get("profile", {})
                demand = payload.get("demand", "")
                self._json(build_network_match(profile, demand))
            elif self.path == "/api/negotiate":
                profile = payload.get("profile", {})
                demand = payload.get("demand", "")
                candidates = payload.get("candidates") or build_matches(profile, demand)["candidates"]
                result = negotiate_candidate(profile, demand, candidates[0], True)
                self._json({**result, "candidates": candidates})
            elif self.path == "/api/intro":
                profile = payload.get("profile", {})
                candidate = payload.get("candidate") or build_matches(profile, payload.get("demand", ""))["candidates"][0]
                self._json(build_intro(profile, candidate))
            else:
                self._json({"error": "not_found"}, 404)
        except Exception as exc:
            self._json({"error": "server_error", "detail": str(exc)}, 500)


def main():
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 4190
    server = ThreadingHTTPServer(("0.0.0.0", port), Handler)
    print(f"连连AI running at http://127.0.0.1:{port}/agent-network-demo.html")
    server.serve_forever()


if __name__ == "__main__":
    main()
