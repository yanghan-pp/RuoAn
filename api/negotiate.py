from api._shared import JsonHandler, core


class handler(JsonHandler):
    def do_POST(self):
        try:
            payload = self.read_json()
            profile = payload.get("profile", {})
            demand = payload.get("demand", "")
            candidates = payload.get("candidates") or core.build_matches(profile, demand)["candidates"]
            result = core.negotiate_candidate(profile, demand, candidates[0], True)
            self.send_json({**result, "candidates": candidates})
        except Exception as exc:
            self.send_error_json(exc)
