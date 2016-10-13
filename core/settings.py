import os

try:
    # Kestrel settings
    AMI_KESTREL_SERVER_IP = os.environ['AMI_KESTREL_SERVER_IP']
    AMI_KESTREL_SERVER_PORT = os.environ['AMI_KESTREL_SERVER_PORT']
    AMI_KESTREL_SERVER = AMI_KESTREL_SERVER_IP + ':' + AMI_KESTREL_SERVER_PORT
    print(AMI_KESTREL_SERVER)

    # Mongo settings
    AMI_MONGO_SERVER_IP = os.environ['AMI_MONGO_SERVER_IP']
    AMI_MONGO_SERVER_PORT = os.environ['AMI_MONGO_SERVER_PORT']
    MONGO_SERVER = AMI_MONGO_SERVER_IP + ':' + AMI_MONGO_SERVER_PORT

    # Redis server
    REDIS_SERVER = os.environ['AMI_REDIS_SERVER_IP']
    REDIS_PORT = os.environ['AMI_REDIS_SERVER_PORT']
    REDIS_DASHBOARD_DB = 0
    REDIS_SESSION_DB = 1
    REDIS_PROCESSED_SESSION_DB = 2
except:
    print('ERROR LOADING ENVIRONMENT VARIABLES')

try:
    from settings_local import *
except:
    pass
