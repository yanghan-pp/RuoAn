from api._shared import JsonHandler, core
import os


class handler(JsonHandler):
    def do_GET(self):
        self.send_json({
            "ok": True,
            "arkConfigured": bool(core.ark_api_key()),
            "supabaseConfigured": bool(core.supabase_rest_url() and core.supabase_service_key()),
            "model": os.environ.get("ARK_MODEL", core.ARK_MODEL),
        })
