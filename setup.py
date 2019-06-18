import os
import sys

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

### python-ly
###
### This setup script packages and/or installs:
### - the ly package
### - the ly script
### - the ly-server script


from ly import pkginfo


def packagelist(directory):
    """Return a sorted list with package names for all packages under the given directory."""
    folder, basename = os.path.split(directory)
    return list(sorted(root[len(folder)+1:].replace(os.sep, '.')
        for root, dirs, files in os.walk(directory)
        if '__init__.py' in files))

scripts = ['bin/ly', 'bin/ly-server']
packages = packagelist('./ly')
py_modules = []

with open('README.rst', 'rb') as f:
    long_description = f.read().decode('utf-8')

package_data = {
    'ly.xml': ['*.ily', '*.ly'],
}

#data_files = [
#    ('share/man/man1', ['ly.1']),
#]

classifiers = [
    'Development Status :: 4 - Beta',
    #'Development Status :: 5 - Production/Stable',
    'License :: OSI Approved :: GNU General Public License (GPL)',
    'Operating System :: MacOS :: MacOS X',
    'Operating System :: Microsoft :: Windows',
    'Operating System :: POSIX',
    'Programming Language :: Python :: 2.7',
    'Programming Language :: Python :: 3',
    'Topic :: Multimedia :: Sound/Audio',
    'Topic :: Text Editors',
]

setup(
    name = pkginfo.name,
    version = pkginfo.version,
    description = pkginfo.description,
    long_description = long_description,
    maintainer = pkginfo.maintainer,
    maintainer_email = pkginfo.maintainer_email,
    url = pkginfo.url,
    license = pkginfo.license,
    
    scripts = scripts,
    packages = packages,
    package_data = package_data,
    py_modules = py_modules,
    classifiers = classifiers,
    #data_files = data_files,
    
)

