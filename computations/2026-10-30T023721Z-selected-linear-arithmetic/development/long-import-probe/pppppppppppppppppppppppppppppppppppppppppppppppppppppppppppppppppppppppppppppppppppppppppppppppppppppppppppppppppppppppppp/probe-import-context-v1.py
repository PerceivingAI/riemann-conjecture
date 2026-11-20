import importlib.util,json,os,sys
from pathlib import Path
print(json.dumps({"script_length":len(__file__),"script_directory_length":len(str(Path(__file__).parent)),"sys_path":sys.path,"safe_path":sys.flags.safe_path,"pythonpath":os.environ.get("PYTHONPATH"),"implicit_helper":str(importlib.util.find_spec("resource_limits_v1"))}),flush=True)
sys.path.insert(0,str(Path(__file__).parent))
print(json.dumps({"explicit_helper":str(importlib.util.find_spec("resource_limits_v1"))}),flush=True)
