import math
import random

from PIL import Image
import blobfile as bf
from mpi4py import MPI
import numpy as np
import torch
from torch.utils.data import DataLoader, Dataset


def load_data(
    *,
    data_dir,
    batch_size,
    image_size,
    class_cond=False,
    deterministic=False,
    random_crop=False,
    random_flip=True,
):
    """
    For a dataset, create a generator over (images, kwargs) pairs.

    Each images is an NCHW float tensor, and the kwargs dict contains zero or
    more keys, each of which map to a batched Tensor of their own.
    The kwargs dict can be used for class labels, in which case the key is "y"
    and the values are integer tensors of class labels.

    :param data_dir: a dataset directory.
    :param batch_size: the batch size of each returned pair.
    :param image_size: the size to which images are resized.
    :param class_cond: if True, include a "y" key in returned dicts for class
                       label. If classes are not available and this is true, an
                       exception will be raised.
    :param deterministic: if True, yield results in a deterministic order.
    :param random_crop: if True, randomly crop the images for augmentation.
    :param random_flip: if True, randomly flip the images for augmentation.
    """
    if not data_dir:
        raise ValueError("unspecified data directory")
    all_files = _list_image_files_recursively(data_dir)
    classes = None
    if class_cond:
        # Assume classes are the first part of the filename,
        # before an underscore.
        class_names = [bf.basename(path).split("_")[0] for path in all_files]
        sorted_classes = {x: i for i, x in enumerate(sorted(set(class_names)))}
        classes = [sorted_classes[x] for x in class_names]
    dataset = ImageDataset(
        image_size,
        all_files,
        classes=classes,
        shard=MPI.COMM_WORLD.Get_rank(),
        num_shards=MPI.COMM_WORLD.Get_size(),
        random_crop=random_crop,
        random_flip=random_flip,
    )
    if deterministic:
        loader = DataLoader(
            dataset, batch_size=batch_size, shuffle=False, num_workers=1, drop_last=True
        )
    else:
        loader = DataLoader(
            dataset, batch_size=batch_size, shuffle=True, num_workers=1, drop_last=True
        )
    while True:
        yield from loader


def _list_image_files_recursively(data_dir):
    results = []
    for entry in sorted(bf.listdir(data_dir)):
        full_path = bf.join(data_dir, entry)
        ext = entry.split(".")[-1]
        if "." in entry and ext.lower() in ["jpg", "jpeg", "png", "gif",'npz']:
            key = full_path.split('/')[-1].split('.')[-2].split('_')[-1]
            # if '_'+key in ['_00','_01','_02','_03','_04','_05','_42','_43','_44','_45','_46','_47']:
            if '_'+key in ['_00','_01','_02','_03','_04', '_43','_44','_45','_46','_47']:
                ...
            else:
                # if 'Sub2023092402' in full_path or 'Sub2023092501' in full_path or 'Sub2023092502' in full_path or 'Sub2023092503' in full_path or 'Sub2023092504' in full_path :
                
                # if 'Sub2023092504' in full_path or 'Sub2023092501' in full_path or 'Sub2023092702' in full_path or 'Sub2023092509' in full_path or 'Sub2023092705' in full_path:
                # if 'Sub2023092504' in full_path or 'Sub2023092501' in full_path or 'Sub2023092702' in full_path:
                if 'Sub2023092504' in full_path:
                    results.append(full_path)
        elif bf.isdir(full_path):
            results.extend(_list_image_files_recursively(full_path))
    return results


class ImageDataset(Dataset):
    def __init__(
        self,
        resolution,
        image_paths,
        classes=None,
        shard=0,
        num_shards=1,
        random_crop=False,
        random_flip=True,
    ):
        super().__init__()
        self.resolution = resolution
        self.local_images = image_paths[shard:][::num_shards]
        print(len(self.local_images))
        self.local_classes = None if classes is None else classes[shard:][::num_shards]
        self.random_crop = random_crop
        self.random_flip = random_flip

    def augment(self,x):
        prob = random.random()
        if prob < 0.5:
            x = torch.flip(x, dims=[2])

        prob = random.random()
        if prob < 0.5:
            x = torch.flip(x, dims=[1])

        prob = random.random()
        if prob < 0.5:
            rotation = random.randint(0, 3)
            x = torch.rot90(x, rotation, dims=[1, 2])
        return x

    def float2cplx(self,float_in):
        return np.array(float_in[...,0]+1.0j*float_in[...,1], dtype='complex64')

    def cplx2float(self, cplx_in):
        return np.array(np.stack((cplx_in.real, cplx_in.imag), axis=-1), dtype='float32')
    
    def __len__(self):
        return len(self.local_images)

    def __getitem__(self, idx):
        path = self.local_images[idx]
        
        imgs = np.squeeze(np.load(path)['rss'])[np.newaxis, ...]

        if 'Sub2023092402' in path:
            imgs = np.roll(imgs,64,-1)
        
        imgs = imgs / np.max(np.abs(imgs), axis=(1,2), keepdims=True)
        imgs = self.cplx2float(imgs)[0]
        
        arr = ( imgs * 2 ) - 1

        arr = np.transpose(arr, [2, 0, 1]).astype(np.float32) #(2,320,320)

        arr = torch.from_numpy(arr)
        arr = torch.nn.functional.interpolate(arr[None],size=[128,128],mode='nearest')[0]

        arr = self.augment(arr)

        out_dict = {}

        return arr, out_dict


def center_crop_arr(pil_image, image_size):
    # We are not on a new enough PIL to support the `reducing_gap`
    # argument, which uses BOX downsampling at powers of two first.
    # Thus, we do it by hand to improve downsample quality.
    while min(*pil_image.size) >= 2 * image_size:
        pil_image = pil_image.resize(
            tuple(x // 2 for x in pil_image.size), resample=Image.BOX
        )

    scale = image_size / min(*pil_image.size)
    pil_image = pil_image.resize(
        tuple(round(x * scale) for x in pil_image.size), resample=Image.BICUBIC
    )

    arr = np.array(pil_image)
    crop_y = (arr.shape[0] - image_size) // 2
    crop_x = (arr.shape[1] - image_size) // 2
    return arr[crop_y : crop_y + image_size, crop_x : crop_x + image_size]


def random_crop_arr(pil_image, image_size, min_crop_frac=0.8, max_crop_frac=1.0):
    min_smaller_dim_size = math.ceil(image_size / max_crop_frac)
    max_smaller_dim_size = math.ceil(image_size / min_crop_frac)
    smaller_dim_size = random.randrange(min_smaller_dim_size, max_smaller_dim_size + 1)

    # We are not on a new enough PIL to support the `reducing_gap`
    # argument, which uses BOX downsampling at powers of two first.
    # Thus, we do it by hand to improve downsample quality.
    while min(*pil_image.size) >= 2 * smaller_dim_size:
        pil_image = pil_image.resize(
            tuple(x // 2 for x in pil_image.size), resample=Image.BOX
        )

    scale = smaller_dim_size / min(*pil_image.size)
    pil_image = pil_image.resize(
        tuple(round(x * scale) for x in pil_image.size), resample=Image.BICUBIC
    )

    arr = np.array(pil_image)
    crop_y = random.randrange(arr.shape[0] - image_size + 1)
    crop_x = random.randrange(arr.shape[1] - image_size + 1)
    return arr[crop_y : crop_y + image_size, crop_x : crop_x + image_size]
