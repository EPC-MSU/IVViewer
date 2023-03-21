from setuptools import find_packages, setup


setup(name="ivviewer",
      version="0.1.13",
      description="A configurable Qt widget that displays IV curves",
      url="https://gitlab.ximc.ru/eyepoint/ivviewer",
      author="EPC MSU",
      author_email="info@physlab.ru",
      packages=find_packages(),
      python_requires=">=3.6, <=3.9.13",
      install_requires=[
          "dataclasses==0.8; python_version~='3.6.0'",
          "numpy==1.18.1",
          "PyQt5>=5.8.2, <=5.15.2",
          "PyQt5-sip>=12.0",
          "PythonQwt==0.8.3",
      ],
      package_data={"ivviewer": ["media/*"]}
      )
