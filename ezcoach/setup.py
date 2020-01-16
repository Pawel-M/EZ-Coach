from setuptools import setup

setup(
    name='ezcoach',
    version='0.9',
    packages=['game', 'ezcoach', 'ezcoach.tests', 'examples'],
    package_dir={'': 'src'},
    url='',
    license='',
    author='Paweł Mąka',
    author_email='pawel.maka@protonmail.com',
    description='Framework for training and testing machine learning algorithms as game controllers.',
    install_requires=['numpy', 'matplotlib', 'pandas']
)
