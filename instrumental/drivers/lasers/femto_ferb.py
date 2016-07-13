# -*- coding: utf-8  -*-
# Copyright 2016 Nate Bogdanowicz and Christopher Rogers
"""
Driver for Tobtica FemtoFiber Lasers.  The femtofiber drivers, which among
other things make the usb connection appear as a serial port, must be
installed (available from http://www.toptica.com/products/ultrafast_fiber_lasers/femtofiber_smart/femtosecond_erbium_fiber_laser_1560_nm_femtoferb)
"""

import visa
from . import Laser
from ...errors import InstrumentTypeError

TRUE = '#t'
FALSE = '#f'
bool_dict = {'#t': True, '#f': False}

def _instrument(params):
    """ params must include 'femto_ferb_port'. """
    d = {}
    if 'femto_ferb_port' in params:
        d['port'] = params['femto_ferb_port']
    if not d:
        raise InstrumentTypeError()

    return FemtoFiber(**d)


class FemtoFiber(Laser):
    """
    A femtoFiber laser. Currently, lasers can only be accessed by their
    serial port address.
    """
    def __init__(self, port):
        self._inst = visa.instrument(port)
        self.set_control(True)

    def is_control_on(self):
        """ Returns the status of the hardware input control.

        Hardware input control must be on in order for the laser to be
        controlled by usb connection.

        Returns
        -------
        message : bool
            If True, hardware input conrol is on.
        """
        message = self._ask('(param-ref hw-input-dis)')
        message = bool_dict[message]
        return message

    def set_control(self, control):
        """ Sets the status of the hardware input control.

        Hardware input control must be on in order for the laser to be
        controlled by usb connection.

        Parameters
        ----------
        control : bool
            If True, hardware input conrol is turned on.

        Returns
        -------
        error : int or str
            Zero is returned if the hardware input control status was set
            correctly.  Otherwise, the error string returned by the laser
            is returned.
        """
        for key, item in bool_dict.iteritems():
            if item == control:
                control = key
        error = self._ask('(param-set! hw-input-dis {})'.format(control),
                          return_error=True)
        return error

    def is_on(self):
        """
        Returns True if the laser is on, and returns False is the laser is off.
        """
        message = self._ask('(param-ref laser:en)')
        message = bool_dict[message]
        return message

    def _set_emission(self, control):
        """ Sets the emission status of the laser.

        Parameters
        ----------
        control : bool
            If True, the laser output is turned on.  If False, the laser output
            is turned off.

        Returns
        -------
        error : int or str
            Zero is returned if the emission status was set
            correctly.  Otherwise, the error string returned by the laser
            is returned.
        """
        for key, item in bool_dict.iteritems():
            if item == control:
                control = key
        error = self._ask('(param-set! laser:en {})'.format(control),
                          return_error=True)
        return error

    def turn_on(self):
        """ Turns the laser on.

        Note that hardware control must be enabled in order for this method
        to execute properly.

        Returns
        -------
        error : int or str
            Zero is returned if the laser was successfuly turned on.
            Otherwise, the error string returned by the laser is returned.
        """
        return self._set_emission(True)

    def turn_off(self):
        """  Turns the laser off.

        Note that hardware control must be enabled in order for this method
        to execute properly.

        Returns
        -------
        error : int or str
            Zero is returned if the laser was correctly turned off.
            Otherwise, the error string returned by the laser is returned.
        """
        return self._set_emission(False)

    def _ask(self, message, return_error=False):
        self._inst.ask(message)
        message = self._inst.read(termination='\n')
        if return_error:
            error = message
            if error == '0':
                error = int(error)
            return error
        return message

    def close(self):
        """
        Closes the connection to the laser.
        """
        self._inst.close()