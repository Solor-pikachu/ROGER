from sampling import *
from sampling import _ifft,_fft
from mrfft import *
from torch_grappa import GRAPPA_calibrate_weights_2d_torch,GRAPPA_interpolate_imageSpace_2d_torch
import torch

import numpy as np
from functools import partial

from guided_diffusion.script_util import create_model


import argparse
parser = argparse.ArgumentParser(description='')
parser.add_argument('--input',  type=str)
parser.add_argument('--output', type=str)
parser.add_argument('--chk',    type=str, default='384x384_ema_0.9999_200000.pt')

parser.add_argument('--MB', type=int)
parser.add_argument('--R', type=int)

parser.add_argument('--LFE_device', type=str,  default='cpu')
parser.add_argument('--calib_pd',   type=int,  default=30)
parser.add_argument('--block_size', type=list, default=[4,4])
parser.add_argument('--regularization_factor', type=float, default=0.01)

parser.add_argument('--DDPM_device', type=str,  default='cuda:0')
parser.add_argument('--lfe_pd', type=int,  default=8)
parser.add_argument('--scale', type=float, default=0.3)
parser.add_argument('--dc_iters',  type=int,   default=4)
parser.add_argument('--step_size', type=float, default=2.)
parser.add_argument('--T',         type=int,   default=1000)
args = parser.parse_args()

##############        Load Model         ##############
model = create_model(
    image_size=256,
    num_channels=128,
    num_res_blocks=2,
    channel_mult="",
    learn_sigma=True,
    class_cond=False,
    use_checkpoint=False,
    attention_resolutions="16,8",
    num_heads=4,
    num_head_channels=-1,
    num_heads_upsample=-1,
    use_scale_shift_norm=True,
    dropout=0,
    resblock_updown=False,
    use_fp16=False,
    use_new_attention_order=False,
)
model.eval()
print('Load Model State:', model.load_state_dict(torch.load(args.chk, map_location='cpu')))
betas = np.linspace(0.0001, 0.02, 1000, dtype=np.float64)

##############     Load SMS data      ##############
data = np.load(args.input,allow_pickle=True)
readout_data        = data['readout_data']
readout_calibration = data['readout_calibration']
readout_csm         = data['readout_csm']
shifts              = data['shifts']
nx,ny               = readout_data.shape[0],readout_data.shape[1]

############## LFE: update A and mask ##############
device = torch.device(args.LFE_device)
calib_pd             = 30
calib                = readout_calibration[nx//2-calib_pd:nx//2+calib_pd,ny//2-calib_pd:ny//2+calib_pd]
calib_torch          = torch.from_numpy(calib.astype(np.complex64)).to(device)
readout_data_torch   = torch.from_numpy(readout_data.astype(np.complex64)).to(device)

grappa_weights_torch = GRAPPA_calibrate_weights_2d_torch(calib_torch, 
                                                         (args.MB, args.R), 
                                                         device, 
                                                         args.block_size, 
                                                         args.regularization_factor)

kspace_recon_kykxc, image_coilcombined_sos, unmixing_map_coilWise = GRAPPA_interpolate_imageSpace_2d_torch(
    readout_data_torch, 
    (args.MB, args.R), 
    args.block_size, 
    grappa_weights_torch, 
    device)

##############     DIffusion model     ##############
device = torch.device(args.DDPM_device)
lfe_pd = args.lfe_pd
mask = np.where(np.abs(readout_data)!=0,1,0)[...,0]
mask[nx//2-lfe_pd//2:nx//2+lfe_pd//2,ny//2-lfe_pd//2:ny//2+lfe_pd//2] = 1

torch_mask_real = torch.from_numpy(mask[None][None].astype(np.complex64)).to(device)
und_ksp = kspace_recon_kykxc.to(device).permute(2,0,1)[None] * torch_mask_real
coilsen = torch.from_numpy(readout_csm.transpose(2,0,1)[None].astype(np.complex64)).to(device)
zero_filled = torch.sum((_ifft(und_ksp) * torch.conj(coilsen)),dim=1)
zero_filled_Real = zero_filled / zero_filled.abs().max()

grad_params = {'measurement': zero_filled_Real*args.scale,   'mask': torch_mask_real,  'coilsen': coilsen, 'shifts': shifts}
AHA_Real    = partial(cond_func, **grad_params)

model = model.to(device)
betas = torch.from_numpy(betas).float().to(device)

with torch.no_grad():
    x = torch.randn([args.MB, 2 , nx//args.MB, ny]).to(device) # B, C, H, W -> MB, 2, 384, 384
    x = ddnm_diffusion(x, model, betas, T=args.T, sigma_y=0.0, step_size=args.step_size, arg_iters=args.dc_iters, cond_func=AHA_Real)

images = float2cplx(inverse_data_transform(x).cpu().permute(0,2,3,1))
np.savez(args.output,recon=images.astype(np.complex64))

