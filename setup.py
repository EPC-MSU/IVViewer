from setuptools import setup, find_packages


setup(
    version="0.1.13",
    name="ivviewer",
    packages=find_packages(),
    install_requires=[
        "PyQt5",
        "numpy==1.18.1",
        "PythonQwt==0.8.3",
        "dataclasses==0.8"
    ],
    package_data={"ivviewer": ["media/*"]}
)
