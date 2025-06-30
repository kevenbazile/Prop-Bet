from setuptools import setup, find_packages

setup(
    name="wagerbrain",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "numpy",
        "pandas", 
        "scipy"
    ],
    python_requires=">=3.7",
)