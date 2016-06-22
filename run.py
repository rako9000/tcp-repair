#!/usr/bin/env python2

import sys, os
import hashlib
from subprocess import Popen, PIPE

str2 = "test_test" * (1 << 20)
str1 = "Test_Test!"

use_ssh = True
ssh = []

src = os.getenv("TCP_SRC", "localhost")
dst = os.getenv("TCP_DST", "localhost")
sport = os.getenv("TCP_SPORT", "12345")
dport = os.getenv("TCP_DPORT", "54321")
ssh_key = os.getenv("TCP_SSHKEY", "")

if src != "localhost":
    if Popen(["scp", "-i", ssh_key, "tcp-create", "root@%s:" % dst]).wait():
        sys.exit(1)
    if Popen(["scp", "-i", ssh_key, "tcp-test.py", "root@%s:" % dst]).wait():
        sys.exit(1)

    ssh = ["ssh", "-i", ssh_key, "root@%s" % dst]

args = ["./tcp-create",
        "--addr", src, "--port", sport, "--seq", "555",
        "--next",
        "--addr", dst, "--port", dport, "--seq", "666",
        "--reverse", "--", "./tcp-test.py"]

p1 = Popen(ssh + args + ["dst"], stdout = PIPE, stdin = PIPE)

args.remove("--reverse");

p2 = Popen(args + ["src"], stdout = PIPE, stdin = PIPE)

p1.stdout.read(5)
p2.stdout.read(5)
p1.stdin.write("start")
p2.stdin.write("start")

p1.stdin.write(str1)
p1.stdin.close()
p2.stdin.write(str2)
p2.stdin.close()

s = p1.stdout.read()
m = hashlib.md5()
m.update(str2)
str2 = m.hexdigest()

if str2 != eval(s):
    print "FAIL", repr(str2), repr(s)
    sys.exit(5);

s = p1.stdout.read()
m = hashlib.md5()
m.update(str1)
str1 = m.hexdigest()

s = p2.stdout.read()
if str1 != eval(s):
    print "FAIL", repr(str1), s
    sys.exit(5);

if p1.wait():
    sys.exit(1)
if p2.wait():
    sys.exit(1)

print "PASS"
