# Python Installation and Setup

These instructions detail how to set up a Python analysis environment using the Anaconda distribution.

## Introduction

Python is an open-source programming language with a number of packages to facilitate data analysis. A Python **module** is a single .py file that contains functions, and a **package** is a collection of modules. These packages are analogous to toolboxes in MATLAB. Common packages and their uses for data analysis include:

* **Pandas**: data reading/writing, manipulation, analysis
* **Numpy**: handling multi-dimensional array data
* **SciPy**: scientific computing, including support for signal processing and statistics
* **Matplotlib**: data plotting and visualization
* **Scikit Learn**: machine learning
* **Jupyter Notebook**: Python integrated development environment

Rather than installing each of these packages individually, a simplified way to install and manage packages is with a Python distribution, such as **Anaconda**. In addition to simplifying package installation and management, Anaconda also manages **virtual environments**. A virtual environment is an independent copy of Python, which can be tailored with specific versions of packages. Virtual environments will help you maintain dependencies across different projects.

## Installing Python

The latest distribution of Anaconda for Windows, macOS, or Linux can be downloaded at https://www.anaconda.com/download.

Alternatively, if you prefer not to use Anaconda, the latest version of standard Python for your operating system can be downloaded at https://www.python.org/downloads/. Additional modules will have to be installed separately.

In either case, the prompts of the graphical installer should be straightforward.

## Installing the Rune SDK

The Rune software development kit (SDK), known as `runeq`, simplifies the use of our API. It can be installed in a terminal/command prompt as follows:

```
pip install --upgrade pip
pip install runeq
```

Improvements to our SDK are regularly released as new versions, so it is recommended to stay up to date. This can be accomplished by running:

```
pip install --upgrade runeq
```

Additional information on installing Python modules can be found here: https://docs.python.org/3/installing/index.html

## Setting up a Virtual Environment

To make sure that Anaconda installed correctly, enter the following command in a terminal/command prompt:

```
conda list
```

This should print a list of the packages you now have in Python. Note that these packages are currently in your “base” environment. To start a new virtual environment, enter:

```
conda create -n <your_environment_name>
```

To open up a virtual environment, enter:

```
conda activate <your_environment_name>
```

Next, add packages to this environment with:

```
conda install pandas numpy scipy matplotlib scikit-learn jupyter requests 
```

To close out your virtual environment and return to the base environment, enter:

```
conda deactivate
```

## Using Jupyter Notebook

[Jupyter Notebook](https://jupyter.org/) is an open source integrated development environment that runs within a web browser. It is a space to write and execute Python code, generate visualizations, and add data narratives in mark-down cells. To start up a Jupyter Notebook, first activate your virtual environment. Then enter the following in a terminal/command prompt:

```
jupyter notebook
```

This should open up a new browser page, where you can navigate to your directory of interest and start a new notebook or load up an existing one.

Alternatively, Jupyter Notebook (or JupyterLab) can be launched using the Anaconda Navigator GUI. JupyterLab includes a handy file browser, from which notebooks can be launched, and allows multiple notebooks to be run in tabs.

Jupyter Notebook also has a number of (unofficial) extensions for added functionality (https://github.com/ipython-contrib/jupyter_contrib_nbextensions). These extensions are optional, but some may be useful for analyses, such as Variable Inspector and ExecuteTime.

## Initialize API credentials

`runeq` uses YAML-formatted files to manage configuration settings.

You will first need to initialize your API credentials. These credentials are analogous to having a username/password for accessing patient data. You can set up an access token for read access to all patients within your organization. After creating your API credentials, set up a .yaml file with your token and secret. This is a text file that will store your credentials and be referenced by the SDK. See our [`runeq` quickstart](https://runeq.readthedocs.io/en/latest/pages/quickstart.html#configuration) for instructions on setting this up. See different [valid ways to create a config](https://runeq.readthedocs.io/en/latest/pages/config.html).