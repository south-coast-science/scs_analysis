"""
Created on 4 Sep 2020

@author: Jade Page (jade.page@southcoastscience.com)
https://packaging.python.org/tutorials/packaging-projects/
"""

import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

with open('requirements.txt') as req_txt:
    required = [line for line in req_txt.read().splitlines() if line]

setuptools.setup(
    name="SCS_ANALYSIS",
    version="0.0.3",
    author="South Coast Science",
    author_email="contact@southcoastscience.com",
    description="Information management and analysis utilities for South Coast Science data consumers.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/south-coast-science/scs_analysis",
    package_dir={'': 'src'},
    packages=setuptools.find_packages('src'),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "License :: OSI Approved :: MIT License",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows :: Windows 10",
        "Operating System :: POSIX",
    ],
    entry_points={
        'console_scripts': [
            'aws_api_auth = scs_analysis.aws_api_auth:main',
            'aws_mqtt_client = scs_analysis.aws_mqtt_client:main',
            'aws_mqtt_control = scs_analysis.aws_mqtt_control:main',
            'aws_topic_history = scs_analysis.aws_topic_history:main',
            'aws_topic_publisher = scs_analysis.aws_topic_publisher:main',
            'csv_reader = scs_analysis.csv_reader:main',
            'csv_writer = scs_analysis.csv_writer:main',
            'histo_chart = scs_analysis.histo_chart:main',
            'localised_datetime = scs_analysis.localised_datetime:main',
            'multi_chart = scs_analysis.multi_chart:main',
            'node = scs_analysis.node:main',
            'osio_api_auth = scs_analysis.osio_api_auth:main',
            'osio_mqtt_client = scs_analysis.osio_mqtt_client:main',
            'osio_mqtt_control = scs_analysis.osio_mqtt_control:main',
            'osio_topic_history = scs_analysis.osio_topic_history:main',
            'osio_topic_publisher = scs_analysis.osio_topic_publisher:main',
            'sample_average = scs_analysis.sample_average:main',
            'sample_conv = scs_analysis.sample_conv:main',
            'sample_error = scs_analysis.sample_error:main',
            'sample_interval = scs_analysis.sample_interval:main',
            'sample_max = scs_analysis.sample_max:main',
            'sample_midpoint = scs_analysis.sample_midpoint:main',
            'sample_min = scs_analysis.sample_min:main',
            'sample_regression = scs_analysis.sample_regression:main',
            'single_chart = scs_analysis.single_chart:main',
            'socket_receiver = scs_analysis.socket_receiver:main',
            'uds_receiver = scs_analysis.uds_receiver:main',
        ],
    },
    install_requires=required,
    platforms=['any'],
    python_requires='>3.5',
    extras_require={
        'dev': [
            'pypandoc'
        ]
    }
)
