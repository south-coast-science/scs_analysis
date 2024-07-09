"""
Created on 17 Aug 2022

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

source repo: scs_analysis
"""

from subprocess import Popen, PIPE

from scs_core.data.json import JSONify


# --------------------------------------------------------------------------------------------------------------------

class ConfigurationCSVGenerator(object):
    """
    classdocs
    """

    COMMON_NODES = ['tag', 'rec', 'rec.report', 'rec.update', 'ver']

    # ----------------------------------------------------------------------------------------------------------------

    def __init__(self, verbose):
        self.__csv_opts = '-vsq' if verbose else '-sq'
        self.__node_opts = '-v' if verbose else ''


    # ----------------------------------------------------------------------------------------------------------------

    def generate(self, selected_configs, selected_nodes, file_path, **kwargs):
        jstr = '\n'.join([JSONify.dumps(config, **kwargs) for config in selected_configs])
        node_args = self.COMMON_NODES + ['val.' + selected_node for selected_node in selected_nodes]

        if selected_nodes:
            p = Popen(['node.py', self.__node_opts] + node_args, stdin=PIPE, stdout=PIPE)
            csv_data, _ = p.communicate(input=jstr.encode())
        else:
            csv_data = jstr.encode()

        p = Popen(['csv_writer.py', self.__csv_opts, file_path], stdin=PIPE)
        p.communicate(input=csv_data)
