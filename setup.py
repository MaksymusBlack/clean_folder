from setuptools import setup, find_namespace_packages

setup(
      name='Clean folder',
      version='0.0.1',
      description='Code creates separate folders and sorts files in those folders',
      url='http://github.com/dummy_user/useful',
      author='MaksymusBlack',
      author_email='kuleshovmaksym42@gmail.com',
      license='MIT',
      packages=find_namespace_packages(),
      entry_points={'console_scripts': ['clean-folder = clean_folder.clean:run']}
      )
      