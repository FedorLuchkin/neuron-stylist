import sys
import time
if len(sys.argv) != 2:
    print('one argument expected')
else:
    print('sub start')
    print(sys.argv[1])
    time.sleep(7)
    print('sub finish')