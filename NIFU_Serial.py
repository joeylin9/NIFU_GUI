import serial
import pandas as pd
import time

class EldexPump:
    def __init__(self):
        self.commands = {
            'run': 'RU',
            'stop': 'ST',
            'set flow rate': 'SFxx.xxx',
            'read flow rate': ' RF',
            'read ID': 'ID',
            'read pressure': 'RP',
            'set high pressure limit': 'SHxxxx',
            'set low pressure limit': 'SLxxxx',
            'read high pressure limit': 'RH',
            'read low pressure limit': 'RL',
            'set compressibility compensation': 'SCxx',
            'read compressibility compensation': 'RC',
            'set refill rate factor': 'SRx',
            'read refill rate factor': 'RR',
            'disables keypad': 'KD',
            'enables keypad': 'KE',
            'set piston diameter': 'SDx',
            'read piston diameter': 'RD',
            'set stroke': 'SSx',
            'read stroke': 'RS',
            'set material': 'SMx',
            'read material': 'RM',
            'read fault status': 'RX',
            'set LED to red and stops pump': 'SX',
            'read attributes': 'RI',
            'reset command buffer': 'Z'
        }

    def eldex_pump_command(self, port_number, command, value=''):
        p = f'COM{port_number}'
        ser = serial.Serial(port=p, baudrate=9600, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE,
                            bytesize=serial.EIGHTBITS, timeout=1)
        print("connected to: " + ser.portstr)

        # Format the command string and encode it to bytes
        command_str = f'{command}{value}\r\n'
        ser.write(command_str.encode('ascii'))

        # Read and print the response from the pump
        response = ser.readline().decode('ascii')
        print(p + ':', response)

class UI22_Pump():
    def __init__(self):
        self.commands = {
            'stop pump':'G1,0',
            'start pump': 'G1,1',
            'stop priming': 'G5,0',
            'start priming': 'G5,1',
            'fixed control mode': 'S2,1',
            'self-learning mode': 'S2,2',
            'flow rate': 'S3,aaaaa', #in units of μL/min
            'pressure limit': 'S6,aaa,bbb', #in 0.1MPa units, no decimals
            'errors not transmitted': 'SE,0',
            'errors transmitted': 'SE,1',
            'request pump info': 'Q1',
            'request pump stats': 'Q2',
            'request for setting values': 'Q3'
        }

    def UI22_pump_command(self, port_number, command, address='01', value=''):
        p = f'COM{port_number}'
        ser = serial.Serial(port=p, baudrate=9600, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE,
                            bytesize=serial.EIGHTBITS, timeout=1)
        print("connected to: " + ser.portstr)

        # Format the command string and encode it to bytes
        command_str = f';{address},{command},{value}\r\n'
        ser.write(command_str.encode('ascii'))

        # Read and print the response from the pump
        response = ser.readline().decode('ascii')
        print(p + ':', response)

class Balance:
    def balance_read_data(self, port_number, save):
        p = f'COM{port_number}'
        ser = serial.Serial(port=p, baudrate=9600, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE,
                            bytesize=serial.EIGHTBITS, timeout=0.2)
        print("connected to: " + ser.portstr)

        times = []
        balances = []
        t = 0.0
        balance_update_interval = 0.001
        max_time = 1.0

        while t <= max_time:
            s = ser.read(1000)
            s_decoded = s.decode('ascii').strip()  # Decode the bytes to string and strip any whitespace

            times.append(t)
            balances.append(s_decoded)

            time.sleep(balance_update_interval)
            t += balance_update_interval

        data = {'Time': times, 'Balance': balances}
        df = pd.DataFrame(data)
        print(df)

        if save:  # If the save checkbox is marked, save the data to a CSV file
            df.to_csv('test.csv', index=False)
            print("Data saved")
