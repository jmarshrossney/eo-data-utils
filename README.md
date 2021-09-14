# Salinity from space

## Installation

The easiest thing is to create a conda environment using the `environment.yml` file provided, which uses Python 3.9.

```
conda env create --name sfs --file environment.yml
```

Alternatively, install the following packages manually.

1. NumPy, SciPy, Matplotlib, Pandas, IPython
2. PyTorch, PyTorch-Lightning, Tensorboard
3. Jupyterlab (or just Jupyter)
4. Seaborn
5. Black (if you really don't want it you will have to comment out the lines `%load_ext lab_black`)
