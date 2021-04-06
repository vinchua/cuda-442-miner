# cuda-442-miner
For cpen442 coin mining contest 2020.

## Instructions
Run 
```
python cudaminer.py
```

### Requirements
```
python -m pip install requirements.txt
```

## CUDA
The CUDA toolkit is required to compile the .cu and .cuh files.
```
nvcc -o cpen442hash main.cu -arch=sm_61
```

## Kernel adapted from https://github.com/moffa13/SHA256CUDA

Because of std::cin ignoring spaces, including newlines, use getline(std::cin, in) instead.

`$ nvcc -o hash_program main.cu`

Example run:

```
james@acer-nitro5:~/src/cuda/SHA256CUDA$ ./hash_program 
Enter a message : This is a test
Nonce : 0
Difficulty : 7

Shared memory is 16400B
772009 hash(es)/s
Nonce : 8388608
30226098This is a test
00000001adff67cab9570a236d8490c0f5efee91e0303562e2d95ff7c3b7f3ec
james@acer-nitro5:~/src/cuda/SHA256CUDA$
```

On my system with a GTX 1050 GPU, I get 6.5-12 million hash/s.
On my GTX 970, I get 135 millions hashes/s in Release mode and max speed optimization (-O2)

