import matplotlib.pyplot as plt
import numpy as np


def arbitarySSFP(start_echo: int, end_echo: int, ascend=None, balance=False):
    if start_echo == end_echo and ascend is None and not balance:
        raise ValueError(
            "when only single echo, the orientation must be specified")
    if balance and start_echo != 0 and end_echo != 0:
        raise ValueError("when balance, start_echo and end_echo must be 0")

    num_echo = abs(start_echo - end_echo) + 1
    if num_echo != 1:
        ascend = (start_echo < end_echo)
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

    return a, b, c


def arbitarySSFP_Spoiler(start_echo: int, end_echo: int, ascend=None, balance=False, spoiler_portion=0.0):
    a, b, c = arbitarySSFP(start_echo=start_echo,
                           end_echo=end_echo, ascend=ascend, balance=balance)
    num_echo = abs(start_echo - end_echo) + 1
    a = a*(1+spoiler_portion)+spoiler_portion
    b = ([2, spoiler_portion*2]*num_echo)[:-1]
    c = c*(1+spoiler_portion)+spoiler_portion

    return a, b, c


def EPG_plot(start_echo, end_echo, ascend=None, balance=False, spoiler_portion=0.0):
    num_echo = abs(start_echo - end_echo) + 1
    if spoiler_portion != 0:
        a, b, c = arbitarySSFP_Spoiler(
            start_echo, end_echo, ascend, balance, spoiler_portion=spoiler_portion)
    else:
        a, b, c = arbitarySSFP(start_echo, end_echo, ascend, balance)
    print("a:{} b:{} c:{}".format(a, b, c))
    axis_y = 0
    plt.figure()
    plt.subplot(211)
    plt.axhline(y=axis_y, color='k', linestyle='--')

    def plot_block(t, duration, amplitude, c='b', alpha=0.5):
        block_x = [t, t, t+duration, t+duration]
        block_y = [axis_y, axis_y+amplitude, axis_y+amplitude, axis_y]
        plt.plot(block_x, block_y, 'k')
        plt.fill(block_x, block_y, c=c, alpha=alpha)
    t_list = []
    t = 0
    t_list.append(t)
    plot_block(t, 1, a, c='r')
    t += 1
    t_list.append(t)
    if type(b) == int:
        plot_block(t, b, 1, c='g')
        echo_t = t+1+np.arange(num_echo)*2
        t += b
        t_list.append(t)
        for echo_t_ in echo_t:
            plt.subplot(212)
            plt.axvline(x=echo_t_, color='darkgreen', linestyle='--')
            plt.scatter(echo_t_, 0, c='k', marker='o')
            plt.subplot(211)
            plt.axvline(x=echo_t_, color='darkgreen', linestyle='--')
    else:
        for idx, b_ in enumerate(b):
            if idx % 2 == 0:  # RO
                plt.subplot(212)
                plt.axvline(x=t+1, color='darkgreen', linestyle='--')
                plt.scatter(t+1, 0, c='k', marker='o')
                plt.subplot(211)
                plt.axvline(x=t+1, color='darkgreen', linestyle='--')
                plot_block(t, 2, b_/2, c='g')
                t += 2
                t_list.append(t)
            else:  # spoiler
                plot_block(t, 1, b_, c='c')
                t += 1
                t_list.append(t)
    plot_block(t, 1, c, c='r')
    t += 1
    t_list.append(t)

    plt.subplot(212)
    plt.axhline(y=axis_y, color='k', linestyle='--')
    if type(b) == int:
        phase_evolution = np.concatenate(
            ([0], np.cumsum(np.concatenate(([a], [b], [c])))))
    else:
        phase_evolution = np.concatenate(
            ([0], np.cumsum(np.concatenate(([a], b, [c])))))

    if balance == True:
        plt.plot(t_list, phase_evolution, 'k')
    else:
        for idx in np.linspace(start_echo, end_echo, num_echo, endpoint=True):
            plt.plot(t_list, phase_evolution+idx*phase_evolution[-1], 'k')

    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    print("F+1 to F-2", arbitarySSFP(+1, -2))
    print("F-2 to F+1", arbitarySSFP(-2, +1))
    print("F+2 to F-3", arbitarySSFP(+2, -3))
    print("F-3 to F+2", arbitarySSFP(-3, +2))
    print("F+1 to F-1", arbitarySSFP(+1, -1))

    print("F0, balance", arbitarySSFP(0, 0, None, True))
    print("F0, ascend", arbitarySSFP(0, 0, True))
    print("F0, descend", arbitarySSFP(0, 0, False))
    print("F1, ascend", arbitarySSFP(1, 1, True))
    print("F1, descend", arbitarySSFP(1, 1, False))
    print("F-1, ascend", arbitarySSFP(-1, -1, True))
    print("F-1, descend", arbitarySSFP(-1, -1, False))

    print("F+1 to F-2", arbitarySSFP_Spoiler(+1, -2, spoiler_portion=1))
    print("F-2 to F+1", arbitarySSFP_Spoiler(-2, +1, spoiler_portion=1))
    print("F+2 to F-3", arbitarySSFP_Spoiler(+2, -3, spoiler_portion=1))
    print("F-3 to F+2", arbitarySSFP_Spoiler(-3, +2, spoiler_portion=1))
    print("F0, balance", arbitarySSFP_Spoiler(
        0, 0, balance=True, spoiler_portion=1))

    # EPG_plot(0, 0, balance=True)
    EPG_plot(1, 4, spoiler_portion=1.3)
    EPG_plot(+1, -2, spoiler_portion=1.5)
    EPG_plot(-2, +1, spoiler_portion=1.5)
    EPG_plot(0, -1, spoiler_portion=1.5)
    EPG_plot(+1, 0, spoiler_portion=1.5)
