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
            demand = payload.get("demand", "")
            candidates = payload.get("candidates") or core.build_matches(profile, demand)["candidates"]
            result = core.negotiate_candidate(profile, demand, candidates[0], True)
            self.send_json({**result, "candidates": candidates})
        except Exception as exc:
            self.send_error_json(exc)
