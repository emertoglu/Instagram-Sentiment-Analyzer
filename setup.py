from setuptools import setup, find_packages

setup(
    name='Instagram Sentiment Analyzer',
    version='1.0',
    packages=find_packages(),
    install_requires=["pandas","mpld3","matplotlib","textblob","TextBlob","python_instagram"],
    url='',
    license='',
    author='Caleb Skinner',
    author_email='',
    description='Gets the most recent post for a Instagram hashtag and analyzes the sentiment of each post'
)
