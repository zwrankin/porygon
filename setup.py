from setuptools import find_packages, setup

with open('requirements.txt') as f:
    requirements = f.read().splitlines()
    requirements.reverse()  # somehow order ets reversed, need cmake installed first

setup(
    name='porygon',
    packages=find_packages(),
    install_requires=requirements,
    version='0.1.0',
    description='Tools to visualize geospatial data using folium',
    author='Zane Rankin',
    license='MIT',
)
