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
    def subplot_id(id):
        if id == "RF":
            # plt.subplot2grid((7, 1), (0, 0), rowspan=1)
            plt.subplot(611)
        elif id == "SS":
            # plt.subplot2grid((7, 1), (1, 0), rowspan=1)
            plt.subplot(612)
        elif id == "PE":
            # plt.subplot2grid((7, 1), (2, 0), rowspan=1)
            plt.subplot(613)
        elif id == "RO":
            # plt.subplot2grid((7, 1), (3, 0), rowspan=1)
            plt.subplot(614)
        elif id == "EPG":
            # plt.subplot2grid((7, 1), (4, 0), rowspan=3)
            plt.subplot(313)
    num_echo = abs(start_echo - end_echo) + 1
    if spoiler_portion != 0:
        a, b, c = arbitarySSFP_Spoiler(
            start_echo, end_echo, ascend, balance, spoiler_portion=spoiler_portion)
    else:
        a, b, c = arbitarySSFP(start_echo, end_echo, ascend, balance)
    print("a:{} b:{} c:{}".format(a, b, c))
    fig = plt.figure(figsize=(10, 10), dpi=300)
    subplot_id("RO")
    plt.axhline(y=0, color='k', linestyle='--')

    def plot_block(t, duration, amplitude, c='b', alpha=0.5):
        block_x = [t, t, t+duration, t+duration]
        block_y = [0, 0+amplitude, 0+amplitude, 0]
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
            subplot_id("EPG")
            plt.axvline(x=echo_t_, color='darkgreen', linestyle='--')
            plt.scatter(echo_t_, 0, c='k', marker='o')
            subplot_id("RO")
            plt.axvline(x=echo_t_, color='darkgreen', linestyle='--')
    else:
        for idx, b_ in enumerate(b):
            if idx % 2 == 0:  # RO
                subplot_id("EPG")
                plt.axvline(x=t+1, color='darkgreen', linestyle='--')
                plt.scatter(t+1, 0, c='k', marker='o')
                subplot_id("RO")
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
    t_list = np.array(t_list)
    t_list = np.concatenate(([-1], t_list, [t_list[-1]+1]))

    subplot_id("EPG")
    plt.axhline(y=0, color='k', linestyle='--')
    if type(b) == int:
        phase_evolution = np.concatenate(
            ([0], np.cumsum(np.concatenate(([a], [b], [c])))))
    else:
        phase_evolution = np.concatenate(
            ([0], np.cumsum(np.concatenate(([a], b, [c])))))
    phase_evolution = np.concatenate(
        ([phase_evolution[0]], phase_evolution, [phase_evolution[-1]]))

    if balance == True:
        plt.plot(t_list, phase_evolution, 'k')
    else:
        for idx in np.linspace(start_echo, end_echo, num_echo, endpoint=True):
            plt.plot(t_list, phase_evolution+idx*phase_evolution[-1], 'k')

    subplot_id("RF")
    rf0_t = np.linspace(-2, 0, 100)
    rf1_t = np.linspace(t_list[-1]-1, t_list[-1]+1, 100)
    sinc = np.sinc((rf0_t+1)*2)
    plt.plot(rf0_t, sinc, 'k')
    plt.plot(rf1_t, sinc, 'k')
    plt.ylim(-1.1, 1.1)
    plt.axhline(y=0, color='k', linestyle='--')
    plt.axvline(x=-1, color='k', linestyle=':')
    plt.axvline(x=t_list[-1], color='k', linestyle=':')
    plt.xlim(-2.1, t_list[-1]+1.1)
    plt.text(-3.5, 0, "RF", fontsize=20, verticalalignment='bottom',
             horizontalalignment='left')
    plt.axis('off')

    subplot_id("SS")
    t_SS = np.array([-2, -2, 0, 0, 1, 1])
    g_SS = 3*np.array([0, 1, 1, -1, -1, 0])
    plt.plot(t_SS, g_SS, 'k')
    plt.plot(-t_SS[::-1]+t_list[-2], g_SS[::-1], 'k')
    plt.axhline(y=0, color='k', linestyle='--')
    plt.axvline(x=-1, color='k', linestyle=':')
    plt.axvline(x=t_list[-1], color='k', linestyle=':')
    plt.xlim(-2.1, t_list[-1]+1.1)
    plt.ylim(-5, 5)
    plt.text(-3.5, 0, "Gss", fontsize=20, verticalalignment='bottom',
             horizontalalignment='left')
    plt.axis('off')

    subplot_id("PE")
    t_PE_0 = np.array([0, 0, 1, 1])
    t_PE_1 = np.array([t_list[-3], t_list[-3], t_list[-2], t_list[-2]])
    y = np.array([0, 1, 1, 0])
    for g in np.linspace(-3, 3, 7, endpoint=True):
        plt.plot(t_PE_0, g*y, 'k')
        plt.plot(t_PE_1, g*y, 'k')

    plt.axhline(y=0, color='k', linestyle='--')
    plt.axvline(x=-1, color='k', linestyle=':')
    plt.axvline(x=t_list[-1], color='k', linestyle=':')
    plt.xlim(-2.1, t_list[-1]+1.1)
    plt.ylim(-5, 5)
    plt.text(-3.5, 0, "Gpe", fontsize=20, verticalalignment='bottom',
             horizontalalignment='left')
    plt.axis('off')

    subplot_id("RO")
    plt.axvline(x=-1, color='k', linestyle=':')
    plt.axvline(x=t_list[-1], color='k', linestyle=':')
    plt.xlim(-2.1, t_list[-1]+1.1)
    plt.text(-3.5, 0, "Gro", fontsize=20, verticalalignment='bottom',
             horizontalalignment='left')
    plt.axis('off')

    subplot_id("EPG")
    plt.axvline(x=-1, color='k', linestyle=':')
    plt.axvline(x=t_list[-1], color='k', linestyle=':')
    plt.xlim(-2.1, t_list[-1]+1.1)
    plt.text(-3.5, 0, "EPG", fontsize=20, verticalalignment='bottom',
             horizontalalignment='left')
    plt.axis('off')

    for idx in np.linspace(start_echo, end_echo, num_echo, endpoint=True):
        plt.text(-1, idx*phase_evolution[-1],
                 r"$F(k_{%d})$" % (int(idx)), verticalalignment='bottom', horizontalalignment='left')
        plt.scatter(-1, idx*phase_evolution[-1], c='k', marker='x')
        if balance == True:
            plt.text(t_list[-2], idx*phase_evolution[-1], r"$F(k_{%d})$" % (
                int(idx+1)), verticalalignment='bottom', horizontalalignment='left')
        else:
            plt.text(t_list[-2], (idx+1)*phase_evolution[-1], r"$F(k_{%d})$" % (
                int(idx+1)), verticalalignment='bottom', horizontalalignment='left')
        plt.scatter(t_list[-1], (idx+1)*phase_evolution[-1], c='k', marker='x')

    plt.subplots_adjust(hspace=0)
    # plt.show()


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

    EPG_plot(0, 0, balance=True)
    plt.savefig("figs/EPG_plot_balance.png")
    EPG_plot(0, -1)
    plt.savefig("figs/EPG_plot_0n1.png")
    EPG_plot(0, +1)
    plt.savefig("figs/EPG_plot_0p1.png")
    EPG_plot(1, 4, spoiler_portion=1.3)
    plt.savefig("figs/EPG_plot_p1p4_spoil.png")
    EPG_plot(+1, -2, spoiler_portion=1.5)
    plt.savefig("figs/EPG_plot_p1n2_spoil.png")
    EPG_plot(-2, +1, spoiler_portion=1.5)
    plt.savefig("figs/EPG_plot_n2p1_spoil.png")
    EPG_plot(+2, -2, spoiler_portion=1.5)
    plt.savefig("figs/EPG_plot_p2n2_spoil.png")
    EPG_plot(-2, +2, spoiler_portion=1.5)
    plt.savefig("figs/EPG_plot_n2p2_spoil.png")
    EPG_plot(0, -1, spoiler_portion=1.5)
    plt.savefig("figs/EPG_plot_0n1_spoil.png")
    EPG_plot(+1, 0, spoiler_portion=1.5)
    plt.savefig("figs/EPG_plot_p1_0_spoil.png")
