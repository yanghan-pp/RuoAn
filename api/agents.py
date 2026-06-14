from api._shared import JsonHandler, core


class handler(JsonHandler):
    def do_GET(self):
        try:
            self.send_json({"agents": core.candidate_pool({})})
        except Exception as exc:
            self.send_error_json(exc)
