import tkinter as tk
from NIFU_Serial import EldexPump, UI22_Pump, Balance

class NIFU_Synthesis:
    def __init__(self):
        self.root = tk.Tk()
        tk.Label(self.root, text="NIFU SYNTHESIS", font=('Arial',18, 'bold')).pack(pady=10)

        vscrollbar = tk.Scrollbar(self.root, orient='vertical')
        vscrollbar.pack(fill='y', side='right', expand=False)
        hscrollbar = tk.Scrollbar(self.root, orient='horizontal')
        hscrollbar.pack(fill='x', side='bottom', expand=False)
        canvas = tk.Canvas(self.root, bd=0, highlightthickness=0, yscrollcommand=vscrollbar.set, xscrollcommand=hscrollbar.set)
        canvas.pack(side='left', fill='both', expand=True)
        vscrollbar.config(command=canvas.yview)
        hscrollbar.config(command=canvas.xview)

        canvas.xview_moveto(0)
        canvas.yview_moveto(0)

        self.interior = tk.Frame(canvas)
        canvas.create_window(0,0, window=self.interior, anchor='nw')

        def configure_interior(event):
            # Update the scrollbars to match the size of the inner frame.
            size = (self.interior.winfo_reqwidth(), self.interior.winfo_reqheight())
            canvas.config(scrollregion="0 0 %s %s" % size)
            if self.interior.winfo_reqwidth() != canvas.winfo_width():
                # Update the canvas's width to fit the inner frame.
                canvas.config(width=self.interior.winfo_reqwidth())
            if self.interior.winfo_reqheight() != canvas.winfo_height():
            # Update the canvas's width to fit the inner frame.
                canvas.config(height=self.interior.winfo_reqheight())
        self.interior.bind('<Configure>', configure_interior)

        gui_frame = tk.Frame(self.interior)

        ### ---EQUIPMENT--- ###
        equipment_frame = tk.Frame(gui_frame)

        ### --- PUMPS --- ###
        pumps_frame = tk.Frame(equipment_frame)
        tk.Label(equipment_frame, text="Pumps", font=('Arial', 16, 'underline')).pack(anchor='nw', padx=15)
        tk.Label(pumps_frame, text='Connect', font=('Arial', 12, 'bold')).grid(row=0, column=1)
        tk.Label(pumps_frame, text='On', font=('Arial', 12, 'bold')).grid(row=0, column=2)
        tk.Label(pumps_frame, text='Off', font=('Arial', 12, 'bold')).grid(row=0, column=3)
        tk.Label(pumps_frame, text='Flow Rate', font=('Arial', 12, 'bold')).grid(row=0, column=4)
        tk.Label(pumps_frame, text='Set Flow Rate', font=('Arial', 12, 'bold')).grid(row=0, column=5)
        self.pumps_list = ['Pump 1: HNO₃',
            'Pump 2: Acetic anhydride',
            'Pump 3: Furfural',
            'Pump 4: KOH',
            'Pump 5: 2MeTHF',
            'Pump 6: Organic',
            'Pump 7: Aqueous',
            'Pump 8: H₂SO₄',
            'Pump 9: Amionhydantoin',
            'Pump 10: Crude NIFU Out'
        ]
        self.pump_connect_vars = [False] * len(self.pumps_list)
        self.pump_connect_buttons = []
        self.pump_on_buttons = []
        self.pump_off_buttons = []
        self.pump_flow_entry_vars = []

        for i, pump_name in enumerate(self.pumps_list):
            # Pump names
            tk.Label(pumps_frame, text=pump_name).grid(row=i+1, column=0, sticky='w')

            # Connect buttons
            pump_connect_button = tk.Button(pumps_frame, text='Disconnected', width=12, command=lambda i=i: self.pump_connect(i))
            pump_connect_button.grid(row=i+1, column=1, padx=10)
            self.pump_connect_buttons.append(pump_connect_button)

            # On/Off buttons
            pump_on_button = tk.Button(pumps_frame, text='On', width=7, command=lambda i=i: self.pump_on(i))
            pump_off_button = tk.Button(pumps_frame, text='Off', width=7, command=lambda i=i: self.pump_off(i))
            self.pump_on_buttons.append(pump_on_button)
            self.pump_off_buttons.append(pump_off_button)
            pump_on_button.grid(row=i+1, column=2, padx = 10)
            pump_off_button.grid(row=i+1, column=3, padx=10)

            # Entry for flow rate
            self.pump_flow_entry_var = tk.StringVar()
            pump_flow_entry = tk.Entry(pumps_frame, textvariable=self.pump_flow_entry_var, width=15)
            pump_flow_entry.grid(row=i+1, column=4, padx=10)
            self.pump_flow_entry_vars.append(self.pump_flow_entry_var)

            # Set Flow Rate Button
            pump_set_flow_rate_button = tk.Button(pumps_frame, text='Set', width=5, command=lambda i=i: self.pump_set_flow_rate(i))
            pump_set_flow_rate_button.grid(row=i+1, column=5)

        pumps_frame.pack(anchor='nw', padx=15)

        self.pump_type_vars = [None for i in self.pumps_list]
        self.pump_port_vars = [None for i in self.pumps_list]
        self.balance_port_vars = [None for i in self.pumps_list]

        ### --- VALVES --- ###
        valves_frame = tk.Frame(equipment_frame)
        tk.Label(equipment_frame, text="3-Way Valves", font=('Arial', 16, 'underline')).pack(anchor='nw', padx=15, pady=(10,0))
        self.valves_dict = {
            'Valve 1: Organic': None,
            'Valve 2: H₂SO₄': None,
            'Valve 3: Aminohydantoin': None
        }
        self.valves_onoff_vars = []

        for i, valve_name in enumerate(self.valves_dict):
            # Valve names
            tk.Label(valves_frame, text=valve_name).grid(row=i, column=0, sticky='w')

            # On/Off buttons
            valves_var = tk.IntVar()
            valves_var.set(1)
            self.valves_onoff_vars.append(valves_var)
            valve_on_button = tk.Radiobutton(valves_frame, text='collection', value=1, variable=valves_var)
            valve_off_button = tk.Radiobutton(valves_frame, text='waste', value=0, variable=valves_var)
            valve_on_button.grid(row=i, column=1)
            valve_off_button.grid(row=i, column=2)

        valves_frame.pack(anchor='nw', padx=15)

        ### --- TEMPERATURES --- ###
        temps_frame = tk.Frame(equipment_frame)
        tk.Label(equipment_frame, text="Reactor Temperatures (°C)", font=('Arial', 16, 'underline')).pack(anchor='nw', padx=15, pady=(10,0))
        self.temps_dict = {
            'Reactor 1: HNO₃': ['off', '0'],
            'Reactor 2: Furfural': ['off', '0'],
            'Reactor 3: KOH': ['off', '0'],
            'Reactor 4: 2MeTHF': ['off', '0'],
            'Reactor 5: H₂SO₄': ['off', '0'],
            'Reactor 6: Aminohydantoin': ['off', '0']
        }
        self.temps_onoff_vars = []
        self.temp_entry_vars = []

        for i, temp_name in enumerate(self.temps_dict):
            # Temp names
            tk.Label(temps_frame, text=temp_name).grid(row=i, column=0, sticky='w')

            # On/Off buttons
            temps_onoff_var = tk.IntVar()
            temps_onoff_var.set(0)  # Initial state: off
            self.temps_onoff_vars.append(temps_onoff_var)
            temp_on_button = tk.Radiobutton(temps_frame, text='on', value=1, variable=temps_onoff_var)
            temp_off_button = tk.Radiobutton(temps_frame, text='off', value=0, variable=temps_onoff_var)
            temp_on_button.grid(row=i, column=1)
            temp_off_button.grid(row=i, column=2)

            # Entry for temperature
            self.temp_entry_var = tk.StringVar()
            temp_entry= tk.Entry(temps_frame, textvariable=self.temp_entry_var)
            temp_entry.grid(row=i, column=3, sticky='e', padx=(15,0))
            self.temp_entry_vars.append(self.temp_entry_var)

        temps_frame.pack(anchor='nw', padx=15)

        ### --- LIQUID LEVELS --- ###
        liquid_frame = tk.Frame(equipment_frame)
        tk.Label(equipment_frame, text="Liquid Levels (mL)", font=('Arial', 16, 'underline')).pack(anchor='nw', padx=15, pady=(10,0))
        self.liquids_dict = {'Organic': '0', 'Aqueous': '0'}

        self.org_var = tk.StringVar()
        self.org_var.set('0')
        self.aq_var = tk.StringVar()
        self.aq_var.set('0')

        tk.Label(liquid_frame, text='Organic: ').grid(row=0, column=0)
        tk.Entry(liquid_frame, textvariable=self.org_var).grid(row=0, column=1, pady=10)
        tk.Label(liquid_frame, text='Aqueous: ').grid(row=1, column=0)
        tk.Entry(liquid_frame, textvariable=self.aq_var).grid(row=1, column=1)

        liquid_frame.pack(anchor='nw', padx=15)

        ### --- STIRRER --- ###
        stirrer_frame = tk.Frame(equipment_frame)
        tk.Label(equipment_frame, text="Stirrer (rpm)", font=('Arial', 16, 'underline')).pack(anchor='nw', padx=15, pady=(10,0))

        self.stirrer_dict = {'Stirrer 1': '0'}
        tk.Label(stirrer_frame, text='Stirrer 1').grid(row=0, column=0)

        self.stirrer_var = tk.StringVar()
        self.stirrer_var.set('0')
        stirrer_entry = tk.Entry(stirrer_frame, textvariable=self.stirrer_var)
        stirrer_entry.grid(row=0, column=1, padx=(15,0), pady=10)

        stirrer_frame.pack(anchor='nw', padx=15)

        # Create the Enter button
        enter_button = tk.Button(self.root, text='Assign and Read Data', command=self.apply_button_click)
        enter_button.place(x=50, y=10)

        equipment_frame.grid(row=0, column=0, sticky='nw')



        ### --- DATA --- ###
        data_frame = tk.Frame(gui_frame)
        tk.Label(data_frame, text="Graph Data", font=('Arial', 16, 'underline')).grid(row=0, column=0, pady=10, sticky='nw')

        #Checkboxes for different data
        data_types_frame = tk.Frame(data_frame)
        self.data_types = ['Temperature (°C)', 'Pressure (psi)', 'Balance (g)', 'Flow Rate (mL/min)']
        self.data_types_var = [tk.BooleanVar() for data_type in self.data_types]
        for index, value in enumerate(self.data_types):
            data_types_checkbox = tk.Checkbutton(data_types_frame, text=value, variable=self.data_types_var[index])
            data_types_checkbox.grid(row=0, column=index)
            self.data_types_var[index].trace_add('write', self.update_plot_checkboxes)
        data_types_frame.grid(row=1, column=0, sticky='w')

        #graph and graph buttons
        graph_frame = tk.Frame(data_frame)
        graph_frame.columnconfigure(0, weight=4)
        graph_frame.columnconfigure(1, weight=1)

        # graph_display
        graph_display_frame = tk.Frame(graph_frame, width=600, height=450, bg='white')

        #graph_buttons_table
        graph_buttons_table_frame = tk.Frame(graph_frame)

        #buttons
        self.start_button = tk.Button(graph_buttons_table_frame, text='Start', width=15, command=self.change_start_button)
        self.start_button.grid(row=0, column=0)
        self.stop_button = tk.Button(graph_buttons_table_frame, text='Stop', width=15, activebackground='IndianRed1', command=self.change_stop_button)
        self.stop_button.grid(row=1, column=0)
        update_button = tk.Button(graph_buttons_table_frame, text='Update', width=15)
        update_button.grid(row=2, column=0)
        get_data_button = tk.Button(graph_buttons_table_frame, text='Get Data', width=15)
        get_data_button.grid(row=3, column=0)

        #table
        tk.Text(graph_buttons_table_frame, width=20, height=20, bg='gray').grid(row=4, column=0, pady=(25,0))

        graph_display_frame.grid(row=0, column=0, sticky='N')
        graph_buttons_table_frame.grid(row=0, column=1, sticky='n', padx=20)
        graph_frame.grid(row=2, column=0, sticky='w')

        #Checkboxes for what to plot
        tk.Label(data_frame, text='Plot:',font=('Arial', 16, 'underline')).grid(row=3, column=0, pady=10, sticky='nw')
        self.plot_frame = tk.Frame(data_frame)

        # Temperature checkboxes
        self.plot_temperature_name = tk.Label(self.plot_frame, text='Temperature:')
        self.plot_temperature_name.grid(row=0, column=0, sticky='nw')
        self.plot_temperature_name.grid_remove()

        self.plot_temperatures = ['HNO₃', 'Furfural', 'KOH', '2MeTHF', 'Aq-Org Separator', 'H₂SO₄', 'Aminohydantoin']
        self.plot_temperatures_var = [tk.BooleanVar() for _ in self.plot_temperatures]
        self.plot_temperatures_checkboxes = []
        self.plot_temperatures_frame = tk.Frame(self.plot_frame)

        for index, value in enumerate(self.plot_temperatures):
            plot_temperatures_checkbox = tk.Checkbutton(self.plot_temperatures_frame, text=value, variable=self.plot_temperatures_var[index])
            self.plot_temperatures_checkboxes.append(plot_temperatures_checkbox)
            plot_temperatures_checkbox.grid(row=0, column=index, sticky='w')
            plot_temperatures_checkbox.grid_remove()

        self.plot_temperatures_frame.grid(row=0, column=1, sticky='w')

        # Pressure checkboxes
        self.plot_pressure_name = tk.Label(self.plot_frame, text='Pressure:')
        self.plot_pressure_name.grid(row=1, column=0, sticky='nw')
        self.plot_pressure_name.grid_remove()

        self.plot_pressures = ['HNO₃', 'Furfural', 'KOH', 'H₂SO₄', 'Aminohydantoin']
        self.plot_pressures_var = [tk.BooleanVar() for _ in self.plot_pressures]
        self.plot_pressures_checkboxes = []
        self.plot_pressures_frame = tk.Frame(self.plot_frame)

        for index, value in enumerate(self.plot_pressures):
            plot_pressures_checkbox = tk.Checkbutton(self.plot_pressures_frame, text=value, variable=self.plot_pressures_var[index])
            self.plot_pressures_checkboxes.append(plot_pressures_checkbox)
            plot_pressures_checkbox.grid(row=0, column=index, sticky='w')
            plot_pressures_checkbox.grid_remove()

        self.plot_pressures_frame.grid(row=1, column=1, sticky='w')

        # Balance checkboxes
        self.plot_balance_name = tk.Label(self.plot_frame, text='Balance:')
        self.plot_balance_name.grid(row=2, column=0, sticky='nw')
        self.plot_balance_name.grid_remove()

        self.plot_balances = ['HNO₃', 'Acetic anhydride', 'Furfural', 'KOH', '2MeTHF',
                              'Aqueous', 'H₂SO₄', 'Aminohydantoin', 'Crude NIFU Out']
        self.plot_balances_var = [tk.BooleanVar() for _ in self.plot_balances]
        self.plot_balances_checkboxes = []
        self.plot_balances_frame = tk.Frame(self.plot_frame)

        for index, value in enumerate(self.plot_balances):
            plot_balances_checkbox = tk.Checkbutton(self.plot_balances_frame, text=value, variable=self.plot_balances_var[index])
            self.plot_balances_checkboxes.append(plot_balances_checkbox)
            if index <= 5:
                plot_balances_checkbox.grid(row=0, column=index, sticky='w')
            else:
                plot_balances_checkbox.grid(row=1, column=index-6, sticky='w')
            plot_balances_checkbox.grid_remove()

        self.plot_balances_frame.grid(row=2, column=1, sticky='w')

        # Flow rate checkboxes
        self.plot_flowrate_name = tk.Label(self.plot_frame, text='Flow Rate:')
        self.plot_flowrate_name.grid(row=3, column=0, sticky='nw')
        self.plot_flowrate_name.grid_remove()

        self.plot_flow_rates = ['HNO₃', 'Acetic anhydride', 'Reactor 1', 'Furfual', 'Reactor 2',
                                'KOH', '2MeTHF', 'H₂SO₄', 'Aminohydantoin', 'Crude NIFU Out']
        self.plot_flow_rates_var = [tk.BooleanVar() for _ in self.plot_flow_rates]
        self.plot_flow_rates_checkboxes = []
        self.plot_flow_rates_frame = tk.Frame(self.plot_frame)

        for index, value in enumerate(self.plot_flow_rates):
            plot_flow_rates_checkbox = tk.Checkbutton(self.plot_flow_rates_frame, text=value, variable=self.plot_flow_rates_var[index])
            self.plot_flow_rates_checkboxes.append(plot_flow_rates_checkbox)
            if index <= 5:
                plot_flow_rates_checkbox.grid(row=0, column=index, sticky='w')
            else:
                plot_flow_rates_checkbox.grid(row=1, column=index-6, sticky='w')
            plot_flow_rates_checkbox.grid_remove()

        self.plot_flow_rates_frame.grid(row=3, column=1, sticky='w')


        self.plot_frame.grid(row=4, column=0, sticky='w')
        data_frame.grid(row=0, column=1, sticky='nw')

        gui_frame.pack()

        tk.Button(self.root, text='TEST', command=self.test).place(x=10, y=10)
        self.root.bind("<KeyPress>", self.exit_shortcut) #press escape button on keyboard to close the GUI
        self.root.mainloop()


    #equipment functions

    #pumps
    def pump_connect(self, pump_index):
        if self.pump_connect_vars[pump_index]:  # If already connected
            self.pump_connect_vars[pump_index] = False
            self.pump_connect_buttons[pump_index].config(bg='SystemButtonFace', text='Disconnected')  # Change back to default color
        else:  # If not connected
            self.pump_connect_vars[pump_index] = True
            self.pump_connect_buttons[pump_index].config(bg='LightSkyBlue1', text='Connected')  # Change to blue color

    def pump_on(self, pump_index):
        self.pump_on_buttons[pump_index].config(bg='pale green')
        self.pump_off_buttons[pump_index].config(bg='SystemButtonFace')

        if self.pump_connect_vars[pump_index]: #if connected
            pump_type = self.pump_type_vars[pump_index].get().upper()
            pump_port_number = self.pump_port_vars[pump_index].get()

            if pump_type == 'ELDEX':
                EldexPump.eldex_pump_command(self, port_number=pump_port_number, command='RU')
            elif pump_type == 'UI-22':
                UI22_Pump.UI22_pump_command(self, port_number=pump_port_number, command='G1', value='1')

    def pump_off(self, pump_index):
        self.pump_off_buttons[pump_index].config(bg='IndianRed1')
        self.pump_on_buttons[pump_index].config(bg='SystemButtonFace')

        if self.pump_connect_vars[pump_index]: #if connected
            pump_type = self.pump_type_vars[pump_index].get().upper()
            pump_port_number = self.pump_port_vars[pump_index].get()

            if pump_type == 'ELDEX':
                EldexPump.eldex_pump_command(self, port_number=pump_port_number, command='ST')
            elif pump_type == 'UI-22':
                UI22_Pump.UI22_pump_command(self, port_number=pump_port_number, command='G1', value='0')

    def pump_set_flow_rate(self, pump_index):
        if self.pump_connect_vars[pump_index]: #if connected
            pump_type = self.pump_type_vars[pump_index].get().upper()
            pump_port_number = self.pump_port_vars[pump_index].get()
            flow_rate = self.pump_flow_entry_vars[pump_index].get()

            if pump_type == 'ELDEX':
                EldexPump.eldex_pump_command(self, port_number=pump_port_number, command='SF', value=flow_rate)
            elif pump_type == 'UI-22':
                UI22_Pump.UI22_pump_command(self, port_number=pump_port_number, command='S3', value=flow_rate)

    def change_valves(self):
        for i, valve_name in enumerate(self.valves_dict):
            # Update status ('collection', or 'waste')
            valve_status = 'collection' if self.valves_onoff_vars[i].get() == 1 else 'waste'
            self.valves_dict[valve_name] = valve_status

    def change_temps(self):
        for i, temp_name in enumerate(self.temps_dict):
            # Update status ('on' or 'off')
            temp_status = 'on' if self.temps_onoff_vars[i].get() == 1 else 'off'
            self.temps_dict[temp_name][0] = temp_status

            # Update temperature
            if temp_status == 'on':
                temperature = self.temp_entry_vars[i].get()
                self.temps_dict[temp_name][1] = temperature
            else:
                self.temps_dict[temp_name][1] = '0'

    def change_liquids(self):
        self.liquids_dict['Organic'] = self.org_var.get()
        self.liquids_dict['Aqueous'] = self.aq_var.get()

    def change_stirrer(self):
        self.stirrer_dict['Stirrer 1'] = self.stirrer_var.get()

    def apply_button_click(self):
        # Update all dictionaries with the current values from the GUI, and open commands page
        self.change_valves()
        self.change_temps()
        self.change_liquids()
        self.change_stirrer()
        self.open_assign()

    def open_assign(self):
        """
        Assigns a pump type and port number to each pump, and has commands to read data
        Outputs a list for pump type, pump port numbers, and balance port numbers, in the order that corresponds with self.pumps_list
        """

        self.assign_page = tk.Toplevel(self.root)

        #pumps and balance
        tk.Label(self.assign_page, text='Assign Pump Types and Ports', font=('Arial', 14)).pack(pady=10)
        pump_frame = tk.Frame(self.assign_page)

        tk.Label(pump_frame, text='Pump Name', font=('TkDefaultFont', 9, 'underline')).grid(row=0, column=0)
        tk.Label(pump_frame, text='Pump Type', font=('TkDefaultFont', 9, 'underline')).grid(row=0, column=1)
        tk.Label(pump_frame, text='Pump Port Number', font=('TkDefaultFont', 9, 'underline')).grid(row=0, column=2)
        tk.Label(pump_frame, text='Balance Port Number', font=('TkDefaultFont', 9, 'underline')).grid(row=0, column=3)

        self.balance_save_vars = [tk.BooleanVar() for i in self.pumps_list]

        for i, name in enumerate(self.pumps_list):
            tk.Label(pump_frame, text=name).grid(row=i+1, column=0, padx=5)

            self.pump_type_var = tk.StringVar()
            if self.pump_type_vars[i]:
                self.pump_type_var.set(self.pump_type_vars[i].get())
            pump_type_entry = tk.Entry(pump_frame, textvariable=self.pump_type_var)
            pump_type_entry.grid(row=i+1, column=1, padx=5)
            self.pump_type_vars[i] = (self.pump_type_var)

            self.pump_port_var = tk.IntVar()
            if self.pump_port_vars[i]:
                self.pump_port_var.set(self.pump_port_vars[i].get())
            pump_port_spinbox = tk.Spinbox(pump_frame, textvariable=self.pump_port_var, from_=0, to=20, wrap=True)
            pump_port_spinbox.grid(row=i+1, column=2, padx=5)
            self.pump_port_vars[i] = (self.pump_port_var)

            #balances
            self.balance_port_var = tk.IntVar()
            if self.balance_port_vars[i]:
                self.balance_port_var.set(self.balance_port_vars[i].get())
            balance_port_spinbox = tk.Spinbox(pump_frame, textvariable=self.balance_port_var, from_=0, to=20, wrap=True)
            balance_port_spinbox.grid(row=i+1, column=3, padx=5)
            self.balance_port_vars[i] = (self.balance_port_var)

            #reading data buttons
            tk.Button(pump_frame, text='Read Flow Rate', command=lambda i=i: self.read_flow_rate(i)).grid(row=i+1, column=4,padx=5)
            tk.Button(pump_frame, text='Read Balance Data', command=lambda i=i: self.read_balance_data(i)).grid(row=i+1, column=5, padx=5)

            tk.Checkbutton(pump_frame, text='Save', variable=self.balance_save_vars[i]).grid(row=i+1, column=6)

        pump_frame.pack(pady=10)

    def read_flow_rate(self, pump_index):
        pump_type = self.pump_type_vars[pump_index].get().upper()
        pump_port_number = self.pump_port_vars[pump_index].get()
        if pump_type == 'ELDEX':
            EldexPump.eldex_pump_command(self, port_number=pump_port_number, command='RF')
        elif pump_type == 'UI-22':
            UI22_Pump.UI22_pump_command(self, port_number=pump_port_number, command='Q2', value='c')

    def read_balance_data(self, balance_index):
        balance_port_number = self.balance_port_vars[balance_index].get()
        Balance.balance_read_data(self, port_number=balance_port_number, save=self.balance_save_vars[balance_index].get())


    #graph data functions
    def change_start_button(self):
        self.start_button.config(background='pale green')
        self.stop_button.config(background='SystemButtonFace')

    def change_stop_button(self):
        self.start_button.config(background='SystemButtonFace')

    def update_plot_checkboxes(self, *args):
        frames = [
            (self.plot_temperature_name, self.plot_temperatures_checkboxes, self.plot_temperatures_frame),
            (self.plot_pressure_name, self.plot_pressures_checkboxes, self.plot_pressures_frame),
            (self.plot_balance_name, self.plot_balances_checkboxes, self.plot_balances_frame),
            (self.plot_flowrate_name, self.plot_flow_rates_checkboxes, self.plot_flow_rates_frame),
        ]

        row = 0
        for i, var in enumerate(self.data_types_var):
            name, checkboxes, frame = frames[i]
            if var.get():
                name.grid(row=row, column=0, sticky='nw')
                frame.grid(row=row, column=1, sticky='w')
                for checkbox in checkboxes:
                    checkbox.grid()
                row += 1
            else:
                name.grid_remove()
                frame.grid_remove()
                for checkbox in checkboxes:
                    checkbox.grid_remove()

    # Other functions
    def exit_shortcut(self, event):
        """Shortcut for exiting all pages"""
        if event.keysym == "Escape":
            quit()

    def test(self):
        pass
NIFU_Synthesis()
