from setuptools import setup

setup(
    name="zarkdown",
    version="1.0.0",
    author="yangzizhoudiwuxuande",
    description="Zarkdown - 键盘友好型纯文本标记语言",
    py_modules=["core"],
    entry_points={
        "console_scripts": [
            "zarkdown = core:main",
        ],
    },
    python_requires=">=3.6",
)
