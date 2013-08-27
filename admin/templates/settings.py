KESTREL_SERVERS=['{{kestrel_server}}:{{kestrel_port}}']
MONGO_SERVER='{{mongo_server}}:{{mongo_port}}'
REDIS_SERVER='{{redis_server}}'
REDIS_PORT={{redis_port}}

REDIS_DASHBOARD_DB=0
REDIS_SESSION_DB=1
REDIS_PROCESSED_SESSION_DB=2

try:
    from settings_local import *
except:
    pass
