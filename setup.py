from setuptools import setup, find_packages

setup(
    name='json_tools',
    version='0.5',
    packages=['json_tools'],
    url='https://github.com/georgegvg/json_tools',
    license='',
    author='georgegoldberg',
    author_email='g.kalashnikoff@gmail.com',
    description='manage json and yaml',
    install_requires=['pyyaml'],
    python_requires='>=3.7',
    entry_points={
        'console_scripts': ['search_json_yaml = json_tools:main',
                            'check_json_validity = json_tools.check_json_validity:main']
    }
)
