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
            candidate = payload.get("candidate") or core.build_matches(profile, payload.get("demand", ""))["candidates"][0]
            self.send_json(core.build_intro(profile, candidate))
        except Exception as exc:
            self.send_error_json(exc)
