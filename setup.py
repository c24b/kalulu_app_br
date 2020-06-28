from setuptools import setup, find_packages

setup(name='kalulu_app', version='1.0', packages=find_packages(exclude=(["tests","logs", "conf", "admin", "db/files/raw", "db/files/clean", "db/files/archived"])))
