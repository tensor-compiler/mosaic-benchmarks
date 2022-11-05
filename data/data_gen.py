import numpy as np
import scipy.sparse
import scipy.io
import argparse
import random

import os
from pathlib import Path


def get_prng(args):
    prng = np.random.RandomState(args.seed)
    return prng


def get_benchmark_ranges(bench_name):
    if bench_name == "sddmm_dim":
        dim_range = list(range(100, 2001, 200))  # [100, 2001] step=200
        sp_range = [0.4]
    elif bench_name == "sddmm_sp":
        dim_range = [2000]
        sp_range = [.00625, .0125, .025, .05, .1, .2, .4, .8, 1]
    elif bench_name == "spmv":
        dim_range = list(range(0, 5001, 250))
        sp_range = [0.2, 0.4]
    elif bench_name == "plus3t":
        dim_range = [200]
        sp_range = [.00625, .0125, .025, .05, .1, .2, .4, .8, 1]
    else:
        raise NotImplementedError
    return dim_range, sp_range


def gen_urand_mat(dims, nnz_percents, args):
    out_dir_path = os.path.join(args.out_dir, args.bench)
    os.makedirs(Path(out_dir_path), exist_ok=True)

    prng = get_prng(args)
    for dim in dims:
        for nnz_percent in nnz_percents:
            print("Generating data for " + str(dim) + " x " + str(nnz_percent) + "...")
            mat = scipy.sparse.random(dim, dim, density=nnz_percent, random_state=prng, data_rvs=np.ones)
            path = os.path.join(out_dir_path, "B_" + str(dim) + "_" + str(nnz_percent) + ".mtx")
            scipy.io.mmwrite(path, mat)


def gen_urand_3t(dims, nnz_percents, args):
    assert args.bench == "plus3t"

    out_dir_path = os.path.join(args.out_dir, args.bench)
    os.makedirs(Path(out_dir_path), exist_ok=True)

    prng = get_prng(args)
    for dim in dims:
        for nnz_percent in nnz_percents:
            print("Generating data for " + str(dim) + " x " + str(nnz_percent) + "...")

            t1_path = os.path.join(out_dir_path, "B_" + str(dim) + "_" + str(nnz_percent) + ".tns")
            t2_path = os.path.join(out_dir_path, "C_" + str(dim) + "_" + str(nnz_percent) + ".tns")
            with open(t1_path, "w+") as ft1:
                with open(t2_path, "w+") as ft2:
                    for i in range(dim):
                        for j in range(dim):
                            for k in range(dim):
                                rand1 = prng.random(1)[0]
                                if rand1 <= nnz_percent:
                                    ft1.write(str(i) + " " + str(j) + " " + str(k) + " 2\n")
                                if prng.random(1)[0] <= nnz_percent:
                                    ft2.write(str(i) + " " + str(j) + " " + str(k) + " 2\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate sparse data for Mosaic evaluation")
    parser.add_argument("--out_dir", type=str, default="./spdata", help="Where to writeout mtx files")
    parser.add_argument("--seed", default=0, type=int, help="PRNG RandomState Seed")
    parser.add_argument("--bench", type=str, help="Benchmark name")
    parser.add_argument("--dim", type=int, default=None, help="Dimension")
    parser.add_argument("--nnz", type=float, default=None, help="% nnz")

    args = parser.parse_args()

    random.seed(args.seed)
    if args.dim is not None and args.nnz is not None:
        dims = [args.dim]
        nnz_percents = [args.nnz]
    else:
        dims, nnz_percents = get_benchmark_ranges(args.bench)

    if args.bench in ["sddmm_dim", "sddmm_sp", "spmv"]:
        gen_urand_mat(dims, nnz_percents, args)
    elif args.bench == "plus3t":
        gen_urand_3t(dims, nnz_percents, args)
