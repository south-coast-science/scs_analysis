"""
Created on 4 Sep 2020

@author: Jade Page (jade.page@southcoastscience.com)

https://packaging.python.org/tutorials/packaging-projects/
https://packaging.python.org/guides/single-sourcing-package-version/

https://stackoverflow.com/questions/65841378/include-json-file-in-python-package-pypi
https://stackoverflow.com/questions/45147837/including-data-files-with-setup-py
"""

import codecs
import os
import setuptools


# --------------------------------------------------------------------------------------------------------------------

def read(rel_path):
    here = os.path.abspath(os.path.dirname(__file__))
    with codecs.open(os.path.join(here, rel_path)) as fp:
        return fp.read()


def get_version(rel_path):
    for line in read(rel_path).splitlines():
        if line.startswith('__version__'):
            return line.split("'")[1]
    else:
        raise RuntimeError("Unable to find version string.")


# --------------------------------------------------------------------------------------------------------------------

with open('README.md') as fh:
    long_description = fh.read()

with open('requirements.txt') as req_txt:
    required = [line for line in req_txt.read().splitlines() if line]


setuptools.setup(
    name="scs-analysis",
    version=get_version("src/scs_analysis/__init__.py"),
    author="South Coast Science",
    author_email="contact@southcoastscience.com",
    description="Information management and analysis utilities for South Coast Science data consumers",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/south-coast-science/scs_analysis",
    package_dir={'': 'src'},
    packages=setuptools.find_packages('src'),
    package_data={'scs_analysis': ['**/*.csv', '**/*.json', '**/*.me']},
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows :: Windows 10",
        "Operating System :: POSIX",
    ],
    scripts=[
        'src/scs_analysis/alert.py',
        'src/scs_analysis/alert_status.py',
        'src/scs_analysis/aws_byline.py',
        'src/scs_analysis/aws_client_auth.py',
        'src/scs_analysis/aws_mqtt_client.py',
        'src/scs_analysis/aws_topic_history.py',
        'src/scs_analysis/aws_topic_publisher.py',
        'src/scs_analysis/aws_upload_interval.py',
        'src/scs_analysis/baseline.py',
        'src/scs_analysis/baseline_conf.py',
        'src/scs_analysis/client_traffic.py',
        'src/scs_analysis/cognito_devices.py',
        'src/scs_analysis/cognito_email.py',
        'src/scs_analysis/cognito_user_credentials.py',
        'src/scs_analysis/cognito_user_identity.py',
        'src/scs_analysis/cognito_users.py',
        'src/scs_analysis/configuration_csv.py',
        'src/scs_analysis/configuration_monitor.py',
        'src/scs_analysis/configuration_monitor_check.py',
        'src/scs_analysis/configuration_report.py',
        'src/scs_analysis/csv_collation_summary.py',
        'src/scs_analysis/csv_collator.py',
        'src/scs_analysis/csv_join.py',
        'src/scs_analysis/csv_reader.py',
        'src/scs_analysis/csv_segmentor.py',
        'src/scs_analysis/csv_writer.py',
        'src/scs_analysis/device_controller.py',
        'src/scs_analysis/device_monitor.py',
        'src/scs_analysis/device_monitor_status.py',
        'src/scs_analysis/histo_chart.py',
        'src/scs_analysis/localised_datetime.py',
        'src/scs_analysis/monitor_auth.py',
        'src/scs_analysis/multi_chart.py',
        'src/scs_analysis/node.py',
        'src/scs_analysis/organisation_devices.py',
        'src/scs_analysis/organisation_path_roots.py',
        'src/scs_analysis/organisation_user_paths.py',
        'src/scs_analysis/organisation_users.py',
        'src/scs_analysis/organisations.py',
        'src/scs_analysis/sample_aggregate.py',
        'src/scs_analysis/sample_average.py',
        'src/scs_analysis/sample_collator.py',
        'src/scs_analysis/sample_distance.py',
        'src/scs_analysis/sample_duplicates.py',
        'src/scs_analysis/sample_error.py',
        'src/scs_analysis/sample_gas_concentration.py',
        'src/scs_analysis/sample_gas_density.py',
        'src/scs_analysis/sample_interval.py',
        'src/scs_analysis/sample_iso_8601.py',
        'src/scs_analysis/sample_localize.py',
        'src/scs_analysis/sample_low_pass.py',
        'src/scs_analysis/sample_max.py',
        'src/scs_analysis/sample_median.py',
        'src/scs_analysis/sample_midpoint.py',
        'src/scs_analysis/sample_min.py',
        'src/scs_analysis/sample_noise.py',
        'src/scs_analysis/sample_nullify.py',
        'src/scs_analysis/sample_paths.py',
        'src/scs_analysis/sample_regression.py',
        'src/scs_analysis/sample_slope.py',
        'src/scs_analysis/sample_sort.py',
        'src/scs_analysis/sample_stats.py',
        'src/scs_analysis/sample_subset.py',
        'src/scs_analysis/sample_time_shift.py',
        'src/scs_analysis/single_chart.py',
        'src/scs_analysis/socket_receiver.py',
        'src/scs_analysis/timer.py',
        'src/scs_analysis/uds_receiver.py'
    ],
    install_requires=required,
    platforms=['any'],
    python_requires='>3.6',
    extras_require={
        'dev': [
            'pypandoc'
        ]
    }
)
