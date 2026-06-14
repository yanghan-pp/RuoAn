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
            match = core.build_network_match(profile, demand)
            core.save_match_run(profile, demand, match)
            self.send_json(match)
        except Exception as exc:
            self.send_error_json(exc)
