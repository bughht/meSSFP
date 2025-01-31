import numpy as np
import pypulseq as pp
from algo_arbitarySSFP import arbitarySSFP

class ME_SSFP:
    def __init__(self,
                 FA = 35,
                 TR = 10e-3,
                 num_RO = 120,
                 num_PE = 120,
                 fov_RO = 200e-3,
                 fov_PE = 200e-3,
                 slice_thickness = 8e-3,
                 dwell = 1e-05,
                 phase_cycle=np.pi,
                 rf_duration=1e-3,
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
        if system is None:
            self.system = pp.Opts(max_grad=40,grad_unit='mT/m',max_slew=150,slew_unit='T/m/s', rf_ringdown_time=10e-6,rf_dead_time=400e-6,adc_dead_time=70e-6,grad_raster_time=10e-6)
        else:
            self.system = system
        self.prepare_sequence()
        
    def prepare_sequence(self):
        gx_single = pp.make_trapezoid(channel='x', flat_area=self.num_RO / self.fov_RO, flat_time=self.dwell*self.num_RO, system=self.system)
        self.ramp_area = (gx_single.area-gx_single.flat_area)/2
        self.half_grad_area = gx_single.flat_area/2

        self.rf_phase = 0
        self.rf_duration=0.8e-3
        self.rf, self.gz, self.gzr = pp.make_sinc_pulse(
        flip_angle=self.FA * np.pi / 180, duration=self.rf_duration,
        slice_thickness=self.slice_thickness, apodization=0.5, time_bw_product=4,
        system=self.system, use="excitation", return_gz=True)
        self.rf.delay = self.gz.rise_time
        self.gz.delay = 0

        self.PE = np.arange(-self.num_PE// 2, self.num_PE// 2, 1) / self.fov_PE

    def make_sequence(self, start_echo=0, end_echo=0, ascend=None, balance=False):
        seq = pp.Sequence(self.system)
        a,b,c = arbitarySSFP(start_echo, end_echo, ascend, balance)
        print("a:{} b:{} c:{}".format(a,b,c))
        num_echo = abs(start_echo - end_echo) + 1

        gx_pre = pp.make_trapezoid(channel='x', area=-self.ramp_area+self.half_grad_area*a, system=self.system) 
        gx_rep = pp.make_trapezoid(channel='x', area=-self.ramp_area+self.half_grad_area*c, system=self.system)
        gx_ro = pp.make_trapezoid(channel='x', flat_area=self.half_grad_area*b, flat_time=self.dwell*self.num_RO*num_echo, system=self.system)
        adc = pp.make_adc(num_samples=self.num_RO*num_echo, duration=self.dwell*self.num_RO*num_echo, delay = gx_ro.rise_time, system=self.system) 

        gpe_max = pp.make_trapezoid(channel='y', area=np.abs(self.PE).max(), system=self.system)
        min_pre_duration = max(pp.calc_duration(gpe_max), pp.calc_duration(gx_pre))
        min_rep_duration = max(pp.calc_duration(gpe_max), pp.calc_duration(gx_rep))

        min_TR = min_pre_duration+min_rep_duration+pp.calc_duration(gx_ro)+pp.calc_duration(self.gz)
        assert min_TR<self.TR, "TR {} is too short, minimum TR is {}".format(self.TR, min_TR)
        print("min_TR:{}".format(min_TR))
        delay_time = (self.TR-min_TR)
        for pe_idx, pe_area in enumerate(self.PE):
        # for pe_idx, pe_area in enumerate(self.PE[:5]):
            self.rf.phase_offset = pe_idx*self.phase_cycle
            adc.phase_offset = pe_idx*self.phase_cycle
            gpe_pre = pp.make_trapezoid(channel='y', area=pe_area, duration=min_pre_duration, system=self.system)
            gpe_rep = pp.make_trapezoid(channel='y', area=-pe_area, duration=min_rep_duration, system=self.system)

            seq.add_block(self.rf, self.gz)
            seq.add_block(*pp.align(right=gx_pre, left=[gpe_pre, self.gzr]))
            seq.add_block(gx_ro, adc)
            seq.add_block(*pp.align(left=[gx_rep, pp.make_delay(delay_time+min_rep_duration)], right=[gpe_rep, self.gzr]))

        return seq


if __name__ == "__main__":
    import matplotlib.pyplot as plt
    # System Parameter for uMR890
    sys = pp.Opts(max_grad=40,grad_unit='mT/m',max_slew=150,slew_unit='T/m/s', rf_ringdown_time=10e-6,rf_dead_time=400e-6,adc_dead_time=70e-6,grad_raster_time=10e-6)
    me_ssfp = ME_SSFP(TR=8e-3, dwell=1e-5, rf_duration=3e-3,num_PE=120, num_RO=120, system=sys)
    seq_p1n2 = me_ssfp.make_sequence(+1, -2)
    seq_p1n2.write('seq/seq_p1n2.seq')
    seq_0n3 = me_ssfp.make_sequence(+0, -3)
    seq_0n3.write('seq/seq_0n3.seq')
    seq_0n1 = me_ssfp.make_sequence(+0, -1)
    seq_0n1.write('seq/seq_0n1.seq')
    seq_bssfp = me_ssfp.make_sequence(0, 0, None, balance=True)
    seq_bssfp.write('seq/seq_bssfp.seq')


