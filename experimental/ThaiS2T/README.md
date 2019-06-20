# ThaiAutoTranscribe

## Setup guide for Fedora

1. Clone this repository and make sure that gcc ,g++ and python 3.x available
2. Make sure redhat-rpm-config and other static package is avialable

   `$ sudo dnf install redhat-rpm-config`
   `$ sudo dnf install python3-devel`

3. Run following: 
    
    `$ cd [projectpath]`

    `$ python3 -m venv env`

    `$ source ./env/bin/activate`

    `$ pip install -r requirement.txt`
    
    `$ cd ./pyAudioAnalysis`

    `$ pip install -e .`
    
4. Done