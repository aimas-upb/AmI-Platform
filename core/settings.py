KESTREL_SERVERS=['ami-crunch-01.local:22133']
MONGO_SERVER='amilab-daq-10.local:27017'
REDIS_SERVER='amilab-daq-10.local'
REDIS_PORT=6379
REDIS_DASHBOARD_DB=0
REDIS_SESSION_DB=1
REDIS_PROCESSED_SESSION_DB=2

try:
    from settings_local import *
except:
    pass
