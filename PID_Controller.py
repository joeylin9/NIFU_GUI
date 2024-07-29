import time
from typing import Optional
from scipy.stats import linregress
import serial
from datetime import datetime
import collections
import threading

class PID:
    def __init__(self, set_point, kp: float = 1.0, ki: float = 0.0, kd: float = 0.0, integral_error_limit: Optional[float] = None):
        """
        set_point = set point: the desired value to output // constant, based on GUI
        pv = process variable: the current measured output // changes every recall, based on phsyical system
        kp = proportional gain // constant
        ki = integral gain // constant
        t = time // changes

        last_error // changes every recall, initially at 0
        reset // changes every recall, intially at 0
        """
        self._set_point = set_point
        self._kp = kp
        self._ki = ki
        self._kd = kd
        self._integral_error_limit = integral_error_limit

        self._last_error = 0.0
        self._integral_error = 0.0
        self._last_time = time.time()

    def __call__(self, process_variable):
        """
        inputs: process_variable, which is the flow rate that is currently being measured
        call this "function" to output a flow rate that should be closer to the set point
        """
        end_time = time.time()
        t = end_time - self._last_time

        if process_variable == 0:
            self._error = 0
        else:
            self._error = self._set_point - process_variable

        #proportional
        p = self._kp * self._error

        #integral
        self._integral_error += self._error * t

        if self._integral_error_limit and abs(self._integral_error) > self._integral_error_limit:
            self._integral_error = self._integral_error_limit

        i = self._ki * self._integral_error

        #derivative
        d = self._kd * (self._error - self._last_error) / t if t > 0 else 0
        self._last_error = self._error
        self._last_time = time.time()

        output = self._set_point + p + i + d
        return output

    def reset(self):
        self._integral_error = 0

max_data_points = int(input("Enter max length of data arrays: "))
class Balance:
    def __init__(self):
        self._times = collections.deque(maxlen=max_data_points)
        self._masses = collections.deque(maxlen=max_data_points)
        self._mass = None
        self._mass_flow_rate = 0.0

        self._counter = 0

    @property
    def mass(self):
        return self._mass

    @mass.setter
    def mass(self, value):
        """
        inputs: value - masses that are read from the balance using serial
        sets self._mass as the value, appends the current time to self._times, appends value to masses
        every 20 inputs, calculate dt and if dt>120, calculate flow rate and reset self._times and self._masses
        """
        self._counter += 1

        t = time.time()
        value = float(value)
        self._mass = value
        self._times.append(t)
        self._masses.append(value)

        if self._counter == max_data_points:
            try:
                self.estimate_flow_rate()
            except Exception as e:
                print(f'Exception occured while estimating mass flow rate for balance {self}: {e}')
            self._counter = 0

    def estimate_flow_rate(self):
        try:
            result = linregress(self._times, self._masses)
            self._mass_flow_rate = result.slope * 60
        except Exception:
            self._mass_flow_rate = 0.0
            raise

    @property
    def flow_rate(self):
        """
        ouputs flow rate which is the process variable in PID_Controller
        """
        try:
            return self._mass_flow_rate
        except:
            return 0.0

#Test PID controller
#the first index of each list is part of one system, the second index is part of another, etc.
balance_ports = ['COM19', 'COM20']
pump_ports = ['COM5', 'COM6']

pump_controller1 = PID(set_point=NotImplemented, kp=NotImplemented, ki=NotImplemented, kd=NotImplemented, integral_error_limit=100)
pump_controller2 = PID(set_point=NotImplemented, kp=NotImplemented, ki=NotImplemented, kd=NotImplemented, integral_error_limit=100)
pump_controllers = [pump_controller1, pump_controller2]

csv_filenames = ['test1', 'test2']

balance_sers = []
pump_sers = []

def test(balance_port, pump_port, pump_controller, csv_filename):
    balance_ser = serial.Serial(port=balance_port, baudrate = 9600, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE,
                                bytesize=serial.EIGHTBITS, timeout=0.2)
    print("connected to: " + balance_ser.portstr)
    pump_ser = serial.Serial(port=pump_port, baudrate=9600, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE,
                        bytesize=serial.EIGHTBITS, timeout=1)
    print("connected to: " + pump_ser.portstr)
    pump_ser.write(b'RU\r\n')

    balance_sers.append(balance_ser)
    pump_sers.append(pump_ser)

    balance_class = Balance()

    # Prompt user for CSV file name
    csv_filename = csv_filename + '.csv'

    # Open CSV file for writing
    try:
        csv_file = open(csv_filename, 'w', newline='')
    except:
        print("bad file")

    last_flow_rate = 0.0
    while True:
        try:
            balance_data = balance_ser.read(1000)
            value = balance_data.split()[1].decode('ascii').strip()

            if value.startswith('+') or value.startswith('-'):
                # print('skip')
                continue
            else:
                mass_in_float = float(value.split('g')[0])
                balance_class.mass = mass_in_float
                flow_rate = -(balance_class.flow_rate)
                # print('current flow rate:', flow_rate)

                if flow_rate != last_flow_rate:
                    output = float(pump_controller(flow_rate))

                    #put the output in the correct format - for eldex pump (assumes output is less than 100 and nonnegative)
                    output_str = f'{output:06.3f}'

                    # print('updated flow rate:', output)

                    #put flow rate into eldex pump command // comment out to use
                    command_str = f'SF{output_str}\r\n'
                    pump_ser.write(command_str.encode('ascii'))

                    # Read and print the response from the pump
                    # pump_response = pump_ser.readline().decode('ascii')
                    # print('pump response:', pump_response)

                last_flow_rate = flow_rate

            human_time = datetime.now()
            log_time = human_time.timestamp()
            # print(f'{human_time}')

            csv_file.write(f'{log_time},{human_time},{mass_in_float},{flow_rate},{output}\n')
            csv_file.flush()

            time.sleep(.1)

        except Exception as e:
            print('Error:', e)

def pid_start():
    for i in range(len(balance_ports)):
        thread = threading.Thread(target=test, args=(balance_ports[i], pump_ports[i], pump_controllers[i], csv_filenames[i]))
        thread.daemon = True
        thread.start()

    while True:
        try:
            time.sleep(1)
        except KeyboardInterrupt:
            print('\nStopping serial reading...')
            for b, p in zip(balance_sers, pump_sers):
                b.close()
                p.write(b'ST\r\n')
                p.close()
            break
