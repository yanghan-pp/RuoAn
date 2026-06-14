try:
    from api._shared import JsonHandler, get_core
except ModuleNotFoundError:
    from _shared import JsonHandler, get_core


class handler(JsonHandler):
    def do_POST(self):
        try:
            core = get_core()
            payload = self.read_json()
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
            core.save_created_agent(profile, agent)
            self.send_json({"agent": agent})
        except Exception as exc:
            self.send_error_json(exc)
