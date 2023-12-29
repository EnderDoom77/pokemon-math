from lib.ui.ui_base import *

def run_tests():
    root = Element("Root", (0,0,1000,1000))
    left_display = Element("Left Display", (-100,100,250,500), Anchor((0.5,0),(0.5,0),Pivot((1,0))), root)
    print(left_display.rect)

if __name__ == "__main__":
    run_tests()