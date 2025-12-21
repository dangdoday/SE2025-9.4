from setuptools import setup, find_packages

setup(
    name="binancebot",
    version="1.0.0",
    packages=find_packages(where="backend"),
    package_dir={"": "backend"},
    install_requires=[
        # Dependencies will be read from requirements.txt
    ],
)
