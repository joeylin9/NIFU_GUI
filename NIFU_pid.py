import time
from scipy.stats import linregress
import serial
from datetime import datetime
import collections

class pid_control:
    def __init__(self, balance_port, pump_port, pump_controller, pump_type):
        self.balance_port = balance_port
        self.pump_port = pump_port
        p = pump_controller
        self.pump_controller = self.pid(p['set_point'], p['kp'], p['ki'], p['kd'], p['integral_error_limit'])
        self.pump_type = pump_type
        self.max_data_points = 10

        self.stop = False

    def set_balance_port(self, port):
        self.balance_port = port

    def set_pump_port(self, port):
        self.pump_port = port

    def set_pump_controller_set_point(self, set_point):
        self.pump_controller._set_point = float(set_point)

    def set_pump_type(self, pump_type):
        self.pump_type = pump_type

    def set_off(self):
        self.stop = True

    class pid:
        def __init__(self, set_point, kp, ki, kd, integral_error_limit):
            """
            set_point = set point: the desired value to output // constant, based on GUI
            pv = process variable: the current measured output // changes every recall, based on phsyical system
            kp = proportional gain // constant
            ki = integral gain // constant
            t = time // changes
            last_error // changes every recall, initially at 0
            reset // changes every recall, intially at 0
            """
            if set_point:
                self._set_point = float(set_point)
            self._kp = float(kp)
            self._ki = float(ki)
            self._kd = float(kd)
            self._integral_error_limit = float(integral_error_limit)

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

        def get_flow_rate(self):
            return self._set_point

    class Balance():
        def __init__(self, max_data_points):
            self.max_data_points = max_data_points
            self._times = collections.deque(maxlen=self.max_data_points)
            self._masses = collections.deque(maxlen=self.max_data_points)
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

            if self._counter == self.max_data_points:
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
            ouputs flow rate which is the process variable in PID
            """
            try:
                return self._mass_flow_rate
            except:
                return 0.0

    def start_pid(self, filename):
        balance_ser = serial.Serial(port=self.balance_port, baudrate = 9600, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE,
                                    bytesize=serial.EIGHTBITS, timeout=0.2)
        pump_ser = serial.Serial(port=self.pump_port, baudrate=9600, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE,
                            bytesize=serial.EIGHTBITS, timeout=1)
        b = self.Balance(self.max_data_points)

        #for csv file
        csv_filename = filename + '.csv'

        # Open CSV file for writing
        try:
            csv_file = open(csv_filename, 'w', newline='')
        except:
            print("bad file")

        last_flow_rate = 0.0
        while not self.stop:
            try:
                balance_data = balance_ser.read(1000)
                value = balance_data.split()[1].decode('ascii').strip()

                if value.startswith('+') or value.startswith('-'):
                    print('skip')
                    continue
                else:
                    mass_in_float = float(value.split('g')[0])
                    b.mass = mass_in_float
                    flow_rate = -(b.flow_rate)
                    print('current flow rate:', flow_rate)

                    if flow_rate != last_flow_rate:
                        output = float(self.pump_controller(flow_rate))

                        output_str = f'{output:06.3f}' #assumes output is less than 100 and nonnegative
                        if self.pump_type == 'ELDEX':
                            # print('updated flow rate:', output_str)

                            #put flow rate into eldex pump command
                            command_str = f'SF{output_str}\r\n'
                            pump_ser.write(command_str.encode('ascii'))

                            # Read and print the response from the pump
                            # pump_response = pump_ser.readline().decode('ascii')
                            # print('pump response:', pump_response)

                        elif self.pump_type == 'UI-22':
                            command_str = f';01,S3,{output_str}\r\n'
                            pump_ser.write(command_str.encode('ascii'))

                    last_flow_rate = flow_rate

                human_time = datetime.now()
                log_time = human_time.timestamp()
                print(f'{human_time}')

                csv_file.write(f'{log_time},{human_time},{mass_in_float},{flow_rate},{output}\n')
                csv_file.flush()

                time.sleep(.1)

            except Exception as e:
                print('Error:', e)
