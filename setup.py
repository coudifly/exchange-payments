from setuptools import setup, find_packages


__VERSION__ = '0.1'

REQUIREMENTS = [
	'python-bitcoinlib',
	'simple-crypt',
]

setup(
	name='exchange-payments',
	version=__VERSION__,
	description='Exchange payments package',
	author='Juliano Gouveia',
	author_email='juliano@neosacode.com',
	keywords='exchange, payments, neosacode, coins',
	install_requires=REQUIREMENTS,
	packages=find_packages(exclude=[]),
	python_requires='>=3.5'
)