from setuptools import setup, find_packages

setup(
    name='getvillagename',
    version='1.0',
    packages=find_packages(),
    package_data={
        'your_module': ['data/*.txt'],
    },
    include_package_data=True,
    # 其他配置项
)
