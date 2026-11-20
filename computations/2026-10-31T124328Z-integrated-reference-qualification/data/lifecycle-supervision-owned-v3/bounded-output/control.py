import os,time
os.write(1,b'x'*(5*1024*1024))
time.sleep(5)
