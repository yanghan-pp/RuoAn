try:
    from api._shared import JsonHandler, get_core
except ModuleNotFoundError:
    from _shared import JsonHandler, get_core
import os


class handler(JsonHandler):
    def do_GET(self):
        try:
            core = get_core()
            self.send_json({
                "ok": True,
                "arkConfigured": bool(core.ark_api_key()),
                "supabaseConfigured": bool(core.supabase_rest_url() and core.supabase_service_key()),
                "model": os.environ.get("ARK_MODEL", core.ARK_MODEL),
            })
        except Exception as exc:
            self.send_error_json(exc)
