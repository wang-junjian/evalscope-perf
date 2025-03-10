from setuptools import setup, find_packages

import os

# 获取当前文件所在目录
this_directory = os.path.abspath(os.path.dirname(__file__))

# 读取 README.md 内容
with open(os.path.join(this_directory, "README.md"), encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name='evalscope-perf',
    version='1.0.0',
    author = 'Junjian Wang',
    author_email = 'vwarship@163.com',
    description = '大模型性能压测可视化',
    long_description = long_description,
    long_description_content_type = 'text/markdown',
    url = 'http://www.wangjunjian.com',
    packages=find_packages(),
    install_requires=[
        # 在这里添加你的依赖包
        'typer',
        'pandas',
        'matplotlib',
        'evalscope==0.5.5',
    ],
    package_data={
        'evalscope_perf': ['../fonts/*.ttc'],  # 包含字体文件
    },
    include_package_data=True,  # 确保包含非代码文件
    entry_points={
        'console_scripts': [
            # 在这里添加你的命令行工具，例如：
            'evalscope-perf=evalscope_perf.main:app',
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)