import numpy as np
import pypulseq as pp
from algo_arbitarySSFP import arbitarySSFP_Spoiler


class ME_SSFP_Spoiler:
    def __init__(self,
                 FA=35,
                 TR=10e-3,
                 num_RO=120,
                 num_PE=120,
                 fov_RO=200e-3,
                 fov_PE=200e-3,
                 slice_thickness=8e-3,
                 dwell=1e-05,
                 phase_cycle=np.pi,
                 rf_duration=1e-3,
                 slice_spoiler=False,
                 system=None,
                 ):
        self.FA = FA
        self.TR = TR
        self.num_RO = num_RO
        self.num_PE = num_PE
        self.fov_RO = fov_RO
        self.fov_PE = fov_PE
        self.slice_thickness = slice_thickness
        self.dwell = dwell
        self.phase_cycle = phase_cycle
        self.rf_duration = rf_duration
        self.slice_spoiler = slice_spoiler
        if system is None:
            self.system = pp.Opts(max_grad=40, grad_unit='mT/m', max_slew=150, slew_unit='T/m/s',
                                  rf_ringdown_time=20e-6, rf_dead_time=100e-6, adc_dead_time=20e-6, grad_raster_time=10e-6)
        else:
            self.system = system
        self.prepare_sequence()

    def prepare_sequence(self):
        gx_single = pp.make_trapezoid(channel='x', flat_area=self.num_RO /
                                      self.fov_RO, flat_time=self.dwell*self.num_RO, system=self.system)
        self.ramp_area = (gx_single.area-gx_single.flat_area)/2
        self.half_grad_area = gx_single.flat_area/2

        self.rf_phase = 0
        self.rf_duration = 0.8e-3
        self.rf, self.gz, self.gzr = pp.make_sinc_pulse(
            flip_angle=self.FA * np.pi / 180, duration=self.rf_duration,
            slice_thickness=self.slice_thickness, apodization=0.5, time_bw_product=4,
            system=self.system, return_gz=True)

        self.PE = np.arange(-self.num_PE // 2,
                            self.num_PE // 2, 1) / self.fov_PE

    def make_sequence(self, start_echo=0, end_echo=0, ascend=None, balance=False, spoiler_portion=0.0):
        seq = pp.Sequence(self.system)
        a, b, c = arbitarySSFP_Spoiler(
            start_echo, end_echo, ascend, balance, spoiler_portion=spoiler_portion)
        print("a:{} b:{} c:{}".format(a, b, c))
        num_echo = abs(start_echo - end_echo) + 1

        gx_pre = pp.make_trapezoid(
            channel='x', area=-self.ramp_area+self.half_grad_area*a, system=self.system)
        gx_rep = pp.make_trapezoid(
            channel='x', area=-self.ramp_area+self.half_grad_area*c, system=self.system)

        print(gx_pre.area, gx_rep.area, self.ramp_area)
        gx_ro = pp.make_trapezoid(channel='x', flat_area=self.half_grad_area*2,
                                  flat_time=self.dwell*self.num_RO, system=self.system)
        adc = pp.make_adc(num_samples=self.num_RO*num_echo, duration=self.dwell *
                          self.num_RO, delay=gx_ro.rise_time, system=self.system)

        gx_spoil = pp.make_trapezoid(
            channel='x', area=2*self.half_grad_area*spoiler_portion, system=self.system)

        if gx_spoil.flat_time == 0:

            gx_spoil_amplitude = (gx_spoil.area-0.5*gx_ro.amplitude*(gx_spoil.rise_time+gx_spoil.fall_time))/(
                0.5*(gx_spoil.rise_time+gx_spoil.fall_time)+gx_spoil.flat_time)
            gx_ro_left = pp.make_extended_trapezoid(channel='x', times=[0, gx_ro.rise_time, gx_ro.rise_time+gx_ro.flat_time, gx_ro.rise_time+gx_ro.flat_time+gx_spoil.rise_time], amplitudes=[
                                                    0, gx_ro.amplitude, gx_ro.amplitude, gx_spoil.amplitude-gx_ro.amplitude], system=self.system)
            gx_ro_mid = pp.make_extended_trapezoid(channel='x', times=[0, gx_spoil.fall_time, gx_spoil.fall_time+gx_ro.flat_time, gx_spoil.fall_time+gx_ro.flat_time+gx_spoil.rise_time], amplitudes=[
                                                   gx_spoil.amplitude-gx_ro.amplitude, gx_ro.amplitude, gx_ro.amplitude, gx_spoil.amplitude-gx_ro.amplitude], system=self.system)
            gx_ro_right = pp.make_extended_trapezoid(channel='x', times=[0, gx_spoil.fall_time, gx_spoil.fall_time+gx_ro.flat_time, gx_spoil.fall_time+gx_ro.flat_time+gx_ro.fall_time], amplitudes=[
                                                     gx_spoil.amplitude-gx_ro.amplitude, gx_ro.amplitude, gx_ro.amplitude, 0], system=self.system)
        else:
            gx_spoil_amplitude = (gx_spoil.area-0.5*gx_ro.amplitude*(gx_spoil.rise_time+gx_spoil.fall_time))/(
                0.5*(gx_spoil.rise_time+gx_spoil.fall_time)+gx_spoil.flat_time)
            # print("ro_amplitude", gx_ro.amplitude, "spoil_amplitude", gx_spoil_amplitude, "ro_area", gx_ro.flat_area, "spoil area", gx_spoil.area, gx_spoil_amplitude *
            #       gx_spoil.flat_time+0.5*(gx_ro.amplitude+gx_spoil_amplitude)*(gx_spoil.rise_time+gx_spoil.fall_time))
            gx_ro_left = pp.make_extended_trapezoid(channel='x', times=[0, gx_ro.rise_time, gx_ro.rise_time+gx_ro.flat_time, gx_ro.rise_time+gx_ro.flat_time+gx_spoil.rise_time, gx_ro.rise_time +
                                                    gx_ro.flat_time+gx_spoil.rise_time+gx_spoil.flat_time], amplitudes=[0, gx_ro.amplitude, gx_ro.amplitude, gx_spoil_amplitude, gx_spoil_amplitude], system=self.system)
            gx_ro_mid = pp.make_extended_trapezoid(channel='x', times=[0, gx_spoil.fall_time, gx_spoil.fall_time+gx_ro.flat_time, gx_spoil.fall_time+gx_ro.flat_time+gx_spoil.rise_time, gx_spoil.fall_time +
                                                   gx_ro.flat_time+gx_spoil.rise_time+gx_spoil.flat_time], amplitudes=[gx_spoil_amplitude, gx_ro.amplitude, gx_ro.amplitude, gx_spoil_amplitude, gx_spoil_amplitude], system=self.system)
            gx_ro_right = pp.make_extended_trapezoid(channel='x', times=[0, gx_spoil.fall_time, gx_spoil.fall_time+gx_ro.flat_time, gx_spoil.fall_time +
                                                     gx_ro.flat_time+gx_ro.fall_time], amplitudes=[gx_spoil_amplitude, gx_ro.amplitude, gx_ro.amplitude, 0], system=self.system)
        print("Delta TE: ", pp.calc_duration(gx_ro_mid))
        adc_left = pp.make_adc(num_samples=self.num_RO, duration=self.dwell *
                               self.num_RO, delay=gx_ro.rise_time, system=self.system)
        adc_mid = pp.make_adc(num_samples=self.num_RO, duration=self.dwell *
                              self.num_RO, delay=gx_spoil.fall_time, system=self.system)
        adc_right = pp.make_adc(num_samples=self.num_RO, duration=self.dwell *
                                self.num_RO, delay=gx_spoil.fall_time, system=self.system)

        gpe_max = pp.make_trapezoid(channel='y', area=np.abs(
            self.PE).max(), system=self.system)
        min_pre_duration = max(pp.calc_duration(
            gpe_max), pp.calc_duration(gx_pre))
        min_rep_duration = max(pp.calc_duration(
            gpe_max), pp.calc_duration(gx_rep))

        if num_echo == 1:
            min_TR = min_pre_duration+min_rep_duration + \
                pp.calc_duration(gx_ro)+pp.calc_duration(self.gz)
        else:
            min_TR = min_pre_duration+min_rep_duration+pp.calc_duration(gx_ro_left)+pp.calc_duration(
                gx_ro_mid)*(num_echo-2)+pp.calc_duration(gx_ro_right)+pp.calc_duration(self.gz)

        assert min_TR < self.TR, "TR {} is too short, minimum TR is {}".format(
            self.TR, min_TR)
        print("min_TR:{}".format(min_TR))
        delay_time = (self.TR-min_TR)
        for pe_idx, pe_area in enumerate(self.PE):
            # for pe_idx, pe_area in enumerate(self.PE[:5]):
            self.rf.phase_offset = pe_idx*self.phase_cycle
            adc.phase_offset = pe_idx*self.phase_cycle
            adc_left.phase_offset, adc_mid.phase_offset, adc_right.phase_offset = adc.phase_offset, adc.phase_offset, adc.phase_offset
            gpe_pre = pp.make_trapezoid(
                channel='y', area=pe_area, duration=min_pre_duration, system=self.system)
            gpe_rep = pp.make_trapezoid(
                channel='y', area=-pe_area, duration=min_rep_duration, system=self.system)

            seq.add_block(self.rf, self.gz)
            seq.add_block(*pp.align(right=gx_pre, left=[gpe_pre, self.gzr]))
            if len(b) == 1:
                seq.add_block(gx_ro, adc)
            else:
                for idx_echo in range(num_echo):
                    if idx_echo == 0:
                        seq.add_block(gx_ro_left, adc_left)
                    elif idx_echo == num_echo-1:
                        seq.add_block(gx_ro_right, adc_mid)
                    else:
                        seq.add_block(gx_ro_mid, adc_right)
            seq.add_block(
                *pp.align(left=[gx_rep, pp.make_delay(delay_time+min_rep_duration)], right=[gpe_rep, self.gzr]))

        return seq


if __name__ == "__main__":
    import matplotlib.pyplot as plt
    sys = pp.Opts(max_grad=60, grad_unit='mT/m', max_slew=150, slew_unit='T/m/s',
                  rf_ringdown_time=20e-6, rf_dead_time=100e-6, adc_dead_time=20e-6, grad_raster_time=10e-6)

    me_ssfp = ME_SSFP_Spoiler(FA=40, TR=20e-3, dwell=1e-5,
                              rf_duration=1e-3, num_PE=120, num_RO=120, system=sys, phase_cycle=np.pi)

    # seq_p1n2 = me_ssfp.make_sequence(+1, -2, spoiler_portion=1)
    # seq_p1n2.write('seq/seq_p1n2_spoiler.seq')
    # seq_0n1 = me_ssfp.make_sequence(0, -1, spoiler_portion=1.5)
    # seq_0n1.write('seq/seq_0n1_spoiler.seq')
    # seq_n10 = me_ssfp.make_sequence(-1, 0, spoiler_portion=1.5)
    # seq_n10.write('seq/seq_n10_spoiler.seq')
    seq_p2n3 = me_ssfp.make_sequence(+2, -3, spoiler_portion=3.5)
    seq_p2n3.write('seq/seq_p2n3_spoiler.seq')
    # seq_0n3 = me_ssfp.make_sequence(+0, -3)
    # seq_0n3.write('seq/seq_0n3.seq')
    # seq_bssfp = me_ssfp.make_sequence(0, 0, None, balance=True)
    # seq_bssfp.plot()
    # seq_bssfp.write('seq/seq_bssfp.seq')
