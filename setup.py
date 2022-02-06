from setuptools import find_packages, setup
setup(
    name='mim365mi',
    version='1.0.0',
    url='https://github.com/catSIXe/m365-mi',
    license='GNU AGPL v3',
    author='catSIXe',
    description='Authenticate and interact with Xiaomi M365 Scooters over BLE(the new Protocol)',
    packages=find_packages(include=['mim365mi', 'mim365mi.*']),
    install_requires=[
        'miauth==0.9.2'
    ],
    python_requires=">=3.6",
)