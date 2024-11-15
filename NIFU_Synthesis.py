import tkinter as tk
import threading
from NIFU_Serial import Pump, Balance, temp, valve_fan
from NIFU_pid import pid_control, excel_file, graph
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from time import sleep

# replace with correct values
pump1_controller = {
    "set_point": None,
    "kp": 0.1,
    "ki": 0.0001,
    "kd": 0.01,
    "integral_error_limit": 100,
}
pump2_controller = {
    "set_point": None,
    "kp": 1,
    "ki": 1,
    "kd": 1,
    "integral_error_limit": 100,
}
pump3_controller = {
    "set_point": None,
    "kp": 1,
    "ki": 1,
    "kd": 1,
    "integral_error_limit": 100,
}
pump4_controller = {
    "set_point": None,
    "kp": 1,
    "ki": 1,
    "kd": 1,
    "integral_error_limit": 100,
}
pump5_controller = {
    "set_point": None,
    "kp": 1,
    "ki": 1,
    "kd": 1,
    "integral_error_limit": 100,
}
pump6_controller = {
    "set_point": None,
    "kp": 1,
    "ki": 1,
    "kd": 1,
    "integral_error_limit": 100,
}
pump7_controller = {
    "set_point": None,
    "kp": 1,
    "ki": 1,
    "kd": 1,
    "integral_error_limit": 100,
}
pump8_controller = {
    "set_point": None,
    "kp": 1,
    "ki": 1,
    "kd": 1,
    "integral_error_limit": 100,
}
pump9_controller = {
    "set_point": None,
    "kp": 1,
    "ki": 1,
    "kd": 1,
    "integral_error_limit": 100,
}
pump10_controller = {
    "set_point": None,
    "kp": 1,
    "ki": 1,
    "kd": 1,
    "integral_error_limit": 100,
}
pump_controllers = [
    pump1_controller,
    pump2_controller,
    pump3_controller,
    pump4_controller,
    pump5_controller,
    pump6_controller,
    pump7_controller,
    pump8_controller,
    pump9_controller,
    pump10_controller,
]
matrix_lengths = [10, 10, 10, 10, 10, 10, 10, 10, 10, 10]


class NIFU_Synthesis:
    def __init__(self):
        self.root = tk.Tk()
        tk.Label(self.root, text="NIFU SYNTHESIS", font=("Arial", 18, "bold")).pack(
            pady=10
        )

        vscrollbar = tk.Scrollbar(self.root, orient="vertical")
        vscrollbar.pack(fill="y", side="right", expand=False)
        hscrollbar = tk.Scrollbar(self.root, orient="horizontal")
        hscrollbar.pack(fill="x", side="bottom", expand=False)
        canvas = tk.Canvas(
            self.root,
            bd=0,
            highlightthickness=0,
            yscrollcommand=vscrollbar.set,
            xscrollcommand=hscrollbar.set,
        )
        canvas.pack(side="left", fill="both", expand=True)
        vscrollbar.config(command=canvas.yview)
        hscrollbar.config(command=canvas.xview)

        canvas.xview_moveto(0)
        canvas.yview_moveto(0)

        self.interior = tk.Frame(canvas)
        canvas.create_window(0, 0, window=self.interior, anchor="nw")

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

        self.interior.bind("<Configure>", configure_interior)

        gui_frame = tk.Frame(self.interior)

        ### ---EQUIPMENT--- ###
        equipment_frame = tk.Frame(gui_frame)
        self.excel_obj = None

        ### --- PUMPS --- ###
        pumps_frame = tk.Frame(equipment_frame)
        tk.Label(equipment_frame, text="Pumps", font=("Arial", 16, "underline")).pack(
            anchor="nw", padx=15
        )
        tk.Label(pumps_frame, text="Connect", font=("Arial", 12, "bold")).grid(
            row=0, column=1
        )
        tk.Label(pumps_frame, text="On", font=("Arial", 12, "bold")).grid(
            row=0, column=2
        )
        tk.Label(pumps_frame, text="Off", font=("Arial", 12, "bold")).grid(
            row=0, column=3
        )
        tk.Label(pumps_frame, text="Flow Rate", font=("Arial", 12, "bold")).grid(
            row=0, column=4
        )
        tk.Label(pumps_frame, text="Set Flow Rate", font=("Arial", 12, "bold")).grid(
            row=0, column=5
        )
        self.pumps_list = [
            "HNO₃",
            "Acetic anhydride",
            "Furfural",
            "KOH",
            "2MeTHF",
            "Organic",
            "Aqueous",
            "H₂SO₄",
            "Amionhydantoin",
            "Crude NIFU Out",
        ]
        self.pump_connect_vars = [False] * len(self.pumps_list)
        self.pump_connect_buttons = []
        self.pump_sers = [None] * len(self.pumps_list)
        self.balance_sers = [None] * len(self.pumps_list)
        self.pump_on_buttons = []
        self.pump_off_buttons = []
        self.pump_flow_entry_vars = []

        self.pump_pid_classes = [None] * len(self.pumps_list)
        self.pump_pid_threads_started = [False] * len(self.pumps_list)
        self.pid_vars = [tk.BooleanVar(value=True) for i in self.pumps_list]

        for i, pump_name in enumerate(self.pumps_list):
            # Pump names
            tk.Label(pumps_frame, text=f"Pump {i + 1}: {pump_name}").grid(
                row=i + 1, column=0, sticky="w"
            )

            # Connect buttons
            pump_connect_button = tk.Button(
                pumps_frame,
                text="Disconnected",
                width=12,
                command=lambda i=i: self.pump_connect(i),
            )
            pump_connect_button.grid(row=i + 1, column=1, padx=10)
            self.pump_connect_buttons.append(pump_connect_button)

            # On/Off buttons
            pump_on_button = tk.Button(
                pumps_frame, text="On", width=7, command=lambda i=i: self.pump_on(i)
            )
            pump_off_button = tk.Button(
                pumps_frame, text="Off", width=7, command=lambda i=i: self.pump_off(i)
            )
            self.pump_on_buttons.append(pump_on_button)
            self.pump_off_buttons.append(pump_off_button)
            pump_on_button.grid(row=i + 1, column=2, padx=10)
            pump_off_button.grid(row=i + 1, column=3, padx=10)

            # Entry for flow rate
            self.pump_flow_entry_var = tk.StringVar()
            pump_flow_entry = tk.Entry(
                pumps_frame, textvariable=self.pump_flow_entry_var, width=15
            )
            pump_flow_entry.grid(row=i + 1, column=4, padx=10)
            self.pump_flow_entry_vars.append(self.pump_flow_entry_var)

            # Set Flow Rate Button
            pump_set_flow_rate_button = tk.Button(
                pumps_frame,
                text="Set",
                width=5,
                command=lambda i=i: self.pump_set_flow_rate(i),
            )
            pump_set_flow_rate_button.grid(row=i + 1, column=5)

            # use pid or no
            data_types_checkbox = tk.Checkbutton(
                pumps_frame,
                text="PID",
                variable=self.pid_vars[i],
                command=lambda i=i: self.change_pid_onoff(i),
            )
            data_types_checkbox.grid(row=i + 1, column=6)

        pumps_frame.pack(anchor="nw", padx=15)

        self.pump_type_vars = [None for _ in self.pumps_list]
        self.pump_port_vars = [None for _ in self.pumps_list]
        self.balance_port_vars = [None for _ in self.pumps_list]

        ### --- VALVES --- ###
        valves_frame = tk.Frame(equipment_frame)
        tk.Label(
            equipment_frame, text="3-Way Valves", font=("Arial", 16, "underline")
        ).pack(anchor="nw", padx=15, pady=(10, 0))
        self.valves_list = [
            "Valve 1: Organic",
            "Valve 2: H₂SO₄",
            "Valve 3: Aminohydantoin"]

        self.valve_on_buttons = []
        self.valve_off_buttons = []
        for i, valve_name in enumerate(self.valves_list):
            # Valve names
            tk.Label(valves_frame, text=valve_name).grid(row=i, column=0, sticky="w")

            # On/Off buttons
            valve_on_button = tk.Button(
                valves_frame, text="Collection", width=10, command=lambda i=i: self.valve_onoff(i, True)
            )
            self.valve_on_buttons.append(valve_on_button)
            valve_off_button = tk.Button(
                valves_frame, text="Waste", width=10, command=lambda i=i: self.valve_onoff(i, False)
            )
            self.valve_off_buttons.append(valve_off_button)
            valve_on_button.grid(row=i, column=1, padx=15)
            valve_off_button.grid(row=i, column=2, padx=15)

        self.valve_address_vars = [None for _ in self.valves_list]
        valves_frame.pack(anchor="nw", padx=15)

        ### --- TEMPERATURES --- ###
        temps_frame = tk.Frame(equipment_frame)
        tk.Label(
            equipment_frame,
            text="Reactor Temperatures (°C)",
            font=("Arial", 16, "underline"),
        ).pack(anchor="nw", padx=15, pady=(10, 0))
        self.temps_list = [
            "HNO₃",
            "Furfural",
            "KOH",
            "2MeTHF",
            "H₂SO₄",
            "Aminohydantoin",
        ]
        self.temp_connect_var = tk.IntVar()
        self.temp_connect_var.set(0)  # Initial state: off
        self.temp_entry_vars = []
        self.temp_reg1_vars = [None for _ in self.temps_list]
        self.temp_reg2_vars = [None for _ in self.temps_list]

        self.temp_connect_button = tk.Button(
            temps_frame,
            text="Connect",
            font=("Arial", 12, "bold"),
            width=12,
            command=self.temp_connect,
        )
        self.temp_connect_button.grid(row=0, column=0)

        tk.Label(temps_frame, text="Temperature", font=("Arial", 12, "bold")).grid(
            row=0, column=3, sticky="nsew"
        )
        tk.Label(temps_frame, text="Set Temperature", font=("Arial", 12, "bold")).grid(
            row=0, column=4, sticky="nsew"
        )
        tk.Label(temps_frame, text="Current", font=("Arial", 12, "bold")).grid(
            row=0, column=5, sticky="nsew"
        )
        self.current_temp_labels = []

        for i, temp_name in enumerate(self.temps_list):
            # Temp names
            tk.Label(temps_frame, text=f"Reactor {i + 1}: {temp_name}").grid(
                row=i + 1, column=0, sticky="w"
            )

            # Entry for temperature
            self.temp_entry_var = tk.StringVar()
            temp_entry = tk.Entry(temps_frame, textvariable=self.temp_entry_var)
            temp_entry.grid(row=i + 1, column=3, padx=15)
            self.temp_entry_vars.append(self.temp_entry_var)
            temp_entry = tk.Button(
                temps_frame, text="Set", width=5, command=self.set_temp(i)
            )
            temp_entry.grid(row=i + 1, column=4, padx=15)
            current_temp_label = tk.Label(temps_frame, text=None, bg="white", width=10)
            current_temp_label.grid(row=i + 1, column=5, padx=15)
            self.current_temp_labels.append(current_temp_label)

        temps_frame.pack(anchor="nw", padx=15)

        ### --- LIQUID LEVELS --- ###
        liquid_frame = tk.Frame(equipment_frame)
        tk.Label(
            equipment_frame, text="Liquid Levels (mL)", font=("Arial", 16, "underline")
        ).pack(anchor="nw", padx=15, pady=(10, 0))

        self.org_var = tk.StringVar()
        self.org_var.set("0")
        self.aq_var = tk.StringVar()
        self.aq_var.set("0")

        tk.Label(liquid_frame, text="Organic: ").grid(row=0, column=0)
        tk.Entry(liquid_frame, textvariable=self.org_var).grid(row=0, column=1, pady=10)
        tk.Label(liquid_frame, text="Aqueous: ").grid(row=1, column=0)
        tk.Entry(liquid_frame, textvariable=self.aq_var).grid(row=1, column=1)

        liquid_frame.pack(anchor="nw", padx=15)

        ### --- STIRRER --- ###
        stirrer_frame = tk.Frame(equipment_frame)
        tk.Label(
            equipment_frame, text="Stirrer (rpm)", font=("Arial", 16, "underline")
        ).pack(anchor="nw", padx=15, pady=(10, 0))

        tk.Label(stirrer_frame, text="Stirrer 1").grid(row=0, column=0)

        self.stirrer_var = tk.StringVar()
        self.stirrer_var.set("0")
        stirrer_entry = tk.Entry(stirrer_frame, textvariable=self.stirrer_var)
        stirrer_entry.grid(row=0, column=1, padx=(15, 0), pady=10)

        stirrer_frame.pack(anchor="nw", padx=15)

        ### --- FAN --- ###
        self.fan_port_vars = [None]

        fan_frame = tk.Frame(equipment_frame)
        tk.Label(equipment_frame, text="Fan", font=("Arial", 16, "underline")).pack(
            anchor="nw", padx=15, pady=(10, 0)
        )
        tk.Label(fan_frame, text='Fan').grid(row=0,column=0, padx=(0,10))
        self.fan_on_button = tk.Button(fan_frame, text="On", width=7, command=self.fan_on)
        self.fan_on_button.grid(row=0,column=1,padx=(0,10))
        self.fan_off_button = tk.Button(fan_frame, text="Off", width=7, command=self.fan_off)
        self.fan_off_button.grid(row=0,column=2)

        fan_frame.pack(anchor="nw", padx=15)

        # Create the Enter button
        enter_button = tk.Button(
            self.root, text="Assign and Read Data", command=self.open_assign
        )
        enter_button.place(x=50, y=10)

        equipment_frame.grid(row=0, column=0, sticky="nw")

        ### --- DATA --- ###
        data_frame = tk.Frame(gui_frame)
        tk.Label(data_frame, text="Graph Data", font=("Arial", 16, "underline")).grid(
            row=0, column=0, pady=10, sticky="nw"
        )

        self.plot_temperatures = {
            "HNO₃": [False, False, []],
            "Furfural": [False, False, []],
            "KOH": [False, False, []],
            "2MeTHF": [False, False, []],
            "Aq-Org Separator": [False, False, []],
            "H₂SO₄": [False, False, []],
            "Aminohydantoin": [False, False, []],
        }
        self.plot_pressures = {
            "HNO₃": [False, False, []],
            "Furfural": [False, False, []],
            "KOH": [False, False, []],
            "H₂SO₄": [False, False, []],
            "Aminohydantoin": [False, False, []],
        }
        self.plot_balances = {
            "HNO₃": [False, False, []],
            "Acetic anhydride": [False, False, []],
            "Furfural": [False, False, []],
            "KOH": [False, False, []],
            "2MeTHF": [False, False, []],
            "Aqueous": [False, False, []],
            "H₂SO₄": [False, False, []],
            "Aminohydantoin": [False, False, []],
            "Crude NIFU Out": [False, False, []],
        }
        self.plot_flow_rates = {
            "HNO₃": [False, False, []],
            "Acetic anhydride": [False, False, []],
            "Reactor 1": [False, False, []],
            "Furfural": [False, False, []],
            "KOH": [False, False, []],
            "2MeTHF": [False, False, []],
            "H₂SO₄": [False, False, []],
            "Aminohydantoin": [False, False, []],
            "Crude NIFU Out": [False, False, []],
        }
        self.data_type_dict_objects = [
            self.plot_temperatures,
            self.plot_pressures,
            self.plot_balances,
            self.plot_flow_rates,
        ]

        self.g = graph(
            self.plot_temperatures,
            self.plot_pressures,
            self.plot_balances,
            self.plot_flow_rates,
        )
        self.temp_plc = temp("169.254.92.250", 502)
        self.temp_plc.set_graph_obj(self.g)
        self.valve_plc = valve_fan("169.254.92.250")
        self.fan_plc = valve_fan(NotImplementedError) # put host number here

        # Checkboxes for different data
        data_types_frame = tk.Frame(data_frame)
        self.data_types = ["Temperature", "Pressure", "Balance", "Flow_Rate"]
        self.data_types_vars = [tk.BooleanVar() for _ in self.data_types]
        for index, value in enumerate(self.data_types):
            data_types_checkbox = tk.Checkbutton(
                data_types_frame,
                text=value,
                variable=self.data_types_vars[index],
                command=lambda v=value: self.g.big_checkmark(v),
            )
            data_types_checkbox.grid(row=0, column=index)
            self.data_types_vars[index].trace_add("write", self.update_plot_checkboxes)
        data_types_frame.grid(row=1, column=0, sticky="w")

        # graph and graph buttons
        graph_frame = tk.Frame(data_frame)
        graph_frame.columnconfigure(0, weight=4)
        graph_frame.columnconfigure(1, weight=1)

        # graph_display
        self.graph_display_frame = tk.Frame(
            graph_frame, width=800, height=500, bg="white"
        )
        self.figure = Figure(figsize=(10, 7), dpi=100)
        plot1 = self.figure.add_subplot(221)
        plot2 = self.figure.add_subplot(222)
        plot3 = self.figure.add_subplot(223)
        plot4 = self.figure.add_subplot(224)

        plot1.set_title("Temperature Over Time")
        plot1.set_xlabel("Time (s)")
        plot1.set_ylabel("Temperature (°C)")

        plot2.set_title("Pressure Over Time")
        plot2.set_xlabel("Time (s)")
        plot2.set_ylabel("Pressure (psi)")

        plot3.set_title("Balance Over Time")
        plot3.set_xlabel("Time (s)")
        plot3.set_ylabel("Balance (g)")

        plot4.set_title("Flow Rate Over Time")
        plot4.set_xlabel("Time (s)")
        plot4.set_ylabel("Flow Rate (mL/min)")

        self.plots = [plot1, plot2, plot3, plot4]
        self.figure.tight_layout()
        self.canvas = FigureCanvasTkAgg(self.figure, master=self.graph_display_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack()

        # graph_buttons_table
        graph_buttons_table_frame = tk.Frame(graph_frame)

        # buttons
        self.start_button = tk.Button(
            graph_buttons_table_frame,
            text="Start",
            width=20,
            command=self.change_start_button,
        )
        self.start_button.grid(row=0, column=0)
        self.stop_button = tk.Button(
            graph_buttons_table_frame,
            text="Stop",
            width=20,
            activebackground="IndianRed1",
            command=self.change_stop_button,
        )
        self.stop_button.grid(row=1, column=0)
        self.start_excel_button = tk.Button(
            graph_buttons_table_frame,
            text="Start Reading Data",
            width=20,
            command=self.start_excel,
        )
        self.start_excel_button.grid(row=2, column=0)
        self.stop_excel_button = tk.Button(
            graph_buttons_table_frame,
            text="End Reading Data",
            width=20,
            activebackground="IndianRed1",
            command=self.stop_excel,
        )
        self.stop_excel_button.grid(row=3, column=0)

        # table
        tk.Text(graph_buttons_table_frame, width=30, height=23, bg="gray").grid(
            row=4, column=0, pady=(25, 0)
        )

        self.graph_display_frame.grid(row=0, column=0, sticky="N")
        graph_buttons_table_frame.grid(row=0, column=1, sticky="n", padx=20)
        graph_frame.grid(row=2, column=0, sticky="w")

        # Checkboxes for what to plot
        tk.Label(data_frame, text="Plot:", font=("Arial", 16, "underline")).grid(
            row=3, column=0, pady=10, sticky="nw"
        )
        self.plot_frame = tk.Frame(data_frame)

        # Temperature checkboxes
        self.plot_temperature_name = tk.Label(self.plot_frame, text="Temperature:")
        self.plot_temperature_name.grid(row=0, column=0, sticky="nw")
        self.plot_temperature_name.grid_remove()

        self.plot_temperatures_vars = [tk.BooleanVar() for _ in self.plot_temperatures]
        self.plot_temperatures_checkboxes = []
        self.plot_temperatures_frame = tk.Frame(self.plot_frame)

        for index, value in enumerate(self.plot_temperatures):
            plot_temperatures_checkbox = tk.Checkbutton(
                self.plot_temperatures_frame,
                text=value,
                variable=self.plot_temperatures_vars[index],
                command=lambda v=value: self.g.checkmark("Temperature", v),
            )
            self.plot_temperatures_checkboxes.append(plot_temperatures_checkbox)
            plot_temperatures_checkbox.grid(row=0, column=index, sticky="w")
            plot_temperatures_checkbox.grid_remove()

        self.plot_temperatures_frame.grid(row=0, column=1, sticky="w")

        # Pressure checkboxes
        self.plot_pressure_name = tk.Label(self.plot_frame, text="Pressure:")
        self.plot_pressure_name.grid(row=1, column=0, sticky="nw")
        self.plot_pressure_name.grid_remove()

        self.plot_pressures_vars = [tk.BooleanVar() for _ in self.plot_pressures]
        self.plot_pressures_checkboxes = []
        self.plot_pressures_frame = tk.Frame(self.plot_frame)

        for index, value in enumerate(self.plot_pressures):
            plot_pressures_checkbox = tk.Checkbutton(
                self.plot_pressures_frame,
                text=value,
                variable=self.plot_pressures_vars[index],
                command=lambda v=value: self.g.checkmark("Pressure", v),
            )
            self.plot_pressures_checkboxes.append(plot_pressures_checkbox)
            plot_pressures_checkbox.grid(row=0, column=index, sticky="w")
            plot_pressures_checkbox.grid_remove()

        self.plot_pressures_frame.grid(row=1, column=1, sticky="w")

        # Balance checkboxes
        self.plot_balance_name = tk.Label(self.plot_frame, text="Balance:")
        self.plot_balance_name.grid(row=2, column=0, sticky="nw")
        self.plot_balance_name.grid_remove()

        self.plot_balances_vars = [tk.BooleanVar() for _ in self.plot_balances]
        self.plot_balances_checkboxes = []
        self.plot_balances_frame = tk.Frame(self.plot_frame)

        for index, value in enumerate(self.plot_balances):
            plot_balances_checkbox = tk.Checkbutton(
                self.plot_balances_frame,
                text=value,
                variable=self.plot_balances_vars[index],
                command=lambda v=value: self.g.checkmark("Balance", v),
            )
            self.plot_balances_checkboxes.append(plot_balances_checkbox)
            plot_balances_checkbox.grid(row=0, column=index, sticky="w")
            plot_balances_checkbox.grid_remove()

        self.plot_balances_frame.grid(row=2, column=1, sticky="w")

        # Flow rate checkboxes
        self.plot_flowrate_name = tk.Label(self.plot_frame, text="Flow Rate:")
        self.plot_flowrate_name.grid(row=3, column=0, sticky="nw")
        self.plot_flowrate_name.grid_remove()

        self.plot_flow_rates_vars = [tk.BooleanVar() for _ in self.plot_flow_rates]
        self.plot_flow_rates_checkboxes = []
        self.plot_flow_rates_frame = tk.Frame(self.plot_frame)

        for index, value in enumerate(self.plot_flow_rates):
            plot_flow_rates_checkbox = tk.Checkbutton(
                self.plot_flow_rates_frame,
                text=value,
                variable=self.plot_flow_rates_vars[index],
                command=lambda v=value: self.g.checkmark("Flow_Rate", v),
            )
            self.plot_flow_rates_checkboxes.append(plot_flow_rates_checkbox)
            plot_flow_rates_checkbox.grid(row=0, column=index, sticky="w")
            plot_flow_rates_checkbox.grid_remove()

        self.plot_flow_rates_frame.grid(row=3, column=1, sticky="w")

        self.plot_frame.grid(row=4, column=0, sticky="w")
        data_frame.grid(row=0, column=1, sticky="nw")

        gui_frame.pack()

        tk.Button(self.root, text="TEST", command=self.test).place(x=10, y=10)
        self.root.bind(
            "<KeyPress>", self.exit_shortcut
        )  # press escape button on keyboard to close the GUI
        self.root.mainloop()

    # equipment functions

    # pumps
    def pump_connect(self, pump_index):
        if not self.pump_connect_vars[pump_index]:  # If not connected
            self.pump_connect_vars[pump_index] = True
            self.pump_connect_buttons[pump_index].config(
                bg="LightSkyBlue1", text="Connected"
            )  # Change to blue color

            p_ser = Pump.pump_connect(self, self.pump_port_vars[pump_index].get())
            self.pump_sers[pump_index] = p_ser

            b_ser = Balance.balance_connect(
                self, self.balance_port_vars[pump_index].get()
            )
            self.balance_sers[pump_index] = b_ser

            c = pid_control(
                b_ser,
                p_ser,
                self.pump_type_vars[pump_index].get().upper(),
                self.pumps_list[pump_index],
                self.g,
            )
            self.pump_pid_classes[pump_index] = c
            c.set_excel_obj(self.excel_obj)

        else:  # If already connected
            self.pump_connect_vars[pump_index] = False
            self.pump_connect_buttons[pump_index].config(
                bg="SystemButtonFace", text="Disconnected"
            )  # Change back to default color

            p_ser = self.pump_sers[pump_index]
            Pump.pump_disconnect(self, p_ser)

            b_ser = self.balance_sers[pump_index]
            Balance.balance_disconnect(self, b_ser)

    def pump_on(self, pump_index):
        self.pump_on_buttons[pump_index].config(bg="pale green")
        self.pump_off_buttons[pump_index].config(bg="SystemButtonFace")

        if self.pump_connect_vars[pump_index]:  # if connected
            pump_type = self.pump_type_vars[pump_index].get().upper()
            ser = self.pump_sers[pump_index]

            if pump_type == "ELDEX":
                Pump.eldex_pump_command(self, ser, command="RU")
            elif pump_type == "UI-22":
                Pump.UI22_pump_command(self, ser, command="G1", value="1")

            c = self.pump_pid_classes[pump_index]
            if c:
                c.set_stop(False)

    def pump_off(
        self, pump_index
    ):  # turning off requires set flow rate to be set again
        self.pump_off_buttons[pump_index].config(bg="IndianRed1")
        self.pump_on_buttons[pump_index].config(bg="SystemButtonFace")

        if self.pump_connect_vars[pump_index]:  # if connected
            pump_type = self.pump_type_vars[pump_index].get().upper()

            c = self.pump_pid_classes[pump_index]
            if c:
                c.set_stop(True)

            ser = self.pump_sers[pump_index]
            if pump_type == "ELDEX":
                Pump.eldex_pump_command(self, ser, command="ST")
            elif pump_type == "UI-22":
                Pump.UI22_pump_command(self, ser, command="G1", value="0")

    def pump_set_flow_rate(self, index):
        if self.pump_connect_vars[index]:  # if connected, assumes pump is on
            flow_rate = float(self.pump_flow_entry_vars[index].get())
            flow_rate = f"{flow_rate:06.3f}"
            pump_type = self.pump_type_vars[index].get().upper()
            p_ser = self.pump_sers[index]
            pump_controller = pump_controllers[index]
            pump_controller["set_point"] = float(flow_rate)

            # figure out excel writing
            if pump_type == "ELDEX":
                Pump.eldex_pump_command(self, p_ser, command="SF", value=flow_rate)
            elif pump_type == "UI-22":
                flow_rate = flow_rate.replace(".", "")
                Pump.UI22_pump_command(self, p_ser, command="S3", value=flow_rate)

            c = self.pump_pid_classes[index]
            c.set_controller_and_matrix(pump_controller, matrix_lengths[index])
            c.set_stop(False)

            if not self.pump_pid_threads_started[index]:
                t_pid = threading.Thread(target=c.start)
                t_pid.daemon = True
                t_pid.start()

                self.pump_pid_threads_started[index] = True

    def change_pid_onoff(self, i):
        c = self.pump_pid_classes[i]
        if c:
            c.pid_onoff(self.pid_vars[i].get())
            if not self.pid_vars[i].get():
                print("PID control off")
    
    def valve_onoff(self, i, boolean):
        if boolean:
            self.valve_on_buttons[i].config(bg="LightSkyBlue1")
            self.valve_off_buttons[i].config(bg="SystemButtonFace")
            self.valve_plc.write_onoff(address_num=self.valve_address_vars[i], boolean=True)

        else:
            self.valve_off_buttons[i].config(bg="LightSkyBlue1")
            self.valve_on_buttons[i].config(bg="SystemButtonFace")
            self.valve_plc.write_onoff(address_num=self.valve_address_vars[i], boolean=False)

    def temp_connect(self):
        if self.temp_connect_var.get() == 0:  # if not connected, connect
            self.temp_connect_button.config(bg="pale green", text="Connected")
            self.temp_connect_var.set(1)
            self.temp_plc.connect()
            self.temp_plc.reading_onoff(True)
            self.read_temps()
        else:
            self.temp_connect_var.set(0)
            self.temp_connect_button.config(bg="SystemButtonFace", text="Connect")
            self.temp_plc.reading_onoff(False)
            self.temp_plc.disconnect()

    def set_temp(self, index):
        if self.temp_connect_var.get() == 1:
            temp_data = float(self.temp_entry_vars[index].get())
            reg1, reg2 = self.temp_reg1_vars[index], self.temp_reg1_vars[index]
            self.temp_plc.write_temp(temp_data, reg1, reg2)

    def read_temps(self):
        for index, label in enumerate(self.current_temp_labels):
            reg1 = self.temp_reg1_vars[index]
            reg2 = self.temp_reg2_vars[index]
            if reg1:
                t = None
                reg1 = reg1.get()
                reg2 = reg2.get()
                if reg1 != 0 and reg2 != 0:
                    t = threading.Thread(
                        target=self.temp_plc.read_temp,
                        args=(self.temps_list[index], label, reg1, reg2),
                    )
                elif reg1 != 0:
                    t = threading.Thread(
                        target=self.temp_plc.read_temp,
                        args=(self.temps_list[index], label, reg1),
                    )
                if t:
                    t.daemon = True
                    t.start()
    
    def fan_on(self):
        self.fan_on_button.config(bg="pale green")
        self.fan_off_button.config(bg="SystemButtonFace")
        self.fan_plc.connect()
        self.fan_plc.write_onoff(address_num=self.fan_port_vars[0], boolean=True)
    
    def fan_off(self):
        self.fan_off_button.config(bg="IndianRed1")
        self.fan_on_button.config(bg="SystemButtonFace")
        self.fan_plc.write_onoff(address_num=self.fan_port_vars[0], boolean=False)
        self.fan_plc.disconnect()

    def open_assign(self):
        """
        Assigns a pump type and port number to each pump, and has commands to read data
        Outputs a list for pump type, pump port numbers, and balance port numbers, in the order that corresponds with self.pumps_list
        """

        self.assign_page = tk.Toplevel(self.root)
        # pumps and balance
        tk.Label(
            self.assign_page, text="Assign Pump Types and Ports", font=("Arial", 14)
        ).pack(pady=10)
        pump_frame = tk.Frame(self.assign_page)

        tk.Label(
            pump_frame, text="Pump Name", font=("TkDefaultFont", 9, "underline")
        ).grid(row=0, column=0)
        tk.Label(
            pump_frame, text="Pump Type", font=("TkDefaultFont", 9, "underline")
        ).grid(row=0, column=1)
        tk.Label(
            pump_frame, text="Pump Port Number", font=("TkDefaultFont", 9, "underline")
        ).grid(row=0, column=2)
        tk.Label(
            pump_frame,
            text="Balance Port Number",
            font=("TkDefaultFont", 9, "underline"),
        ).grid(row=0, column=3)

        for i, name in enumerate(self.pumps_list):
            tk.Label(pump_frame, text=name).grid(row=i + 1, column=0, padx=5)

            self.pump_type_var = tk.StringVar()
            if self.pump_type_vars[
                i
            ]:  # populate assign page with previously assigned values
                self.pump_type_var.set(self.pump_type_vars[i].get())
            pump_type_entry = tk.Entry(pump_frame, textvariable=self.pump_type_var)
            pump_type_entry.grid(row=i + 1, column=1, padx=5)
            self.pump_type_vars[i] = self.pump_type_var

            self.pump_port_var = tk.IntVar()
            if self.pump_port_vars[i]:
                self.pump_port_var.set(self.pump_port_vars[i].get())
            pump_port_entry = tk.Entry(pump_frame, textvariable=self.pump_port_var)
            pump_port_entry.grid(row=i + 1, column=2, padx=5)
            self.pump_port_vars[i] = self.pump_port_var

            # balances
            self.balance_port_var = tk.IntVar()
            if self.balance_port_vars[i]:
                self.balance_port_var.set(self.balance_port_vars[i].get())
            balance_port_entry = tk.Entry(
                pump_frame, textvariable=self.balance_port_var
            )
            balance_port_entry.grid(row=i + 1, column=3, padx=5)
            self.balance_port_vars[i] = self.balance_port_var

        pump_frame.pack(pady=10)

        # Valve registers
        valve_frame = tk.Frame(self.assign_page)
        tk.Label(
            valve_frame, text="Valve Name", font=("TkDefaultFont", 9, "underline")
        ).grid(row=0, column=0)
        tk.Label(
            valve_frame, text="Address", font=("TkDefaultFont", 9, "underline")
        ).grid(row=0, column=1)

        for i, valve_name in enumerate(self.valves_list):
            tk.Label(valve_frame, text=valve_name).grid(row=i + 1, column=0, padx=5)

            valve_address_var = tk.IntVar()
            if self.valve_address_vars[i]:
                valve_address_var.set(self.valve_address_vars[i].get())
            valve_var_reg_entry = tk.Entry(valve_frame, textvariable=valve_address_var)
            valve_var_reg_entry.grid(row=i + 1, column=1, padx=5)
            self.valve_address_vars[i] = valve_address_var

        valve_frame.pack(pady=10)

        # temperature registers
        temp_frame = tk.Frame(self.assign_page)
        tk.Label(
            temp_frame, text="Temperature Name", font=("TkDefaultFont", 9, "underline")
        ).grid(row=0, column=0)
        tk.Label(
            temp_frame, text="Register 1", font=("TkDefaultFont", 9, "underline")
        ).grid(row=0, column=1)
        tk.Label(
            temp_frame, text="Register 2", font=("TkDefaultFont", 9, "underline")
        ).grid(row=0, column=2)

        for i, temp_name in enumerate(self.temps_list):
            tk.Label(temp_frame, text=temp_name).grid(row=i + 1, column=0, padx=5)

            temp_reg1_var = tk.IntVar()
            temp_reg2_var = tk.IntVar()
            if self.temp_reg1_vars[i]:
                temp_reg1_var.set(self.temp_reg1_vars[i].get())
            if self.temp_reg2_vars[i]:
                temp_reg2_var.set(self.temp_reg2_vars[i].get())
            temp_var_reg1_entry = tk.Entry(temp_frame, textvariable=temp_reg1_var)
            temp_var_reg2_entry = tk.Entry(temp_frame, textvariable=temp_reg2_var)
            temp_var_reg1_entry.grid(row=i + 1, column=1, padx=5)
            temp_var_reg2_entry.grid(row=i + 1, column=2, padx=5)
            self.temp_reg1_vars[i] = temp_reg1_var
            self.temp_reg2_vars[i] = temp_reg2_var

        temp_frame.pack(pady=10)

        # fan
        fan_frame = tk.Frame(self.assign_page)
        self.fan_port_var = tk.IntVar()
        if self.fan_port_vars[0]:
            self.fan_port_var.set(self.fan_port_vars[0].get())
        fan_port_entry = tk.Entry(
            fan_frame, textvariable=self.fan_port_var
        )
        tk.Label(
            fan_frame, text="Fan", font=("TkDefaultFont", 9, "underline")
        ).grid(row=0, column=0)
        tk.Label(
            fan_frame, text="Address", font=("TkDefaultFont", 9, "underline")
        ).grid(row=0, column=1)
        tk.Label(fan_frame, text='Fan').grid(row=1, column=0, padx=10)
        fan_port_entry.grid(row=1, column=1, padx=10)
        self.fan_port_vars[0] = self.fan_port_var
        fan_frame.pack()

    # graph data functions
    def change_start_button(self):
        self.start_button.config(background="pale green")
        self.stop_button.config(background="SystemButtonFace")
        self.g.gui_plot_stop(False)
        t = threading.Thread(target=self.g.plot, args=(self.plots, self.canvas))
        t.daemon = True
        t.start()

    def change_stop_button(self):
        self.start_button.config(background="SystemButtonFace")
        self.g.gui_plot_stop(True)

    def start_excel(self):
        self.start_excel_button.config(background="pale green")
        self.stop_excel_button.config(background="SystemButtonFace")

        print("Writing data into excel file...")
        self.excel_obj = excel_file(self.pumps_list, pump_controllers, matrix_lengths)
        for c in self.pump_pid_classes:
            if c:
                c.set_excel_obj(self.excel_obj)
        t_excel = threading.Thread(target=self.excel_obj.start_file)
        t_excel.daemon = True
        t_excel.start()

    def stop_excel(self):
        self.start_excel_button.config(background="SystemButtonFace")

        print("Stopping excel file...")
        self.excel_obj.stop_file()

    def update_plot_checkboxes(self, *args):
        frames = [
            (
                self.plot_temperature_name,
                self.plot_temperatures_checkboxes,
                self.plot_temperatures_frame,
            ),
            (
                self.plot_pressure_name,
                self.plot_pressures_checkboxes,
                self.plot_pressures_frame,
            ),
            (
                self.plot_balance_name,
                self.plot_balances_checkboxes,
                self.plot_balances_frame,
            ),
            (
                self.plot_flowrate_name,
                self.plot_flow_rates_checkboxes,
                self.plot_flow_rates_frame,
            ),
        ]

        row = 0
        for i, var in enumerate(self.data_types_vars):
            name, checkboxes, frame = frames[i]
            if var.get():
                name.grid(row=row, column=0, sticky="nw")
                frame.grid(row=row, column=1, sticky="w")
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
        # self.plc.connect()
        # print('connected')
        print("here")
        reg1 = 28730
        reg2 = 28731
        self.temp_plc.connect()
        self.temp_plc.reading_onoff(True)
        t = threading.Thread(
            target=self.temp_plc.read_temp,
            args=(None, self.current_temp_labels[0], reg1, reg2),
        )
        t.daemon = True
        t.start()

        pass

gui = NIFU_Synthesis()
