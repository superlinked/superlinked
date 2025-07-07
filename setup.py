from setuptools import setup, find_packages
import os

# Find all packages in framework/src
framework_packages = find_packages(where="framework/src")

# Map framework packages to superlinked namespace
packages = ["superlinked"]  # Add root package
package_dir = {"superlinked": "framework/src"}  # Map root to framework/src

for pkg in framework_packages:
    if pkg == "framework":
        packages.append("superlinked.framework")
        package_dir["superlinked.framework"] = "framework/src/framework"
    elif pkg.startswith("framework."):
        # Map framework.xxx to superlinked.framework.xxx
        new_pkg = "superlinked." + pkg
        packages.append(new_pkg)
        package_dir[new_pkg] = f"framework/src/{pkg.replace('.', '/')}"
    elif pkg == "evaluation":
        packages.append("superlinked.evaluation")
        package_dir["superlinked.evaluation"] = "framework/src/evaluation"
    elif pkg.startswith("evaluation."):
        # Map evaluation.xxx to superlinked.evaluation.xxx
        new_pkg = "superlinked." + pkg
        packages.append(new_pkg)
        package_dir[new_pkg] = f"framework/src/{pkg.replace('.', '/')}"

setup(
    name="superlinked",
    version="0.1.0",
    description="Superlinked framework for vector search",
    packages=packages,
    package_dir=package_dir,
    include_package_data=True,
    python_requires=">=3.8",
    install_requires=[
        # Core ML and data processing dependencies
        "beartype",
        "Pillow",
        "structlog",
        "torch",
        "attrs",
        "numpy",
        "pandas",
        "pydantic",
        "pydantic-settings",
        # Vector databases and storage
        "qdrant-client",
        "redis",
        "pymongo",
        "tenacity",
        # Visualization and development tools
        "graphviz",
        "altair",
        # Web framework dependencies
        "asgi-correlation-id",
        # AI/ML model dependencies
        "instructor",
        "nest-asyncio",
        "huggingface-hub",
        "transformers",
        "sentence-transformers",
        "torchvision",
        "open-clip-torch",
        "cachetools",
        # Utility libraries
        "furl",
        "modal",
        # OpenTelemetry dependencies
        "opentelemetry-api",
        "opentelemetry-sdk",
    ],
    zip_safe=False,
)
