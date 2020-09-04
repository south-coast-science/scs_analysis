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
    version="0.0.4",
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
        "Programming Language :: Python :: 3.7",
        "License :: OSI Approved :: MIT License",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows :: Windows 10",
        "Operating System :: POSIX",
    ],
    scripts=[
        'src/scs_analysis/aws_api_auth.py',
        'src/scs_analysis/aws_mqtt_client.py',
        'src/scs_analysis/aws_mqtt_control.py',
        'src/scs_analysis/aws_topic_history.py',
        'src/scs_analysis/aws_topic_publisher.py',
        'src/scs_analysis/csv_reader.py',
        'src/scs_analysis/csv_writer.py',
        'src/scs_analysis/histo_chart.py',
        'src/scs_analysis/localised_datetime.py',
        'src/scs_analysis/multi_chart.py',
        'src/scs_analysis/node.py',
        'src/scs_analysis/osio_api_auth.py',
        'src/scs_analysis/osio_mqtt_client.py',
        'src/scs_analysis/osio_mqtt_control.py',
        'src/scs_analysis/osio_topic_history.py',
        'src/scs_analysis/osio_topic_publisher.py',
        'src/scs_analysis/sample_average.py',
        'src/scs_analysis/sample_error.py',
        'src/scs_analysis/sample_interval.py',
        'src/scs_analysis/sample_max.py',
        'src/scs_analysis/sample_midpoint.py',
        'src/scs_analysis/sample_min.py',
        'src/scs_analysis/sample_regression.py',
        'src/scs_analysis/single_chart.py',
        'src/scs_analysis/socket_receiver.py',
        'src/scs_analysis/uds_receiver.py',
    ],
    install_requires=required,
    platforms=['any'],
    python_requires='>3.5',
    extras_require={
        'dev': [
            'pypandoc'
        ]
    }
)
