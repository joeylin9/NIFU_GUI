import serial
from pymodbus.client import ModbusTcpClient

class Pump:
    def pump_connect(self, port_number):
        p = f'COM{port_number}'
        ser = serial.Serial(port=p, baudrate=9600, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE,
                            bytesize=serial.EIGHTBITS, timeout=1)
        print("connected to: " + ser.portstr)
        return ser

    def pump_disconnect(self, ser):
        ser.close()
        print("disconnected from: " + ser.portstr)

    # --- ELDEX --- #
    # 'run': 'RU',
    # 'stop': 'ST',
    # 'set flow rate': 'SFxx.xxx',
    # 'read flow rate': ' RF',
    # 'read ID': 'ID',
    # 'read pressure': 'RP',
    # 'set high pressure limit': 'SHxxxx',
    # 'set low pressure limit': 'SLxxxx',
    # 'read high pressure limit': 'RH',
    # 'read low pressure limit': 'RL',
    # 'set compressibility compensation': 'SCxx',
    # 'read compressibility compensation': 'RC',
    # 'set refill rate factor': 'SRx',
    # 'read refill rate factor': 'RR',
    # 'disables keypad': 'KD',
    # 'enables keypad': 'KE',
    # 'set piston diameter': 'SDx',
    # 'read piston diameter': 'RD',
    # 'set stroke': 'SSx',
    # 'read stroke': 'RS',
    # 'set material': 'SMx',
    # 'read material': 'RM',
    # 'read fault status': 'RX',
    # 'set LED to red and stops pump': 'SX',
    # 'read attributes': 'RI',
    # 'reset command buffer': 'Z'

    def eldex_pump_command(self, ser, command, value=''):
        # Format the command string and encode it to bytes
        command_str = f'{command}{value}\r\n'
        ser.write(command_str.encode('ascii'))

        # Read and print the response from the pump
        response = ser.readline().decode('ascii')
        print(f'{ser.portstr}: {response}')

    # --- UI-22 -- #
    # 'stop pump':'G1,0',
    # 'start pump': 'G1,1',
    # 'stop priming': 'G5,0',
    # 'start priming': 'G5,1',
    # 'fixed control mode': 'S2,1',
    # 'self-learning mode': 'S2,2',
    # 'flow rate': 'S3,aaaaa', #in units of μL/min
    # 'pressure limit': 'S6,aaa,bbb', #in 0.1MPa units, no decimals
    # 'errors not transmitted': 'SE,0',
    # 'errors transmitted': 'SE,1',
    # 'request pump info': 'Q1',
    # 'request pump stats': 'Q2',
    # 'request for setting values': 'Q3'

    def UI22_pump_command(self, ser, command, address='01', value=''):
        # Format the command string and encode it to bytes
        command_str = f';{address},{command},{value}\r\n'
        ser.write(command_str.encode('ascii'))

        # Read and print the response from the pump
        response = ser.readline().decode('ascii')
        print(f'{ser.portstr}: {response}')

class Balance:
    def balance_connect(self, port_number):
        p = f'COM{port_number}'
        ser = serial.Serial(port=p, baudrate=9600, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE,
                            bytesize=serial.EIGHTBITS, timeout=0.2)
        print("connected to: " + ser.portstr)
        return ser

    def balance_disconnect(self, ser):
        ser.close()
        print("disconnected from: " + ser.portstr)

class PLC:
    def __init__(self) -> None:
        self.client = ModbusTcpClient(host = 'IP', port = 'port') #change to real values
        self.client.connect()

    def read(self, address, number):
        regs = self.client.read_holding_registers(address, number)
        if regs:
            print(regs)
            return regs
        else:
            print('Read Error')

        #to get value, can do value = regs[0]
