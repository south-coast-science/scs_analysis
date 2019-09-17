"""
Created on 11 Jan 2018

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

source repo: scs_analysis
"""

import json

from scs_core.control.control_receipt import ControlReceipt


# --------------------------------------------------------------------------------------------------------------------

class AWSMQTTControlHandler(object):
    """
    classdocs
    """

    # ----------------------------------------------------------------------------------------------------------------

    def __init__(self):
        """
        Constructor
        """
        self.__outgoing_pub = None
        self.__receipt = None


    # ----------------------------------------------------------------------------------------------------------------

    def set(self, outgoing_pub):
        self.__outgoing_pub = outgoing_pub
        self.__receipt = None


    def handle(self, _client, _userdata, message):
        payload = json.loads(message.payload.decode())

        try:
            receipt = ControlReceipt.construct_from_jdict(payload)
        except TypeError:
            return

        if receipt.tag == self.__outgoing_pub.payload.attn and receipt.omd == self.__outgoing_pub.payload.digest:
            self.__receipt = receipt


    # ----------------------------------------------------------------------------------------------------------------

    @property
    def receipt(self):
        return self.__receipt


    # ----------------------------------------------------------------------------------------------------------------

    def __str__(self, *args, **kwargs):
        return "AWSMQTTControlHandler:{outgoing_pub:%s, receipt:%s}" %  (self.__outgoing_pub, self.receipt)
