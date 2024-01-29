"""
app inforcer
"""

import casbin
from krispcall.common.app_settings.app_settings import Settings
from krispcall.common.database.connection import DbConnection
# from krispcall.permission.service_layer.messagebus import RedisWatcher
# from krispcall.permission.adapters.casbin_adapter import DatabasesAdapter


class AppEnforcer:
    """
    enforcer = [] first item in this list is enforcer object after connection.
    """

    # enforcer = []

    def __init__(self, settings: Settings, db_conn: DbConnection):
        self.db_conn = db_conn
        self._redis_dsn = settings.redis_settings
        self.base_path = settings.base_path
        self.enforcer = None

    async def connect(self):
        adapter = DatabasesAdapter(self.db_conn)
        if not self.enforcer:
            # maybe path absolute path is required
            casbin_conf = self.base_path.joinpath("config/casbin_model.conf")
            # default_policies = self.base_path.joinpath("config/policy.csv")
            e = casbin.Enforcer(str(casbin_conf), None)
            e.set_adapter(adapter)
            if not e.is_filtered():
                await e.load_policy()

            watcher = RedisWatcher(self._redis_dsn.host, self._redis_dsn.port)
            watcher.set_update_callback(e.load_policy)
            e.set_watcher(watcher)
            self.enforcer = e
            return self.enforcer

    async def disconnect(self):
        pass
