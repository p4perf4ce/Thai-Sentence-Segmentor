from setuptools import find_packages, setup

with open("requirements.txt", "r", encoding="utf-8") as f:
    requirements = f.read().splitlines()

setup(name='thaiS2t',
      version='0.2.0A',
      description='Thai Speech to Text Transcript Generator',
      author='Amrest Chinkamol',
      author_email='amrest.c@ku.th',
      url='https://www.p4perf4ce.github.io',
      install_requires=requirements,
      license="Apache Software License 2.0",
)