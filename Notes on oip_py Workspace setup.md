Notes on oip_py Workspace Setup 
-------------------------------------

- Install Anaconda
  - When installing Anaconda
    - check box "Add Anaconda to my PATH environment variable" (otherwise conda not found from command prompts)
      - failing this,edit the _system_ path manually to add "C:\ProgramData\Anaconda3\condabin"
      - see System Properties, Advanced, Environment Variables, System Path
    - install for current user, not all users (otherwise modifying environments requires admin privileges)
      - failing this, find folder C:\ProgramData\Anaconda3
      - right click on the folder for Properties, set security privileges for all Users to "Full control" (properties will be altered for every file in the folder)
    - See [Anaconda User Guide](https://docs.conda.io/projects/conda/en/latest/user-guide/index.html)
    - See [Anaconda Command Reference](https://docs.conda.io/projects/conda/en/latest/commands.html)

- import oip_env environment for conda
  - "conda env create --file oip_env.yml"

- install git
    - with [git Download for Windows](https://git-scm.com/download/win)
    - optionally install the GUI GitHub for Desktop, if using Github

- Install VC Code
  - add extensions
    - Jupyter
    - Python
  - set Black as auto-styler for python (how was this done?)