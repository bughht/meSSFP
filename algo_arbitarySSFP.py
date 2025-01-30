def arbitarySSFP(start_echo: int, end_echo: int, ascend=None, balance=False):
    assert((start_echo!=end_echo) or (start_echo==end_echo and ascend is not None) or (balance and start_echo==0 and end_echo==0), "when only single echo, the orientation must be specified")

    num_echo = abs(start_echo - end_echo) + 1
    if num_echo!=1:
        ascend=(start_echo<end_echo)
    if ascend:
        idx_echo0 = -start_echo
        sum = -2
    else:
        idx_echo0 = start_echo
        sum = 2
    if balance:
        sum = 0
    a = -(idx_echo0*2+1)
    b = num_echo*2
    c = sum-a-b

    return a,b,c

if __name__ == "__main__":
    print("F+1 to F-2",arbitarySSFP(+1, -2))
    print("F-2 to F+1",arbitarySSFP(-2, +1))
    print("F+2 to F-3",arbitarySSFP(+2, -3))
    print("F-3 to F+2",arbitarySSFP(-3, +2))
    print("F+1 to F-1",arbitarySSFP(+1, -1))

    print("F0, balance",arbitarySSFP(0, 0, None, True))
    print("F0, ascend",arbitarySSFP(0, 0, True))
    print("F0, descend",arbitarySSFP(0, 0, False))
    print("F1, ascend",arbitarySSFP(1, 1, True))
    print("F1, descend",arbitarySSFP(1, 1, False)) 
    print("F-1, ascend",arbitarySSFP(-1, -1, True))
    print("F-1, descend",arbitarySSFP(-1, -1, False))
