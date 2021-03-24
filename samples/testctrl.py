import time
import sys

for i in range(100):
    sys.stdout.write(str(i+1) + '%\r')
    sys.stdout.flush()
    time.sleep(0.1)