from setuptools import find_packages, setup

with open('requirements.txt') as f:
    requirements = f.read().splitlines()
    requirements.reverse  # need to ensure this order is same as requirements.txt

setup(
    name='porygon',
    packages=find_packages(),
    install_requires=requirements,
    version='0.1.0',
    description='Tools to visualize geospatial data using folium',
    author='Zane Rankin',
    license='MIT',
)
