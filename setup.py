from setuptools import setup, find_packages


with open("VERSION", "r") as version_file:
	version = version_file.read().strip()

with open("README.md", "r") as f:
	setup(
		name="openpower",
		version=version,
		author="tris10au",
		description="Python library for monitoring and controlling solar power systems, including batteries and inverters",
		long_description_content_type="text/markdown",
		long_description=f.read(),
		url="https://github.com/tris10au/openpower",
		packages=find_packages(),
		classifiers=[
			"Programming Language :: Python :: 3",
			"License :: OSI Approved :: MIT License",
			"Operating System :: OS Independent",
		],
		install_requires=["requests"]
	)
