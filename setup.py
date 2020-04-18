from setuptools import setup, find_packages

setup(
    name='json_tools',
    version='0.3',
    packages=[''],
    url='https://github.com/georgegvg/json_tools',
    license='',
    author='georgegoldberg',
    author_email='g.kalashnikoff@gmail.com',
    description='manage json and yaml',
    install_requires=['pyyaml'],
    python_requires='>=3.7',
    entry_points={
        'console_scripts': ['json_tools = json_tools.json_tools:main']
    }
)
