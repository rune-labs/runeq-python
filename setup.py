from setuptools import find_packages, setup

package_name = 'runeq'

with open('README.md') as r:
    long_description = r.read()

with open('requirements/common.txt', 'r') as r:
    install_requires = r.read().splitlines()

setup(
    name=package_name,
    version='0.3.0',
    author='Rune Labs',
    maintainer_email='support@runelabs.io',
    description='Query data from Rune Labs APIs',
    long_description=long_description,
    long_description_content_type='text/markdown',
    keywords='rune api query',
    url='https://github.com/rune-labs/runeq-python',
    packages=find_packages(),
    install_requires=install_requires,
    test_suite='tests',
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
)
