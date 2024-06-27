import tkinter as tk
from tkinter import messagebox
from NIFU_Serial import EldexPump, UI22_Pump, Balance

class NIFU_Synthesis:
    def __init__(self):
        self.root = tk.Tk()
        self.root.columnconfigure(0, weight=1)
        self.root.columnconfigure(1, weight=5)
        tk.Label(self.root, text="NIFU SYNTHESIS", font=('Arial',18, 'bold')).grid(row=0, column=0, pady=(20,10))

        gui_frame = tk.Frame(self.root)

        ### ---EQUIPMENT--- ###
        equipment_frame = tk.Frame(gui_frame)

        ### --- PUMPS --- ###
        pumps_frame = tk.Frame(equipment_frame)
        tk.Label(equipment_frame, text="Pumps | Flow Rates (mL/min)", font=('Arial', 16, 'underline')).pack(anchor='nw', padx=15)
        self.pumps_dict = {
            'Pump 1: HNO₃': ['off', '0', None, None],
            'Pump 2: Acetic anhydride': ['off', '0', None, None],
            'Pump 3: Furfural': ['off', '0', None, None],
            'Pump 4: KOH': ['off', '0', None, None],
            'Pump 5: 2MeTHF': ['off', '0', None, None],
            'Pump 6: Organic': ['off', '0', None, None],
            'Pump 7: Aqueous': ['off', '0', None, None],
            'Pump 8: H₂SO₄': ['off', '0', None, None],
            'Pump 9: Amionhydantoin': ['off', '0', None, None],
            'Pump 10: Crude NIFU Out': ['off', '0', None, None]
        }
        self.pumps_onoff_vars = []
        self.pump_flow_entry_vars = []

        for i, pump_name in enumerate(self.pumps_dict):
            # Pump names
            tk.Label(pumps_frame, text=pump_name).grid(row=i, column=0, sticky='w')

            # On/Off buttons
            pumps_onoff_var = tk.IntVar()
            pumps_onoff_var.set(0)  # Initial state: off
            self.pumps_onoff_vars.append(pumps_onoff_var)
            pump_on_button = tk.Radiobutton(pumps_frame, text='on', value=1, variable=pumps_onoff_var)
            pump_off_button = tk.Radiobutton(pumps_frame, text='off', value=0, variable=pumps_onoff_var)
            pump_on_button.grid(row=i, column=1)
            pump_off_button.grid(row=i, column=2)

            # Entry for flow rate
            self.pump_flow_entry_var = tk.StringVar()
            pump_flow_entry = tk.Entry(pumps_frame, textvariable=self.pump_flow_entry_var)
            pump_flow_entry.grid(row=i, column=3, sticky='e', padx=(15,0))
            self.pump_flow_entry_vars.append(self.pump_flow_entry_var)

        pumps_frame.pack(anchor='nw', padx=15)

        ### --- VALVES --- ###
        valves_frame = tk.Frame(equipment_frame)
        tk.Label(equipment_frame, text="3-Way Valves", font=('Arial', 16, 'underline')).pack(anchor='nw', padx=15, pady=(20,0))
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
        tk.Label(equipment_frame, text="Reactor Temperatures (°C)", font=('Arial', 16, 'underline')).pack(anchor='nw', padx=15, pady=(20,0))
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
        tk.Label(equipment_frame, text="Liquid Levels (mL)", font=('Arial', 16, 'underline')).pack(anchor='nw', padx=15, pady=(20,0))
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
        tk.Label(equipment_frame, text="Stirrer (rpm)", font=('Arial', 16, 'underline')).pack(anchor='nw', padx=15, pady=(20,0))

        self.stirrer_dict = {'Stirrer 1': '0'}
        tk.Label(stirrer_frame, text='Stirrer 1').grid(row=0, column=0)

        self.stirrer_var = tk.StringVar()
        self.stirrer_var.set('0')
        stirrer_entry = tk.Entry(stirrer_frame, textvariable=self.stirrer_var)
        stirrer_entry.grid(row=0, column=1, padx=(15,0), pady=10)

        stirrer_frame.pack(anchor='nw', padx=15)

        # Create the Enter button
        enter_button = tk.Button(self.root, text='Apply Changes / Commands', command=self.apply_button_click)
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
        data_types_frame.grid(row=1, column=0, sticky='w')

        #graph and graph buttons
        graph_frame = tk.Frame(data_frame)
        graph_frame.columnconfigure(0, weight=4)
        graph_frame.columnconfigure(1, weight=1)

        # graph_display
        graph_display_frame = tk.Frame(graph_frame, width=790, height=500, bg='white')


        #graph_buttons_table
        graph_buttons_table_frame = tk.Frame(graph_frame)

        #buttons
        self.start_button = tk.Button(graph_buttons_table_frame, text='Start', width=20, command=self.change_start_button)
        self.start_button.grid(row=0, column=0)
        self.stop_button = tk.Button(graph_buttons_table_frame, text='Stop', width=20, activebackground='IndianRed1', command=self.change_stop_button)
        self.stop_button.grid(row=1, column=0)
        update_button = tk.Button(graph_buttons_table_frame, text='Update', width=20)
        update_button.grid(row=2, column=0)
        get_data_button = tk.Button(graph_buttons_table_frame, text='Get Data', width=20)
        get_data_button.grid(row=3, column=0)

        #table
        tk.Text(graph_buttons_table_frame, width=25, height=23, bg='gray').grid(row=4, column=0, pady=(25,0))


        graph_display_frame.grid(row=0, column=0)
        graph_buttons_table_frame.grid(row=0, column=1, sticky='n', padx=20)
        graph_frame.grid(row=2, column=0, sticky='w')

        #Checkboxes for what to plot
        tk.Label(data_frame, text='Plot:',font=('Arial', 16, 'underline')).grid(row=3, column=0, pady=10, sticky='nw')
        plot_frame = tk.Frame(data_frame)

        #Temperature checkboxes
        tk.Label(plot_frame, text='Temperature:').grid(row=0, column=0, sticky='nw')
        self.plot_temperatures = ['Reactor 1: HNO₃', 'Reactor 2: Furfural', 'Reactor 3: KOH','Reactor 4: 2MeTHF',
                                'Aq-Org Separator', 'Reactor 5: H₂SO₄', 'Reactor 6: Aminohydantoin']
        self.plot_temperatures_var = [tk.BooleanVar() for data_type in self.plot_temperatures]
        for index, value in enumerate(self.plot_temperatures):
            plot_temperatures_checkbox = tk.Checkbutton(plot_frame, text=value, variable=self.plot_temperatures_var[index])
            if index <= 4:
                plot_temperatures_checkbox.grid(row=0, column=index+1, sticky='w')
            else:
                plot_temperatures_checkbox.grid(row=1, column=index-4, sticky='w', pady=(0,10))

        #Pressure checkboxes
        tk.Label(plot_frame, text='Pressure:').grid(row=2, column=0, sticky='nw')
        self.plot_pressures = ['Pressure 1: HNO₃', 'Pressure 2: Furfural', 'Pressure 3: KOH',
                               'Pressure 4: H₂SO₄', 'Pressure 5: Aminohydantoin']
        self.plot_pressures_var = [tk.BooleanVar() for data_type in self.plot_pressures]
        for index, value in enumerate(self.plot_pressures):
            plot_pressures_checkbox = tk.Checkbutton(plot_frame, text=value, variable=self.plot_pressures_var[index])
            plot_pressures_checkbox.grid(row=2, column=index+1, sticky='w', pady=(0,10))

        #Balance checkboxes
        tk.Label(plot_frame, text='Balance:').grid(row=3, column=0, sticky='nw')
        self.plot_balances = ['Balance 1: HNO₃', 'Balance 2: Acetic anhydride', 'Balance 3: Furfural', 'Balance 4: KOH',
                              'Balance 5: 2MeTHF', 'Balance 6: Aqueous', ' Balance 7: H₂SO₄', 'Balance 8: Aminohydantoin',
                              'Balance 9: Crude NIFU Out']
        self.plot_balances_var = [tk.BooleanVar() for data_type in self.plot_balances]
        for index, value in enumerate(self.plot_balances):
            plot_balances_checkbox = tk.Checkbutton(plot_frame, text=value, variable=self.plot_balances_var[index])
            if index <= 4:
                plot_balances_checkbox.grid(row=3, column=index+1, sticky='w')
            else:
                plot_balances_checkbox.grid(row=4, column=index-4, sticky='w', pady=(0,10))

        #Flow_rate checkboxes
        tk.Label(plot_frame, text='Flow Rate:').grid(row=5, column=0, sticky='nw')
        self.plot_flow_rates = ['Flow Rate 1: HNO₃', 'Flow Rate 2: Acetic anhydride', 'Flow Rate 3: Reactor 1', 'Flow Rate 4: Furfual',
                                'Flow Rate 5: Reactor 2', 'Flow Rate 6: KOH', ' Flow Rate 7: 2MeTHF', 'Flow Rate 8: H₂SO₄',
                                'Flow Rate 9: Aminohydantoin', 'Flow Rate 10: Crude NIFU Out']
        self.plot_flow_rates_var = [tk.BooleanVar() for data_type in self.plot_flow_rates]
        for index, value in enumerate(self.plot_flow_rates):
            plot_flow_rates_checkbox = tk.Checkbutton(plot_frame, text=value, variable=self.plot_flow_rates_var[index])
            if index <= 4:
                plot_flow_rates_checkbox.grid(row=5, column=index+1, sticky='w')
            else:
                plot_flow_rates_checkbox.grid(row=6, column=index-4, sticky='w', pady=(0,10))

        plot_frame.grid(row=4, column=0, sticky='w')

        data_frame.grid(row=0, column=1, sticky='nw')

        gui_frame.grid()

        tk.Button(self.root, text='TEST', command=self.p).place(x=10, y=10)
        tk.Button(self.root, text=' X ', command=quit).grid(row=0, column=0, sticky='ne', padx=10, pady=10)
        self.root.bind("<KeyPress>", self.exit_shortcut) #press escape button on keyboard to close the GUI
        self.root.attributes('-fullscreen', True)
        self.root.mainloop()

    #equipment functions
    def change_pumps(self):
        for i, pump_name in enumerate(self.pumps_dict):
            # Update status ('on' or 'off')
            pump_status = 'on' if self.pumps_onoff_vars[i].get() == 1 else 'off'
            self.pumps_dict[pump_name][0] = pump_status

            # Update flow rate
            if pump_status == 'on':
                flow_rate = self.pump_flow_entry_vars[i].get()
                self.pumps_dict[pump_name][1] = flow_rate
            else:
                self.pumps_dict[pump_name][1] = '0'

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
        self.change_pumps()
        self.change_valves()
        self.change_temps()
        self.change_liquids()
        self.change_stirrer()
        self.open_assign()

    def open_assign(self):
        self.assign_page = tk.Toplevel(self.root)
        tk.Label(self.assign_page, text='Assign Pump Types and Ports', font=('Arial', 14)).pack(pady=10)
        pump_frame = tk.Frame(self.assign_page)

        tk.Label(pump_frame, text='Pump Name', font=('TkDefaultFont', 9, 'underline')).grid(row=0, column=0)
        tk.Label(pump_frame, text='Pump Type', font=('TkDefaultFont', 9, 'underline')).grid(row=0, column=1)
        tk.Label(pump_frame, text='Port Number', font=('TkDefaultFont', 9, 'underline')).grid(row=0, column=2)

        self.pump_type_vars = []
        self.pump_port_vars = []

        self.pumps_on = []
        for p in self.pumps_dict:
            if self.pumps_dict[p][0] == 'on':
                self.pumps_on.append(p)

        for i, name in enumerate(self.pumps_on):
            tk.Label(pump_frame, text=name).grid(row=i+1, column=0, sticky='w', padx=5)

            self.pump_type_var = tk.StringVar()
            pump_type_entry = tk.Entry(pump_frame, textvariable=self.pump_type_var)
            pump_type_entry.grid(row=i+1, column=1, padx=5)
            self.pump_type_vars.append(self.pump_type_var)

            self.pump_port_var = tk.IntVar()
            pump_port_spinbox = tk.Spinbox(pump_frame, textvariable=self.pump_port_var, from_=0, to=20, wrap=True)
            pump_port_spinbox.grid(row=i+1, column=2, padx=5)
            self.pump_port_vars.append(self.pump_port_var)

        balance_frame = tk.Frame(self.assign_page)
        self.balance_port_var = tk.IntVar()
        tk.Label(balance_frame, text='Balance Port Number:').grid(row=0,column=0)
        balance_port_spinbox = tk.Spinbox(balance_frame, textvariable=self.balance_port_var, from_=0, to=20, wrap=True)
        balance_port_spinbox.grid(row=0, column=1)

        pump_frame.pack(pady=10)
        balance_frame.pack(pady=10)
        tk.Button(self.assign_page, text='Apply Changes', command=self.apply_pump_changes).pack(pady=5)
        tk.Button(self.assign_page, text='Read Flow Rates', command=self.read_flow_rates).pack(pady=5)
        tk.Button(self.assign_page, text='Read Balance Data', command=self.read_balance_data).pack(pady=5)

    def apply_pump_changes(self):
        if messagebox.askyesno(title='Confirm', message='Apply Changes?'):
            #change pump type and port
            for i, pump_name in enumerate(self.pumps_on):
                self.pumps_dict[pump_name][2] = self.pump_type_vars[i].get().upper() #pump type
                self.pumps_dict[pump_name][3] = self.pump_port_vars[i].get() #pump port number

            for i, pump_name in enumerate(self.pumps_dict):
                onoff = self.pumps_dict[pump_name][0]
                flow_rate = self.pumps_dict[pump_name][1]
                pump_type = self.pumps_dict[pump_name][2]
                pump_port_num = self.pumps_dict[pump_name][3]
                if pump_type == 'ELDEX':
                    if onoff == 'on':
                        EldexPump.eldex_pump_command(self, port_number=pump_port_num, command='RU') #start pump
                        EldexPump.eldex_pump_command(self, port_number=pump_port_num, command='SF', value=flow_rate) #set flow
                    else:
                        EldexPump.eldex_pump_command(self, port_number=pump_port_num, command='ST') #stop pump
                elif pump_type == 'UI22':
                    if onoff == 'on':
                        UI22_Pump.UI22_pump_command(self, port_number=pump_port_num, command='G1', value='1') #start pump
                        UI22_Pump.UI22_pump_command(self, port_number=pump_port_num, command='S3', value=flow_rate) #set flow
                    else:
                        UI22_Pump.UI22_pump_command(self, port_number=pump_port_num, command='G1', value='0') #stop pump
        else:
            self.assign_page.destroy()

    def read_flow_rates(self):
        #change pump type and port
        for i, pump_name in enumerate(self.pumps_on):
            self.pumps_dict[pump_name][2] = self.pump_type_vars[i].get().upper() #pump type
            self.pumps_dict[pump_name][3] = self.pump_port_vars[i].get() #pump port number

        for i, pump_name in enumerate(self.pumps_on):
            pump_type = self.pumps_dict[pump_name][2]
            pump_port_num = self.pumps_dict[pump_name][3]

            if pump_type == 'ELDEX':
                EldexPump.eldex_pump_command(self, port_number=pump_port_num, command='RF')
            elif pump_type == 'UI22':
                UI22_Pump.UI22_pump_command(self, port_number=pump_port_num, command='Q2', value='c')

    def read_balance_data(self):
        port_num = self.balance_port_var.get()
        Balance.balance_read_data(self, port_number=port_num)

    #graph data functions
    def change_start_button(self):
        self.start_button.config(background='pale green')
        self.stop_button.config(background='SystemButtonFace')

    def change_stop_button(self):
        self.start_button.config(background='SystemButtonFace')

    def exit_shortcut(self, event):
        """Shortcut for exiting all pages"""
        if event.keysym == "Escape":
            quit()

    def p(self):
        print('Pumps:', self.pumps_dict)
        print('Valves:',self.valves_dict)
        print('Temp:',self.temps_dict)
        print('Liquids:',self.liquids_dict)
        print('Stirrer:',self.stirrer_dict)

NIFU_Synthesis()
