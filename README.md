# Pulse sequence diagram for arbitrary multi-echo steady-state free precession (me-SSFP)

## Theory

The extended phase graph (EPG) decompose the magnetization into a series of fourier coefficients in the transverse plane ($F_n$) and longitudinal axis ($Z_n$).

$$F(k_n)= \frac{1}{2\pi} \int_{-\pi}^{\pi} M_{xy}(\theta) e^{-jn\theta} d\theta, \quad n \in \mathbb{Z}$$

$$Z(k_n) = \frac{1}{2\pi} \int_{-\pi}^{\pi} M_z(\theta) e^{-jn\theta} d\theta, \quad n \in \mathbb{N}$$

$$k_n=n\phi_{\text{inc}} = n\gamma\int_0^{t_{\text{inc}}}G_\text{RO}(\tau)d\tau = n\gamma G_\text{RO}t_\text{inc}$$

The RF pulse induced rotation of the magnetization could be regarded as independent rotation of each isochromat. The rotation of the $n$-th isochromat is given by

$$\begin{bmatrix}
F^+(k_n) \\
F^+(k_{-n})\\
Z^+(k_n) \\
\end{bmatrix} = \mathbf{R}(\theta,\phi)\begin{bmatrix}
F^-(k_n) \\
F^-(k_{-n})\\
Z^-(k_n) \\
\end{bmatrix}$$

where the rotation matrix $\mathbf{R}(\theta,\phi)$ is given by

$$\mathbf{R}(\theta,\phi) = \begin{bmatrix} \cos^2 \frac{\alpha}{2} & e^{2i\phi} \sin^2 \frac{\alpha}{2} & -ie^{i\phi} \sin \alpha \\
e^{-2i\phi} \sin^2 \frac{\alpha}{2} & \cos^2 \frac{\alpha}{2} & ie^{-i\phi} \sin \alpha \\
 -\frac{i}{2} e^{-i\phi} \sin \alpha & \frac{i}{2} e^{i\phi} \sin \alpha & \cos \alpha
\end{bmatrix}$$

The evolution of states between the RF pulses is given by

$$\begin{aligned}
F_{n+1}^- &= E_2 F_n^+\\
Z_n^- &= E_1 Z_n^+,\quad n\ne 0\\
Z_0^- &= E_1 Z_n^+ + M_0(1-E_1)\\
\end{aligned}$$


The analytic solution for the $n$-th coefficient of the transverse magnetization after the RF pulse $F^+$ is given by \cite{leupold2017steady}

$$F^+(k_n) = \frac{M_0(1-E_1)}{(A-BE_2^2)\sqrt{1-a^2}}\left[\left(\frac{\sqrt{1-a^2}-1}{a}\right)^{|n|} - E_2\left(\frac{\sqrt{1-a^2}-1}{a}\right)^{|n+1|}\right]$$

$$\begin{aligned}
A &= 1 - E_1\cos(\alpha) \\
B &= E_1\sin(\alpha) \\
a &= \frac{E_2(B-A)}{A-BE_2^2} \\
\end{aligned}$$

and under the assumption of lorentz distribution of the off-resonance within the voxel for describing the $T_2'$, the echo signal $S_n$ to be measured is given by

$$S_n(\text{TE}_n) = F_n^+ \underbrace{e^{-\text{TE}_n/T_2}}_{T_2\text{ relaxation}} \underbrace{e^{-\left|\text{TE}_n+n\text{TR}\right|/T_2'}}_{T_2'\text{ relaxation}}\underbrace{e^{j\omega_0(\text{TE}_n+n\text{TR})}}_{\text{off-resonance phase}}$$

where the $T_2$ and $T_2'$ relaxation terms are multiplied to the transverse magnetization after the RF pulse $F^+$, and the off-resonance phase term corresponds to the phase shift of the $n$-th echo due to the B0 field inhomogeneity.

## Algorithm