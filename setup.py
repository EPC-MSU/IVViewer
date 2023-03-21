from setuptools import find_packages, setup


setup(
    version="0.1.13",
    name="ivviewer",
    packages=find_packages(),
    install_requires=[
        "dataclasses==0.8"
        "numpy==1.18.1",
        "PyQt5>=5.8.2, <=5.15.0",
        "PythonQwt==0.8.3",
    ],
    package_data={"ivviewer": ["media/*"]}
)
