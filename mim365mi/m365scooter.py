#
#     Mi365 Scooter Library
#     MiAuth - Authenticate and interact with Xiaomi devices over BLE
#     Copyright (C) 2021  Daljeet Nandha + modified by @catSIXe
#
#     This program is free software: you can redistribute it and/or modify
#     it under the terms of the GNU Affero General Public License as
#     published by the Free Software Foundation, either version 3 of the
#     License, or (at your option) any later version.
#
#     This program is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU Affero General Public License for more details.
#
#     You should have received a copy of the GNU Affero General Public License
#     along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
import time

from bluepy import btle

from miauth.mi.micommand import MiCommand
from miauth.mi.micrypto import MiCrypto
from miauth.uuid import UUID
from miauth.mi.miclient import MiClient

class M365Scooter(MiClient):
    def __init__(self, p, mac, debug=False):
        super().__init__(p, mac, debug)
        self.cachedData = {}
        self.dataUpdated = None

    def handleData(self, callback):
        self.dataUpdated = callback

    def main_handler(self, data):
        if len(data) == 0:
            return
        #if self.debug:
        #print("<-", data.hex())
        frm = data[0] + 0x100 * data[1]
        
        if self.get_state() in [MiClient.State.RECV_INFO,
                                MiClient.State.RECV_KEY]:
            self.receive_handler(frm, data)
        elif self.get_state() in [MiClient.State.SEND_KEY,
                                  MiClient.State.SEND_DID]:
            self.send_handler(frm, data)
        elif self.get_state() == MiClient.State.CONFIRM:
            self.confirm_handler(frm)
        elif self.get_state() == MiClient.State.COMM:
            # TODO: check if correct number of frames received
            self.received_data += data
            #print('attaching data', len(self.received_data), len(data), data.hex())
            if len(data) != 0:
                try:
                    recvData = MiCrypto.decrypt_uart(
                        self.keys['dev_key'],
                        self.keys['dev_iv'],
                        self.received_data
                    ) #[3:-4]
                    self.received_data = b''
                    if  recvData[0:3].hex() in self.cachedData.keys():
                        if recvData[3:-4].hex() != self.cachedData[ recvData[0:3].hex() ].hex():
                            self.dataUpdated(recvData[0:3].hex(), recvData[3:-4])
                    else:
                        self.dataUpdated(recvData[0:3].hex(), recvData[3:-4])
                    self.cachedData[ recvData[0:3].hex() ] = recvData[3:-4]
                except:
                    pass

    def comm_simplex(self, cmd):
        if self.get_state() != MiClient.State.COMM:
            raise Exception("Not in COMM state. Retry maybe.")

        if type(cmd) not in [bytearray, bytes]:
            cmd = bytes.fromhex(cmd)

        if cmd[:2] != b'\x55\xAA':
            if cmd[:2] == b'\x5a\xa5':
                raise Exception("Command must start with 55 AA (M365 PROTOCOl)!\
                                You sent a Nb command, try Nb pairing instead.")
            else:
                raise Exception("Command must start with 55 AA (M365 PROTOCOl)!")

        self.received_data = b''
        if not self.keys:
            self.bt_write(self.ch_tx, cmd)

            while self.p.waitForNotifications(3.0):
                continue

            if not self.received_data:
                raise Exception("No answer received. Try login first.")

            return self.received_data

        res = MiCrypto.encrypt_uart(self.keys['app_key'], self.keys['app_iv'], cmd, it=self.uart_it)
        self.bt_write(self.ch_tx, res)
        self.uart_it += 1


#
