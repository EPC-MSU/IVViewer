from setuptools import find_packages, setup


setup(name="ivviewer",
      version="1.0.5",
      description="A configurable Qt widget that displays IV curves",
      url="https://gitlab.ximc.ru/eyepoint/ivviewer",
      author="EPC MSU",
      author_email="info@physlab.ru",
      packages=find_packages(),
      python_requires=">=3.6",
      install_requires=[
          "dataclasses==0.8; python_version~='3.6.0'",
          "numpy",
          "PyQt5",
          "PyQt5-sip",
          "PythonQwt",
      ],
      package_data={"ivviewer": ["media/*"]}
      )
