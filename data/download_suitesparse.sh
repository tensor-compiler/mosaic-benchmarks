#!/bin/bash
#SBATCH -N 1
#SBATCH -t 360

outdir=/nobackup/owhsu/sparse-datasets/suitesparse

mkdir -p $outdir
cd $outdir


#!/bin/bash
#SBATCH -N 1
#SBATCH -t 360

outdir=/nobackup/owhsu/sparse-datasets/suitesparse

mkdir -p $outdir
cd $outdir

# wget https://sparse.tamu.edu/MM/JGD_Homology/ch4-4-b1.tar.gz
# wget https://sparse.tamu.edu/MM/JGD_Homology/ch7-6-b1.tar.gz
# wget https://sparse.tamu.edu/MM/LPnetlib/lpi_itest6.tar.gz
wget https://sparse.tamu.edu/MM/JGD_Relat/relat3.tar.gz
wget https://sparse.tamu.edu/MM/Oberwolfach/LFAT5.tar.gz

# wget https://sparse.tamu.edu/MM/Sandia/adder_dcop_54.tar.gz
# wget https://sparse.tamu.edu/MM/Rajat/rajat12.tar.gz
# wget https://sparse.tamu.edu/MM/Gset/G42.tar.gz
wget https://sparse.tamu.edu/MM/LPnetlib/lp_maros.tar.gz
wget https://sparse.tamu.edu/MM/Meszaros/progas.tar.gz