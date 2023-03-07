import argparse
import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import csv

import os
from pathlib import Path

colors = {"tblis" : "olive", "gsl" : "green", "blas" : "red", "taco" : "blue", "gsl_tensor" : "cyan", \
          "dot_blas" : "gold", "dot_gsl" : "grey", "gemv_blas" : "purple", "gemv_gsl" : "pink", "mkl" :"black", "cuda":"green",\
         "dot_mkl" : "silver", "gemv_mkl" : "yellow", "stardust":"orange",
         "taco_csr" : "green", "taco_coo" : "red", "row" : "olive", "col" : "green", "block" : "red", 
         "block_diagonal" : "blue", "random" : "cyan"}

markers = {"tblis" : "o", "gsl" : "p", "blas" : "*", "taco" : ".", "gsl_tensor" : ".", \
          "dot_blas" : ".", "dot_gsl" : ".", "gemv_blas" : ".", "gemv_gsl" : "p", "mkl" :"v", "cuda":"s",\
         "dot_mkl" : ".", "gemv_mkl" : ".", "stardust":"1", "taco_coo" : "p", "taco_csr" : ".", \
          "row" : "o", "col" : "p", "random" : "*", "block" : ".", "block_diagonal" : "."}
                      
linestyles = {"tblis" : "-", "gsl" : "-", "blas" : "-", "taco" : "-", "gsl_tensor" : "-", \
          "dot_blas" : "-", "dot_gsl" : "-", "gemv_blas" : "-", "gemv_gsl" : "-", "mkl" :"--", "cuda":"-",\
         "dot_mkl" : "-", "gemv_mkl" : "-", "stardust":"-", "taco_coo" : "-", "taco_csr" : "--",\
           "row" : "-", "col" : "-", "block" : "-", "block_diagonal" : "-", "random" : "-"  }


def generate_dim_plot(name, directory, systems, expr, start, interval, stardust=None, filtered=None, unit="us"):
    
    result = None
    
    for system in systems:
        data = json.load(open(f'{directory}/{system}'))
        df = pd.DataFrame(data["benchmarks"])
        df = df[df['aggregate_name'] == "median"]['real_time']
        df = df.reset_index(drop=True)
        df = df.rename_axis('dimension').reset_index()
        df['dimension'] = df['dimension']*interval + start
        
        df.rename(columns = {'real_time': f'{system}_real_time'}, inplace = True)
        
        if result is None:
            result = df
        else:
            result = pd.merge(result, df, on='dimension', how='outer')
        
    if stardust is not None:
        data = pd.read_csv(os.getenv("MOSAIC_DIR") + "/mosaic-benchmarks/stardust-runs/spmv_plus2.csv")
        if stardust == "SpMV":
            df = pd.DataFrame(data[["app", "cycles", "dim_0_2"]])
            df.rename(columns = {'dim_0_2': f'dimension'}, inplace = True)
        else:
            df = pd.DataFrame(data[["app", "cycles", "dataset"]])
        # Stardust cycles are in ns and call to it takes 0.0002 ms
        df[df['app'] == stardust]
        if unit == "ms":
            df['cycles'] = df['cycles'] *1e-6 + 0.0002
        elif unit == "us":
            df['cycles'] = df['cycles'] * 1e-3 + 0.0002*1000
        else:
            raise NotImplemented
        df.rename(columns = {'cycles': f'stardust_real_time'}, inplace = True)
        result = pd.merge(result, df, on='dimension', how='outer')
        systems.append("stardust")
        
    if filtered is not None: 
        for system in filtered:
            data = pd.read_csv(f'{directory}/{system}_filter')
            df = data['real_time']
            df = df.reset_index(drop=True)
            df = df.rename_axis('dimension').reset_index()
            df['dimension'] = df['dimension']*interval + start
        
            df.rename(columns = {'real_time': f'{system}_real_time'}, inplace = True)
            result = pd.merge(result, df, on='dimension', how='outer')
        systems = systems + filtered
            
        
    full_plt = result.plot(kind = 'line', x = 'dimension', y = [f'{i}_real_time' for i in systems],  
                           color=[colors[system] for system in systems], 
                           #marker='plot_marker',
                           title=expr)
    
    for i, line in enumerate(full_plt.get_lines()):
        line.set_marker(markers[systems[i]])
        line.set_linestyle(linestyles[systems[i]])

    plt.ylabel('Real Time (ms)')
    plt.xlabel('Dimension')
    
    plt.savefig(f'{directory}/raw_graph.svg', format="svg")

    f, (ax, ax2) = plt.subplots(2, 1, sharex=True)
    result.plot(kind = 'line', x = 'dimension', y = [f'{i}_real_time' for i in systems], color=[colors[system] for system in systems], ax=ax)
    result.plot(kind = 'line', x = 'dimension', y = [f'{i}_real_time' for i in systems], color=[colors[system] for system in systems], ax=ax2)    
    
    full_plt = result.plot(kind = 'line', x = 'dimension', y = [f'{i}_real_time' for i in systems],  color=[colors[system] for system in systems], title=expr)
    
    for i, line in enumerate(full_plt.get_lines()):
        line.set_marker(markers[systems[i]])
        line.set_linestyle(linestyles[systems[i]])
    full_plt.legend(full_plt.get_lines(), [f'{i}_real_time' for i in systems])

    plt.yscale("log")
    plt.ylabel('Real Time (ms)')
    plt.xlabel('Dimension')
    
    plt.savefig(f'{directory}/{name}.pdf', format="pdf")


def generate_sparsity_plots(name, directory, systems, expr, sparse, stardust=None, unit="us"):

    print(stardust)
    
    result = None
    
    for system in systems:
        data = json.load(open(f'{directory}/{system}'))
        df = pd.DataFrame(data["benchmarks"])
        df = df.reset_index(drop=True)
        df = df.rename_axis('sparisty').reset_index()
        df.rename(columns = {'real_time': f'{system}_real_time'}, inplace = True)
        
        if result is None:
            result = df
        else:
            result = pd.merge(result, df, on='sparisty', how='outer')
    
    if stardust is not None:
        data = pd.read_csv(os.getenv("MOSAIC_DIR") + "/stardust-runs/spmv_plus2.csv")
        if stardust == "SpMV":
            df = pd.DataFrame(data[["app", "cycles", "dataset"]])
            df.rename(columns = {'dim_0_2': f'dimension'}, inplace = True)
        elif stardust == "Plus2CSR":
            df = pd.DataFrame(data[["app", "cycles", "dataset", "par"]])
            df.sort_values(by=['dataset'])
            df = df[df['par'] == 8]
        # Stardust cycles are in ns and call to it takes 0.0002 ms
        df = df[df['app'] == stardust]
        if unit == "ms":
            df['cycles'] = df['cycles'] *1e-6 + 0.0002
        elif unit == "us":
            df['cycles'] = df['cycles'] *1e-3 + 0.0002*1000
        df = df.reset_index(drop=True)
        df = df.rename_axis('sparisty').reset_index()
        print(df)
        df.rename(columns = {'cycles': f'stardust_real_time'}, inplace = True)
        result = pd.merge(result, df, on='sparisty', how='outer')
        systems.append("stardust")
    
    sparse = [str(i) for i in sparse]
    result['sparisty'] = sparse
    full_plt = result.plot(kind = 'line', x = 'sparisty', y = [f'{i}_real_time' for i in systems],  color=[colors[system] for system in systems], title=expr)

    for i, line in enumerate(full_plt.get_lines()):
        line.set_marker(markers[systems[i]])
        line.set_linestyle(linestyles[systems[i]])
    full_plt.legend(full_plt.get_lines(), [f'{i}_real_time' for i in systems])
        
    f, (ax, ax2) = plt.subplots(2, 1, sharex=True)
    result.plot(kind = 'line', x = 'sparisty', y = [f'{i}_real_time' for i in systems], color=[colors[system] for system in systems], ax=ax)
    result.plot(kind = 'line', x = 'sparisty', y = [f'{i}_real_time' for i in systems], color=[colors[system] for system in systems], ax=ax2)
    

    full_plt = result.plot(kind = 'line', x = 'sparisty', y = [f'{i}_real_time' for i in systems],  color=[colors[system] for system in systems], title=expr)
    for i, line in enumerate(full_plt.get_lines()):
        line.set_marker(markers[systems[i]])
        line.set_linestyle(linestyles[systems[i]])
    full_plt.legend(full_plt.get_lines(), [f'{i}_real_time' for i in systems])
    
    plt.yscale("log")
    plt.ylabel('Real Time (ms)')
    plt.xlabel('sparisty')
    
    plt.savefig(f'{directory}/{name}.pdf', format="pdf")
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate Figures from Data")
    parser.add_argument("--data_dir", type=str, default="./", help="Where To Find the Data")
    parser.add_argument("--name", type=str, default="No Name", help="Name of the Figure")
    parser.add_argument("--x_label", type=str, default="Dimension", help="Label of X axis")
    parser.add_argument("--y_label", type=str, default="Runtime (us)", help="Label of Y axis")
    parser.add_argument("--start_dim", type=int, default=0, help="Dimension to Start")
    parser.add_argument("--step_dim", type=int, default=0, help="Step for dimension")
    parser.add_argument("--type", type=str, default="", help="Which type of plot to generate")
    parser.add_argument('--systems', type=str, default="")
    parser.add_argument('--sparsity', type=str, default="")
    parser.add_argument('--stardust', type=str, default="")
    args = parser.parse_args()

    print(args.stardust)
    
    if args.type == "vary_sparse":
        if (args.stardust == "Plus2CSR"):
            generate_sparsity_plots(args.name, args.data_dir, args.systems.split(','),\
                                args.name, [float(item) for item in args.sparsity.split(',')], args.stardust)
        else: 
            generate_sparsity_plots(args.name, args.data_dir, args.systems.split(','),\
                                args.name, [float(item) for item in args.sparsity.split(',')])
    elif args.type == "vary_dim":
        if (args.stardust == "SpMV"):
            generate_dim_plot(args.name, args.data_dir, args.systems.split(','), args.name,\
                    args.start_dim, args.step_dim, args.stardust)
        else:
            generate_dim_plot(args.name, args.data_dir, args.systems.split(','), args.name,\
                    args.start_dim, args.step_dim)
    else:
        print("Type can only be of two types, vary_sparse and vary_dim")



