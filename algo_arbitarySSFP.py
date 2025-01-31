def arbitarySSFP(start_echo: int, end_echo: int, ascend=None, balance=False):
    if start_echo==end_echo and ascend is None and not balance:
        raise ValueError("when only single echo, the orientation must be specified")
    if balance and start_echo!=0 and end_echo!=0:
        raise ValueError("when balance, start_echo and end_echo must be 0")

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

def arbitarySSFP_Spoiler(start_echo: int, end_echo: int, ascend=None, balance=False, spoiler_portion=0.0):
    a,b,c = arbitarySSFP(start_echo=start_echo, end_echo=end_echo, ascend=ascend, balance=balance)
    num_echo = abs(start_echo - end_echo) + 1
    a = a*(1+spoiler_portion)+spoiler_portion
    b = ([2, spoiler_portion*2]*num_echo)[:-1]
    c = c*(1+spoiler_portion)+spoiler_portion

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

    print("F+1 to F-2",arbitarySSFP_Spoiler(+1, -2, spoiler_portion=1))
    print("F-2 to F+1",arbitarySSFP_Spoiler(-2, +1, spoiler_portion=1))
    print("F+2 to F-3",arbitarySSFP_Spoiler(+2, -3, spoiler_portion=1))
    print("F-3 to F+2",arbitarySSFP_Spoiler(-3, +2, spoiler_portion=1))
    print("F0, balance",arbitarySSFP_Spoiler(0, 0, balance=True, spoiler_portion=1))
