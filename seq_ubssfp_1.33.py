import numpy as np
import MRzeroCore as mr0
import pypulseq as pp
import matplotlib.pyplot as plt

# @title Define SSFP in PyPulseq
# %% S2. DEFINE the sequence

FAex = 35  # @param {type: "slider", min: 1, max: 180}
P_alpha_half = False  # @param {type: "boolean"}
TR_ms = 0  # @param {type: "slider", min: 0.0, max: 20, step:0.1}
TR = TR_ms*1e-3
PEtype = 'linear'  # @param ['centric', 'linear']
PE_flag = True  # @param {type: "boolean"}
TI = 0  # @param {type: "slider", min: 0, max: 5, step:0.1}

# choose the scanner limits
system = pp.Opts(max_grad=40, grad_unit='mT/m', max_slew=150, slew_unit='T/m/s',
                 rf_ringdown_time=20e-6, rf_dead_time=100e-6, adc_dead_time=20e-6, grad_raster_time=10e-6)
# Nread = 120
# Nphase= 120
Nread = 240
Nphase = 240

seq = pp.Sequence(system)

# Define FOV and resolution
fov = 200e-3
slice_thickness = 8e-3

# rf1 = pp.make_block_pulse(flip_angle=90 * np.pi / 180, duration=1e-3, system=system)

fastest_grad = pp.make_extended_trapezoid_area(
    area=(Nphase)/fov, channel='y', grad_end=0.0, grad_start=0.0, system=system)
# this is a first speedup test, in shoudl run with area=(Nphase/2)/fov, but only area=(Nphase)/fov worked
min_gr_dur = fastest_grad[0].shape_dur

dwell = 1e-05

ub_factor = 4/3
# Define other gradients and ADC events
gx = pp.make_trapezoid(channel='x', flat_area=Nread / fov,
                       flat_time=dwell*Nread, system=system)
adc = pp.make_adc(num_samples=Nread, duration=dwell*Nread,
                  phase_offset=0 * np.pi/180, delay=gx.rise_time, system=system)
gx_pre = pp.make_trapezoid(
    channel='x', area=-gx.area / 2, duration=min_gr_dur, system=system)
gp = pp.make_trapezoid(channel='y', area=1, duration=min_gr_dur, system=system)

gx.flat_time *= ub_factor
adc.num_samples *= ub_factor

rf_phase = 0

# Define rf events
rf_IR = pp.make_block_pulse(
    flip_angle=180 * np.pi / 180, phase_offset=90 * np.pi / 180, duration=0.5e-3, system=system)
gz_spoil = pp.make_trapezoid(
    channel='z', area=64, duration=1e-3, system=system)

rfdur = 0.8e-3
rf1, gz1, gzr1 = pp.make_sinc_pulse(
    flip_angle=FAex * np.pi / 180, duration=rfdur,
    slice_thickness=slice_thickness, apodization=0.5, time_bw_product=4,
    system=system, return_gz=True)

rf0, gz0, gzr0 = pp.make_sinc_pulse(
    flip_angle=FAex/2 * np.pi / 180, duration=rfdur,
    slice_thickness=slice_thickness, apodization=0.5, time_bw_product=4,
    system=system, return_gz=True)

# ======
# CONSTRUCT SEQUENCE
# ======
# linear reordering
phenc = np.arange(-Nphase // 2, Nphase // 2, 1) / fov
permvec = np.arange(0, Nphase, 1)
# centric reordering
if PEtype == 'centric':
    permvec = sorted(np.arange(len(phenc)),
                     key=lambda x: abs(len(phenc) // 2 - x))
# random reordering
# perm =np.arange(0, Nphase, 1);  permvec = np.random.permutation(perm)

phenc_centr = phenc[permvec] * PE_flag

ktraj = np.array([])
if TI > 0:
    seq.add_block(rf_IR)
    seq.add_block(gz_spoil)
    seq.add_block(pp.make_delay(TI))

seq.add_block(pp.make_delay(0.0015-(rfdur/2+rf1.delay)))

minTR = pp.calc_duration(gz1) + pp.calc_duration(gx_pre, gp, gzr1) + \
    pp.calc_duration(gx)+pp.calc_duration(gp, gx_pre, gzr1)
minTR2 = minTR/2
TRd = round(max(0, (TR/2-minTR2))/10e-5)*10e-5  # round to raster time
TR = 2*(minTR2 + TRd)
if TRd == 0:
    print('rep. time set to minTR [ms]', TR*1000)
else:
    print(' TR [ms]', TR*1000)

if P_alpha_half:
    seq.add_block(rf0, gz0)
    seq.add_block(gzr0)
    # last timing step is to add TR/2 between alpha half and first rf pulse
    # from pulse top to pulse top we have already played out one full gz0 and 2*gzr0, thus we substract these from TR
    seq.add_block(pp.make_delay(minTR2+TRd-pp.calc_duration(gz0)-2 *
                  pp.calc_duration(gzr0)))  # for balancing Gz is played out twice!
    seq.add_block(gzr0)  # balance Gz!
for ii in range(0, Nphase):  # e.g. -64:63

    rf_phase = divmod(rf_phase + 180, 360.0)[1]
    # set current rf phase, 180° alternating phase cycling
    rf1.phase_offset = rf_phase / 180 * np.pi
    adc.phase_offset = rf_phase / 180 * np.pi  # follow with ADC

    ktraj = np.append(ktraj, phenc_centr[ii])
    seq.add_block(rf1, gz1)
    gp = pp.make_trapezoid(
        channel='y', area=phenc_centr[ii], duration=min_gr_dur, system=system)
    seq.add_block(pp.make_delay(TRd))

    seq.add_block(gx_pre, gp, gzr1)
    seq.add_block(adc, gx)
    gp = pp.make_trapezoid(
        channel='y', area=-phenc_centr[ii], duration=min_gr_dur, system=system)
    # seq.add_block(gx_pre, gp,gzr1)  #  balance Gz!
    seq.add_block(*pp.align(right=[gx_pre, gp, gzr1]))
    seq.add_block(pp.make_delay(TRd))
    # full pulse            delay of rf2 -ringdown rf1  + TR_delay + RO/2
# %% S3. CHECK, PLOT and WRITE the sequence  as .seq
# Check whether the timing of the sequence is correct
ok, error_report = seq.check_timing()
if ok:
    print('Timing check passed successfully')
else:
    print('Timing check failed. Error listing follows:')
    [print(e) for e in error_report]

# PLOT sequence
# sp_adc, t_adc = mr0.util.pulseq_plot(seq, clear=False, figid=(11,12))

# Prepare the sequence output for the scanner
seq.set_definition('FOV', [fov, fov, slice_thickness])
seq.write('seq/ubSSFP_1.33.seq')


# seq.plot(time_range=[0, 0.1])
# plt.show()
