"""
Created on 11 Jan 2018

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

source repo: scs_analysis
"""

from scs_core.control.control_receipt import ControlReceipt


# --------------------------------------------------------------------------------------------------------------------

class OSIOMQTTControlHandler(object):
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


    def handle(self, pub):
        try:
            receipt = ControlReceipt.construct_from_jdict(pub.payload)
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
        return "OSIOMQTTControlHandler:{outgoing_pub:%s, receipt:%s}" %  (self.__outgoing_pub, self.receipt)

