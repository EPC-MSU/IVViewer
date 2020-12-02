from setuptools import setup, find_packages


setup(
    version="0.1.4",
    name="ivviewer",
    packages=find_packages(),
    install_requires=[
        "PyQt5>=5.8.2, <=5.15.0",
        "numpy==1.14.5",
        "PythonQwt==0.8.3",
        "dataclasses==0.8"
    ]
)
