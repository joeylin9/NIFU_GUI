import time
from scipy.stats import linregress
from datetime import datetime
import collections
from openpyxl import Workbook
import csv
import os

class pid_control:
    def __init__(self, balance_ser, pump_ser, pump_controller, pump_type, pump_name, matrix_len):
        self.balance_ser = balance_ser
        self.pump_ser = pump_ser
        p = pump_controller
        self.pump_controller = self.pid(p['set_point'], p['kp'], p['ki'], p['kd'], p['integral_error_limit'])
        self.pump_type = pump_type
        self.pump_name = pump_name
        self.max_data_points = matrix_len

        self.csv_obj = None
        self.mass = None
        self.flow_rate = None
        self.pid_output = None

        self.stop = False

    def set_off(self):
        self.stop = True

        self.mass = None
        self.flow_rate = None
        self.pid_output = None

    def set_csv_obj(self, csv_obj):
        self.csv_obj = csv_obj

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

    def start_pid(self):
        balance_ser = self.balance_ser
        pump_ser = self.pump_ser
        b = self.Balance(self.max_data_points)

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

                    if flow_rate != last_flow_rate:
                        output = float(self.pump_controller(flow_rate))
                        print('current flow rate:', flow_rate)
                        print('updated flow rate:', output)
                        output_str = f'{output:06.3f}' #assumes output is less than 100 and nonnegative

                        if self.pump_type == 'ELDEX':
                            #put flow rate into eldex pump command
                            command_str = f'SF{output_str}\r\n'
                            pump_ser.write(command_str.encode('ascii'))

                        elif self.pump_type == 'UI-22':
                            output_str = output_str.replace('.', '')
                            command_str = f';01,S3,{output_str}\r\n'
                            pump_ser.write(command_str.encode('ascii'))

                    last_flow_rate = flow_rate

                self.mass = mass_in_float
                self.flow_rate = flow_rate
                self.pid_output = output
                if self.csv_obj:
                    self.csv_obj.change_data(self.pump_name, self.get_last())

                time.sleep(.1)

            except Exception as e:
                print('Error:', e)

        if self.csv_obj:
            self.csv_obj.change_data(self.pump_name, self.get_last()) #when exciting out loop as well

    def get_last(self):
        if self.mass and self.flow_rate and self.pid_output:
            return [self.mass, self.flow_rate, self.pid_output]
        else:
            return ['','','']

class csv_file:
    def __init__(self, pump_list):
        self.pumps_data = {pump: ['','',''] for pump in pump_list}

        human_time = datetime.now()
        self.filename = str(human_time).replace(':', '.')
        self.csv_filename = self.filename + '.csv'
        self.csv_file = open(self.csv_filename, 'w', newline='', encoding="utf-8")

        self.stopped = False

    def change_data(self, pump, data):
        #data should be an array of [mass, flow rate, pid value]
        self.pumps_data[pump] = data

    def start_file(self):
        heading = 'Time,'
        for pump in self.pumps_data:
            heading += pump + ': Mass (g),' + pump + ': Flow Rate (g/min),' + pump + ': PID Value (mL/min),'
        self.csv_file.write(f'{heading}\n')

        while not self.stopped:
            human_time = datetime.now()

            self.csv_file.write(f'{human_time},')
            for p in self.pumps_data:
                mass = self.pumps_data[p][0]
                flow_rate = self.pumps_data[p][1]
                pid_value = self.pumps_data[p][2]
                self.csv_file.write(f'{mass},{flow_rate},{pid_value},')
            self.csv_file.write('\n')
            self.csv_file.flush()

            time.sleep(.2)

        # self.csv_file.close()
        # wb = Workbook()
        # ws = wb.active
        # ws.title = self.csv_filename
        # data = open(self.csv_filename)
        # csv_data = list(csv.reader(data)) #Method used to open and read a csv file
        # for i in csv_data:
        #     ws.append(i)
        # data.close()
        # wb.save(self.filename + '.xlsx')

        # #delete the original csv file
        # file = self.csv_filename
        # if(os.path.exists(file) and os.path.isfile(file)):
        #     os.remove(file)

    def stop_file(self):
        self.stopped = True
