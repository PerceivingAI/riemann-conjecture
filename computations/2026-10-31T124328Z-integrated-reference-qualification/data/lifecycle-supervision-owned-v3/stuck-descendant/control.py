from pathlib import Path
import subprocess,sys,time,json
child=subprocess.Popen([sys._base_executable,'-B','-c','import time;time.sleep(60)'])
Path(__file__).with_name('descendant.json').write_text(json.dumps({'pid':child.pid}))
while True:
    try: time.sleep(.05)
    except KeyboardInterrupt: pass
