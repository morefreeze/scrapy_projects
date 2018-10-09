import subprocess
import tempfile
import sys

def decode(bytes):
    with tempfile.NamedTemporaryFile(delete=False) as f:
        f.write(bytes)
        f.flush()
        try:
            res = subprocess.check_output('node duokan/decode.js %s' % (f.name), shell=True)
        except Exception as e:
            print(e, file=sys.stderr)
            res = {}
    return res
