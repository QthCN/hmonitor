from setuptools import setup, find_packages


setup(
    name="hmonitor",
    version="0.10",
    description="A monitor control console",
    author="Qin TianHuan",
    author_email="tianhuan@bingotree.cn",
    url="",
    packages=find_packages(),

    provides=["hmonitor.utils.executor",
              ],
    entry_points={
        "hmonitor.utils.executor": [
            'ssh = hmonitor.utils.executor.ssh:SSHExecutor',
        ],
    },
)
