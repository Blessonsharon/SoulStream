import os
import subprocess
import sys

def check_requirements():
    requirements = ['tensorflow', 'numpy', 'keras']
    for package in requirements:
        try:
            __import__(package)
            print(f'Package {package} is already installed.')
        except ImportError:
            print(f'Package {package} not found. Installing...')
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])
            print(f'Package {package} installed successfully.')

def download_pretrained_models():
    urls = ['https://example.com/model1.h5', 'https://example.com/model2.h5']
    for url in urls:
        filename = url.split('/')[-1]
        print(f'Downloading {filename}...')
        subprocess.check_call(['curl', '-O', url])
        print(f'{filename} downloaded successfully.')

def create_directories():
    directories = ['models', 'data']
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f'Directory {directory} created.')
        else:
            print(f'Directory {directory} already exists.')

def test_installations():
    try:
        import tensorflow
        import numpy
        import keras
        print('All installations are successful.')
    except ImportError as e:
        print(f'Error in installation: {e}')

if __name__ == '__main__':
    print('Starting setup...')
    check_requirements()
    download_pretrained_models()
    create_directories()
    test_installations()
    print('Setup complete! Ready to go. Please follow the next steps...')
