from setuptools import setup, find_packages

setup(
    name='gfypy',
    version='0.0.6',
    description='Python wrapper for the Gfycat API',
    long_description='Provides an easy to use interface to the API at '
                     'https://developers.gfycat.com/api/.',
    url='https://github.com/noahkw/gfypy',
    author='Noah K W',
    author_email='noah@dreckbu.de',
    license='MIT',
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 3 - Alpha',

        # Indicate who your project is intended for
        'Intended Audience :: Developers',

        # Pick your license as you wish (should match "license" above)
        'License :: OSI Approved :: MIT License',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
    keywords=['gfycat api wrapper'],
    packages=find_packages(), install_requires=['requests', 'tqdm']
)
