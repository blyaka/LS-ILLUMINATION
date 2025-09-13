import time
def now_ts(_request):
    return {'now_ts': int(time.time())}
