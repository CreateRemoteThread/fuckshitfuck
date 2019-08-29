#!/usr/bin/env python3

from smartcard.CardType import AnyCardType
from smartcard.CardRequest import CardRequest
from smartcard.CardConnectionObserver import ConsoleCardConnectionObserver
from smartcard.Exceptions import CardRequestTimeoutException

print("Insert a card..")
cardrequest = CardRequest(timeout=5,cardType=AnyCardType())
cardservice = cardrequest.waitforcard()
observer = ConsoleCardConnectionObserver()
cardservice.connection.addObserver(observer)
cardservice.connection.connect()
print("ATR... : %s" % cardservice.connection.getATR())
cardservice.connection.transmit([0x00,0xA4,0x08,0x04,0x02,0x2F,0x00])
cardservice.connection.transmit([0x00,0xC0,0x00,0x00,0x1C])
cardservice.connection.transmit([0x00,0xB2,0x01,0x04,0x26])
cardservice.connection.transmit([0x00,0xA4,0x04,0x04,0x10,0xA0,0x00,0x00,0x87,0x10,0x02,0xFF,0x86,0x11,0x04,0x89,0xFF,0xFF,0xFF,0xff])
