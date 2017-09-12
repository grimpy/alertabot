from setuptools import setup, find_packages

version = '0.0.1'

setup(
    name="alerta-gig",
    version=version,
    description='Example Alerta plugin for gig support alerts',
    url='https://github.com',
    license='Apache License 2.0',
    author='Ashraf Fouda',
    author_email='foudaa@greenitglobe.com',
    packages=find_packages(),
    py_modules=['alerta_gig'],
    install_requires=[],
    include_package_data=True,
    zip_safe=True,
    entry_points={
        'alerta.plugins': [
            'gig = alerta_gig:GIGAlert'
        ]
    }
)
