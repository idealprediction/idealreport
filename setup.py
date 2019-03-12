from setuptools import setup
setup(
  name = 'idealreport',
  packages = ['idealreport'],
  version = '0.14',
  description = 'Ideal Prediction reporting framework',
  author = 'Ideal Prediction',
  author_email = 'info@idealprediction.com',
  url = 'https://github.com/idealprediction/idealreport',
  download_url = 'https://github.com/idealprediction/idealreport/tarball/0.14',
  keywords = ['idealprediction', 'report'],
  classifiers = [],
  package_data = {'idealreport': ['htmlLibs/*.*', 'template.html']},
  include_package_data = True,
  setup_requires = ['sphinx'],
  install_requires = ['htmltag', 'pandas>=0.23.4', 'ujson'],
)
