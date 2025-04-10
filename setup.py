from setuptools import setup, find_packages

setup(
    name="sandbox-interpreter",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "psutil>=5.9.0",
        "flask>=2.0.0",
        "docker>=5.0.0",
        "pyyaml>=6.0",
        "open-interpreter>=0.1.5"
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "black>=22.0.0",
            "flake8>=5.0.0"
        ]
    },
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "sandbox-web=sandbox.web.app:run_server",
        ]
    }
)