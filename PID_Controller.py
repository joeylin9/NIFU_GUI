import time
from typing import Optional
from scipy.stats import linregress
import serial
from datetime import datetime
import threading

class PID_Controller:
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
            self._error = 0 #set error to 0 if process_variable is 0
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

class Balance:
    def __init__(self):
        self._times = []
        self._masses = []
        self._mass = None
        self._mass_flow_rate = 0.0

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
        t = time.time()
        value = float(value)
        self._mass = value

        self._times.append(t)
        self._masses.append(value)

        dt = 0.0
        if len(self._times) % 10 == 0:
            dt = self._times[-1] - self._times[0]

            try:
                if dt >= 10:
                    self.estimate_flow_rate()
                    for i in range(10):
                        self._times.popleft()
                        self._masses.popleft()

            except Exception as e:
                print(f'Exception occured while estimating mass flow rate for balance {self}: {e}')

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

pump_controller1 = PID_Controller(set_point=NotImplemented, kp=NotImplemented, ki=NotImplemented, kd=NotImplemented, integral_error_limit=100)
pump_controller2 = PID_Controller(set_point=NotImplemented, kp=NotImplemented, ki=NotImplemented, kd=NotImplemented, integral_error_limit=100)
pump_controllers = [pump_controller1, pump_controller2]

balance_classes = [f'b{i+1}' for i in range(len(balance_ports))]
csv_filenames = ['test1', 'test2']

def test(balance_port, pump_port, pump_controller, balance_class, csv_filename):
    balance_ser = serial.Serial(port=balance_port, baudrate = 9600, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE,
                                bytesize=serial.EIGHTBITS, timeout=0.2)
    print("connected to: " + balance_ser.portstr)
    pump_ser = serial.Serial(port=pump_port, baudrate=9600, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE,
                        bytesize=serial.EIGHTBITS, timeout=1)
    print("connected to: " + pump_ser.portstr)

    balance_class = Balance()

    # Prompt user for CSV file name
    csv_filename = csv_filename + '.csv'

    # Open CSV file for writing
    try:
        csv_file = open(csv_filename, 'w', newline='')
    except:
        print("bad file")

    while True:
        try:
            balance_data = balance_ser.read(1000)
            value = balance_data.split()[1].decode('ascii').strip()

            if value.startswith('+') or value.startswith('-'):
                # print('skip')
                pass
            else:
                mass_in_float = float(value.split('g')[0])
                balance_class.mass = mass_in_float
                flow_rate = -(balance_class.flow_rate)
                # print('current flow rate:', flow_rate)
                output = float(pump_controller(flow_rate))

                #put the output in the correct format - for eldex pump (assumes output is less than 100 and nonnegative)
                output_str = str(output)
                if len(output_str)>=6:
                    output_str = str(round(float(output_str), 3))
                if output<10:
                    output_str = '0' + output_str
                if len(output_str)<6:
                    output_str = output_str + ('0' * (6-len(output_str)))

                # print('updated flow rate:', output)

                #put flow rate into eldex pump command // comment out to use
                command_str = f'SF{output}\r\n'
                pump_ser.write(command_str.encode('ascii'))

                # Read and print the response from the pump
                # pump_response = pump_ser.readline().decode('ascii')
                # print('pump response:', pump_response)

            time.sleep(.1)

            human_time = datetime.now()
            log_time = human_time.timestamp()
            print(f'{human_time}')

            csv_file.write(','.join([str(value) for value in [log_time, human_time, mass_in_float, flow_rate, output]]))
            csv_file.write('\n')
            csv_file.flush()

        except KeyboardInterrupt:
            print('\nStopping serial reading...')
            balance_ser.close()
            break

threads = [f'thread{i+1}' for i in range(len(balance_ports))]
thread_objects = []
for i, thread in enumerate(threads):
    thread = threading.Thread(target=test, args=(balance_ports[i], pump_ports[i], pump_controllers[i], balance_classes[i], csv_filenames[i]))
    thread_objects.append(thread)
    thread.start()

for thread in thread_objects:
    thread.join()
