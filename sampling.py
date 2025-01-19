import torch
import numpy as np
from tqdm import tqdm

import torch.fft as torch_fft
def _ifft(x):
    x = torch_fft.ifftshift(x, dim=(-2, -1))
    x = torch_fft.ifft2(x, dim=(-2, -1), norm='ortho')
    x = torch_fft.fftshift(x, dim=(-2, -1))
    return x

# Centered, orthogonal fft in torch >= 1.7
def _fft(x):
    x = torch_fft.fftshift(x, dim=(-2, -1))
    x = torch_fft.fft2(x, dim=(-2, -1), norm='ortho')
    x = torch_fft.ifftshift(x, dim=(-2, -1))
    return x


def update_pbar_desc(pbar, metrics, labels):
    pbar_string = ''
    for metric, label in zip(metrics, labels):
        pbar_string += f'{label}: {metric:.7f}; '
    pbar.set_description(pbar_string)


def ddnm_diffusion(xt, model, b, T, sigma_y, step_size, arg_iters,  cond_func=None):
    x = xt
    skip = 1000 / T
    n = xt.size(0)
    losses = []

    times = get_schedule_jump(T, 1, 1)
    time_pairs = list(zip(times[:-1], times[1:]))        

    pbar = tqdm(time_pairs)
    pbar_labels = ['loss', 'mean', 'min', 'max']

    k_init = 0
    b_init = 0
    
    # Reverse diffusion + Nila-DC
    for i, j in pbar:
        i, j = i*skip, j*skip
        if j<0: j=-1 

        t       = (torch.ones(n) * i).to(x.device)
        next_t  = (torch.ones(n) * j).to(x.device)
        at      = compute_alpha(b, t.long())
        at_next = compute_alpha(b, next_t.long())
        sigma_t = (1 - at_next).sqrt()[0, 0, 0, 0]
        a       = at_next.sqrt()[0, 0, 0, 0]
        
        et = model(xt, t)[:, :2]

        xt = (1/at.sqrt()) * (xt - et * (1 - at).sqrt()) # Eq.6
        
        for _ in range(arg_iters): # Fig.2 (a) (for best DC)
            meas_grad = cond_func(xt) 

            if sigma_t / a <  sigma_y: # Eq.10 (lambda function)
                if k_init == 0 and b_init==0:
                    k_init = 0.2 / (-1 * i)
                    b_init = -999 * k_init
                factor = k_init * (999 - i) + b_init
            else:
                factor = 1
                
            xt = xt - factor * meas_grad * step_size
        xt_1 = at_next.sqrt() * xt + torch.randn_like(xt) * sigma_t # Eq.11

        metrics = [(meas_grad).norm(), (xt).abs().mean(), (xt).abs().min(), (xt).abs().max()]
        update_pbar_desc(pbar, metrics, pbar_labels)
        xt = xt_1
    return xt


def float2cplx(float_in):
    return np.array(float_in[...,0]+1.0j*float_in[...,1], dtype='complex64')

def cplx2float(cplx_in):
    return np.array(np.stack((cplx_in.real, cplx_in.imag), axis=-1), dtype='float32')


import torch.fft as torch_fft
def _ifft(x):
    x = torch_fft.ifftshift(x, dim=(-2, -1))
    x = torch_fft.ifft2(x, dim=(-2, -1), norm='ortho')
    x = torch_fft.fftshift(x, dim=(-2, -1))
    return x

# Centered, orthogonal fft in torch >= 1.7
def _fft(x):
    x = torch_fft.fftshift(x, dim=(-2, -1))
    x = torch_fft.fft2(x, dim=(-2, -1), norm='ortho')
    x = torch_fft.ifftshift(x, dim=(-2, -1))
    return x

def compute_alpha(beta, t):
    beta = torch.cat([torch.zeros(1).to(beta.device), beta], dim=0)
    a = (1 - beta).cumprod(dim=0).index_select(0, t + 1).view(-1, 1, 1, 1)
    return a


# form RePaint
def get_schedule_jump(T_sampling, travel_length, travel_repeat):

    jumps = {}
    for j in range(0, T_sampling - travel_length, travel_length):
        jumps[j] = travel_repeat - 1

    t = T_sampling
    ts = []

    while t >= 1:
        t = t-1
        ts.append(t)

        if jumps.get(t, 0) > 0:
            jumps[t] = jumps[t] - 1
            for _ in range(travel_length):
                t = t + 1
                ts.append(t)

    ts.append(-1)

    _check_times(ts, -1, T_sampling)

    return ts

def _check_times(times, t_0, T_sampling):
    # Check end
    assert times[0] > times[1], (times[0], times[1])

    # Check beginning
    assert times[-1] == -1, times[-1]

    # Steplength = 1
    for t_last, t_cur in zip(times[:-1], times[1:]):
        assert abs(t_last - t_cur) == 1, (t_last, t_cur)

    # Value range
    for t in times:
        assert t >= t_0, (t, t_0)
        assert t <= T_sampling, (t, T_sampling)


def inverse_data_transform(x):
    x = (x + 1.0) / 2.0
    return x

def data_transform(x):
    x = (2 * x) - 1.0
    return x

def cond_func(x, measurement, mask, coilsen, shifts=[-0.5,-0.25,0]):

    mb = len(shifts)
    x = inverse_data_transform(x)
    x = torch.view_as_complex(x.permute(0,2,3,1).contiguous())[:,None] # torch.Size([3, 1, 256, 256])
    nx, ny = x.shape[2:]

    x_readout_data = torch.zeros([1,1,nx*mb,ny],dtype=torch.complex64).to(x.device)

    for i,shift in enumerate(shifts):
        shift = int(shift * nx)
        x_readout_data[:,:,i*nx:(i+1)*nx] = torch.roll(x[i],-shift,-1)
    if len(shifts)%2 == 0:
        x_readout_data = torch.roll(x_readout_data,-(nx//2),2)

    k_x = _fft(x_readout_data * coilsen) #Expand coilsen
    x   = _ifft(k_x * mask)              #Under sampling
    x   = torch.sum(x * torch.conj(coilsen), axis=1) #Reduce coilsen
    grad_readout_data = x - measurement # || AHA(x) - y ||

    if len(shifts)%2 == 0:
        grad_readout_data = torch.roll(grad_readout_data,(nx//2),1)
    grad = torch.zeros([mb, nx, ny],dtype=torch.complex64).to(x.device)
    for i,shift in enumerate(shifts):
        shift = int(shift * nx)
        grad[i] = torch.roll(grad_readout_data[:,i*nx:(i+1)*nx],shift,-1)

    grad = torch.view_as_real(grad).permute(0,3,1,2)
    return grad