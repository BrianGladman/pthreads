
from __future__ import print_function

from os import chdir, walk
from os.path import join, dirname, normpath, split, splitext
import shutil
import string
import copy
import subprocess
import code
import sys
import re
from time import sleep

# timeout for running each test
test_time_limit = 60

vs_version = 19
if len(sys.argv) > 1:
  vs_version = int(sys.argv[1])

build_dir_name = 'build.vs'

script_dir = dirname(__file__)
chdir(script_dir)
t = join(script_dir, '..\\..\\' + build_dir_name)
exe_dir = normpath(join(t, 'build_tests'))

def split_pnx(p):
  h, t = split(p)
  n, x = splitext(t)
  if x == '.filters':
    n, _ = splitext(x)
  return (h, n, x)

exe = []
for root, dirs, files in walk(exe_dir, topdown=False):
  for x in files:
    h, t = splitext(x)
    if t == '.exe':
      exe.append(join(root, x))

build_fail = 0
run_ok = 0
run_fail = 0
timed_out_fail = 0
print(len(exe))

fails, timed_out = [], []
for ef in exe:
  fdn, fx = splitext(ef)
  fd, fn = split(fdn)
  fd = fd[fd.find('tests') + 6 : fd.find('\\x64\\')]
  fd = fd + ': ' + fn
  print(fd)
  try:
    prc = subprocess.Popen( ef, stdout = subprocess.PIPE,
      stderr = subprocess.STDOUT, creationflags = 0x08000000 )
  except Exception as str:
    print(fd, ' ... ERROR (', str, ')')
    run_fail += 1
    continue
  for _ in range(test_time_limit):
    sleep(1)
    if prc.poll() is not None:
      output = prc.communicate()[0]
      break
  else:
    print(fd + '... ERROR (test timed out)')
    prc.kill()
    timed_out_fail += 1
    timed_out += [fd]
    continue
  if output:
    op = output.decode().replace('\n', '')
  if prc.returncode:
    t = fd + ' ...ERROR {}'.format(prc.returncode)
    print(t, end=' ')
    fails += [t + ' ' + op]
    run_fail += 1
  else:
    run_ok += 1
  if output:
    op = output.decode().replace('\n', '')
    if 'PASS' in op:
      print(fd + ' ... PASS')
    elif 'SKIPPED' in op:
      print(fd + ' ... SKIPPED')
    else:
      print('output from ' + op)
  else:
    print()
#  else:
#    print("Build failure for {0}".format(i))
#    build_fail += 1
print(build_fail + run_ok + run_fail, "tests:")
if build_fail > 0:
  print("\t{0} failed to build".format(build_fail))
if run_ok > 0:
  print("\t{0} ran correctly".format(run_ok))
if run_fail > 0:
  print("\t{0} failed".format(run_fail))
if timed_out_fail > 0:
  print("\t{0} timed out".format(timed_out_fail))

print('Failed:')
for t in fails:
  print(t)
print('Timed out:')
for t in timed_out:
  print(t)

if len(sys.argv) == 1:
  try:
    input(".. completed - press ENTER")
  except:
    pass
else:
  sys.exit(build_fail + run_fail)
