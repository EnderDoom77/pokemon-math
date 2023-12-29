from lib.testlib.utest_ui import *
from lib.mathlib import *

run_tests()

print(hsl2rgb((0, 1, 1)))
for t in [0,0.2,0.4,0.6,0.8,1]:
    print(f"Max contrast with tint={t}: {max_contrast((255,255,0), tint=t)}")