# ROGER
👏👏 [Robust Simultaneous Multislice MRI Reconstruction Using Deep Generative Priors](https://arxiv.org/abs/2407.21600)

## data and model weight are released at [Google Drive](https://drive.google.com/drive/folders/1dekG6Ya1crYhSpL3qJKEszfLDsB4_4z_?usp=sharing)

## Data preprocess
Before inference, the data should be saved like:
```
readout_data        = data['readout_data']
readout_calibration = data['readout_calibration']
readout_csm         = data['readout_csm']
shifts              = data['shifts']
```

## Inference
``` bash
python infer.py --input meas_MID00273_FID03217_TSE_SMS_334_SMS_data_slice0.npz --output recon_MB3R3.npz --MB 3 --R 3 --chk 384x384_ema_0.9999_200000.pt 
```

## Reconstruction
<table border="1" cellspacing="10" cellpadding="10">
  <tr>
    <th>Sampling setting</th>
    <th>Mask</th>
    <th>SMS Image</th>
    <th>Recon</th>
    <th>GT</th>
  </tr>
  <tr>
    <td>
      MB4R1
    </td>
    <td>
         <img src="misc/mask_MB4R1.png" class="giphy-embed" height="140" width="140" alt="SMS Image">
    </td>
    <td>
        <img src="misc/img_MB4R1.png" class="giphy-embed" height="140" width="140" alt="SMS Image">
    </td>
    <td>
        <img src="misc/fastMRI_MB4R1.gif" frameborder="0" class="giphy-embed" allowfullscreen height="140" width="140" alt="Recon Image">
    </td>

  </tr>
  <tr>
    <td>
      MB4R2
    </td>
    <td>
         <img src="misc/mask_MB4R2.png" class="giphy-embed" height="140" width="140" alt="SMS Image">
    </td>
    <td>
        <img src="misc/img_MB4R2.png" class="giphy-embed" height="140" width="140" alt="SMS Image">
    </td>
    <td>
        <img src="misc/fastMRI_MB4R2.gif" frameborder="0" class="giphy-embed" allowfullscreen height="140" width="140" alt="Recon Image">
    </td>
    <td>
        <img src="misc/gt.gif" frameborder="0" class="giphy-embed" allowfullscreen height="140" width="140" alt="GT">
    </td>
  </tr>
  <tr>
    <td>
      MB4R3
    </td>
    <td>
         <img src="misc/mask_MB4R3.png" class="giphy-embed" height="140" width="140" alt="SMS Image">
    </td>
    <td>
        <img src="misc/img_MB4R3.png" class="giphy-embed" height="140" width="140" alt="SMS Image">
    </td>
    <td>
        <img src="misc/fastMRI_MB4R3.gif" frameborder="0" class="giphy-embed" allowfullscreen height="140" width="140" alt="Recon Image">
    </td>
    
  </tr>
</table>


## Citation
```
@article{huang2024robust,
  title={Robust Simultaneous Multislice MRI Reconstruction Using Deep Generative Priors},
  author={Huang, Shoujin and Luo, Guanxiong and Wang, Yuwan and Yang, Kexin and Zhang, Lingyan and Liu, Jingzhe and Guo, Hua and Wang, Min and Lyu, Mengye},
  journal={arXiv preprint arXiv:2407.21600},
  year={2024}
}
```
