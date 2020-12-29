import setuptools
import os

with open("README.md", "r") as fh:
    long_description = fh.read()

with open('requirements.txt', 'rt') as reqs_file:
    REQUIREMENTS = reqs_file.readlines()

setuptools.setup(
    name="tilt-pitch",
    version=os.getenv('PITCH_VERSION', "0.0.1"),
    author="Lin Meyer",
    author_email="lin@linmeyer.net",
    description="Simple replacement for the Tilt Hydrometer mobile apps and TiltPi with lots of features",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/linjmeyer/tilt-pitch/",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: POSIX :: Linux",
    ],
    python_requires='>=3.7',
    install_requires=[
        'pybluez',
        'influxdb',
        'prometheus_client',
        'python-interface',
        'jsonpickle',
        'beacontools',
        'pyfiglet'
    ],
)
