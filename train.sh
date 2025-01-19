MODEL_FLAGS="--image_size 256 --num_channels 128 --num_res_blocks 2 --num_heads 4 --learn_sigma True"
DIFFUSION_FLAGS="--diffusion_steps 1000 --noise_schedule linear"
TRAIN_FLAGS="--use_fp16 True --lr 1e-4 --batch_size 8"

python scripts/image_train.py --data_dir data --log_dir paper_log/log0 $MODEL_FLAGS $DIFFUSION_FLAGS $TRAIN_FLAGS

# mpiexec -n 8 python scripts/image_train.py --data_dir data --log_dir new_log/log1 $MODEL_FLAGS $DIFFUSION_FLAGS $TRAIN_FLAGS

# python scripts/image_sample.py $MODEL_FLAGS --model_path log1/ema_0.9999_030000.pt
