

from quafu import *

task = Task()
task.load_account()
task.config(backend="ScQ-P10", shots=8196, compile=True)
task.get_backend_info()
# res = task.send(circuit)
