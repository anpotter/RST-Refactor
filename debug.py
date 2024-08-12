# debug print function
debugging = False
def debug(*arg):
    if debugging:
        frameinfo = currentframe()
        print(frameinfo.f_back.f_lineno,":",*arg)
        input()
    return None
