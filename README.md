# :zap: ZapPy :zap:

A collection of python modules of useful class methods and example scripts for pulling and analyzing diagnostic data from the ZaP-HD experiment.

## Table of Contents
- [Tasks/Current Status](#Tasks/Current-Status)
- [Dependencies](#Dependencies)
- [Installation](#Installation)
- [Modules](#Modules)
- [Contributing](#Contributing)
    - [Checking Out the Repo](#checking-out-the-repo)
    - [Committing and Pushing Changes](#committing-and-pushing-changes)

## Tasks/Current Status
WIP


## Dependencies
- [Numpy](https://numpy.org/)
- [Scipy](https://scipy.org/)
- [Matplotlib](https://matplotlib.org/)
- [Spe2py](https://github.com/ashirsch/spe2py)
- [Matlab](https://www.mathworks.com/products/matlab.html)
- [Matlab Engine Python API]()

## Installation

### For Just Analysis
1. Download the .zip file of the repository.
2. Run `pip install -r requirements.txt` to install dependencies.
3. Follow the instructions [here](https://www.mathworks.com/help/matlab/matlab_external/install-the-matlab-engine-for-python.html) to add Matlab support (needed for reading SPE v2.x files). Make sure that it's installed somewhere on the `$PATH` for python.
4. Happy analyzing! :fire:

### For Coding and Analysis
See [Contributing](#contributing).

## Modules

### Spectroscopy
Reads in .SPE data from spectrometer. Reduces spectral data through binning and creating regions of interest. Creates gaussian fits to spectral data for temperature and wavelength analysis. Zeeman splitting support coming soon.


## Contributing
Feel free to fork this repo or create a new branch. You can push to main if your contributions work, otherwise open a pull request so ensure some stability for the repo.

*Ensure that you have the most up to date repo before making changes.*

FOR THE LOVE OF GOD PLEASE DOCUMENT YOUR CODE

### Checking Out the Repo
1. In a terminal, `cd` into the directory where you plan to work on the repo.
2. Once in the directory, use `git clone https://github.com/bennettdiamond/ZapPy.git` to clone the repo.
3. In python, run `pip install -r requirements.txt` to install dependencies.
4. Follow the instructions [here](https://www.mathworks.com/help/matlab/matlab_external/install-the-matlab-engine-for-python.html) to add Matlab support (needed for reading SPE v2.x files). Make sure that it's installed somewhere on the `$PATH` for python.
5. Happy analyzing/coding! :fire:


### Committing and Pushing Changes
1. Stage and commit changes using the command `git commit -a -m "{Comment changes here}"` or `git commit {filename} -m "{Comment changes here}"`.
2. Push the changes using `git push https://github.com/bennettdiamond/ZapPy.git {branch name}`.