try:
    from api._shared import JsonHandler, get_core
except ModuleNotFoundError:
    from _shared import JsonHandler, get_core


class handler(JsonHandler):
    def do_GET(self):
        try:
            core = get_core()
            self.send_json({"agents": core.candidate_pool({})})
        except Exception as exc:
            self.send_error_json(exc)
