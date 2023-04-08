#!/bin/bash
systems=("taco" "blas" "mkl")

SUITESPARSE_INPUT=mimo28x28_system

for i in "${systems[@]}"
do  
    $PATH_TO_MOSAIC_ARTIFACT/mosaic/build/bin/./taco-bench --benchmark_filter=bench_suitesparse_sddmm_$i  --benchmark_format=json --benchmark_out=$PATH_TO_MOSAIC_ARTIFACT/scripts/bench-scripts/suitesparse/$SUITESPARSE_INPUT/$i
done