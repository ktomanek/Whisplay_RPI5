from setuptools import setup, find_packages

setup(
    name="whisplay",
    version="1.0.0",
    description="WhisPlay HAT driver for Raspberry Pi 5",
    author="PiSugar (modified for Pi 5)",
    py_modules=["WhisPlay"],
    package_dir={"": "Driver"},
    install_requires=[
        "spidev",
        "gpiozero",
        "Pillow",
    ],
    python_requires=">=3.9",
)
