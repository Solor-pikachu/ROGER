# ROGER
👏👏 [Robust Simultaneous Multislice MRI Reconstruction Using Deep Generative Priors](https://arxiv.org/abs/2407.21600)

The code will come soon.

## Reconstruction
<table border="1" cellspacing="10" cellpadding="10">
  <tr>
    <th>SMS K-space</th>
    <th>SMS image</th>
    <th>Recon</th>
    <th>GT</th>
  </tr>
  <tr>
    <td>
        <img src="mics/img_MB4R2.png" class="giphy-embed" width="200" height="200">
        <img src="mics/img_MB4R2.png" class="giphy-embed" width="200" height="200">
    </td>
    <td>
        <img src="mics/img_MB4R2.png" class="giphy-embed" width="200" height="200">
        <img src="mics/img_MB4R3.png" class="giphy-embed" width="200" height="200">
    </td>
    <td>
        <img src="mics/fastMRI_MB4R2.gif" class="giphy-embed" width="200" height="200">
        <img src="mics/fastMRI_MB4R3.gif" class="giphy-embed" width="200" height="200">
    </td>
    <td>
        <img src="mics/gt.gif" class="giphy-embed" width="200" height="200">
    </td>
  </tr>
</table>

| SMS K-space | SMS image | Recon | GT |
|-------------|-----------|--------|----|
| ![K-space Image 1](mics/img_MB4R2.png) ![K-space Image 2](mics/img_MB4R2.png) | ![SMS Image MB4R2](mics/img_MB4R2.png) ![SMS Image MB4R3](mics/img_MB4R3.png) | ![Recon MB4R2](mics/fastMRI_MB4R2.gif) ![Recon MB4R3](mics/fastMRI_MB4R3.gif) | ![Ground Truth](mics/gt.gif) |


<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        table {
            width: 100%;
            border-collapse: collapse;
            table-layout: fixed;
        }
        th, td {
            border: 1px solid #ddd;
            padding: 10px;
            text-align: center;
        }
        th {
            width: 25%;
        }
        td {
            width: 25%;
        }
        td img {
            width: 200px; /* 统一的宽度 */
            height: 200px; /* 统一的高度 */
            object-fit: cover; /* 保持图片比例，同时填满单元格 */
            display: block;
            margin: 0 auto;
        }
    </style>
</head>
<body>
    <table>
        <tr>
            <th>SMS K-space</th>
            <th>SMS image</th>
            <th>Recon</th>
            <th>GT</th>
        </tr>
        <tr>
            <td>
                <img src="mics/img_MB4R2.png" alt="K-space Image 1">
                <img src="mics/img_MB4R2.png" alt="K-space Image 2">
            </td>
            <td>
                <img src="mics/img_MB4R2.png" alt="SMS Image MB4R2">
                <img src="mics/img_MB4R3.png" alt="SMS Image MB4R3">
            </td>
            <td>
                <img src="mics/fastMRI_MB4R2.gif" alt="Recon MB4R2">
                <img src="mics/fastMRI_MB4R3.gif" alt="Recon MB4R3">
            </td>
            <td>
                <img src="mics/gt.gif" alt="Ground Truth">
                <img src="mics/gt.gif" alt="Ground Truth">
            </td>
        </tr>
    </table>
</body>
</html>




## Citation
```
@article{huang2024robust,
  title={Robust Simultaneous Multislice MRI Reconstruction Using Deep Generative Priors},
  author={Huang, Shoujin and Luo, Guanxiong and Wang, Yuwan and Yang, Kexin and Zhang, Lingyan and Liu, Jingzhe and Guo, Hua and Wang, Min and Lyu, Mengye},
  journal={arXiv preprint arXiv:2407.21600},
  year={2024}
}
```
