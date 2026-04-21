import tkinter as tk
from tkinter import ttk, messagebox
import tkintermapview
import requests
import random

class RouteFindingSystem:
    def __init__(self, root):
        self.root = root
        self.root.title("AI Route-Finding Production System")
        self.root.geometry("1200x850")
        self.root.configure(bg="#1e1e1e")

        self.start_coord = None
        self.end_coord = None
        self.path_line = None
        self.env_markers = []

        self.setup_ui()

    def setup_ui(self):
        # Sidebar for Controls
        self.sidebar = tk.Frame(self.root, width=350, bg="#2d2d2d", padx=20, pady=20)
        self.sidebar.pack(side="left", fill="y")

        self.map_frame = tk.Frame(self.root, bg="#1e1e1e")
        self.map_frame.pack(side="right", fill="both", expand=True)

        # Header
        tk.Label(self.sidebar, text="ADVANCED ROUTE AGENT", font=("Helvetica", 16, "bold"), bg="#2d2d2d", fg="#3498db").pack(pady=(0, 20))

        # --- AGENT SELECTION ---
        tk.Label(self.sidebar, text="AGENT TYPE", font=("Helvetica", 10, "bold"), bg="#2d2d2d", fg="#aaaaaa").pack(anchor="w")
        self.agent_var = tk.StringVar(value="utility")
        style = ttk.Style()
        style.configure("TRadiobutton", background="#2d2d2d", foreground="white")
        
        rb_frame = tk.Frame(self.sidebar, bg="#2d2d2d")
        rb_frame.pack(fill="x", pady=5)
        tk.Radiobutton(rb_frame, text="Goal-Based (Reach Target)", variable=self.agent_var, value="goal", bg="#2d2d2d", fg="white", selectcolor="#3498db", activebackground="#2d2d2d").pack(side="left")
        tk.Radiobutton(rb_frame, text="Utility-Based (Optimize)", variable=self.agent_var, value="utility", bg="#2d2d2d", fg="white", selectcolor="#2ecc71", activebackground="#2d2d2d").pack(side="left", padx=10)

        # --- UTILITY WEIGHTS (Only for Utility Agent) ---
        tk.Label(self.sidebar, text="UTILITY WEIGHTS (0-10)", font=("Helvetica", 10, "bold"), bg="#2d2d2d", fg="#aaaaaa").pack(anchor="w", pady=(15, 5))
        
        self.time_weight = tk.Scale(self.sidebar, from_=0, to=10, orient="horizontal", label="Time Efficiency", bg="#2d2d2d", fg="white", highlightthickness=0)
        self.time_weight.set(8)
        self.time_weight.pack(fill="x")

        self.cost_weight = tk.Scale(self.sidebar, from_=0, to=10, orient="horizontal", label="Fuel/Cost Saving", bg="#2d2d2d", fg="white", highlightthickness=0)
        self.cost_weight.set(3)
        self.cost_weight.pack(fill="x")

        # --- ENVIRONMENT SIMULATOR ---
        tk.Label(self.sidebar, text="ENVIRONMENT OVERRIDE", font=("Helvetica", 10, "bold"), bg="#2d2d2d", fg="#aaaaaa").pack(anchor="w", pady=(15, 5))
        self.traffic_var = tk.BooleanVar(value=True)
        tk.Checkbutton(self.sidebar, text="Simulate Heavy Traffic", variable=self.traffic_var, bg="#2d2d2d", fg="white", selectcolor="#1e1e1e").pack(anchor="w")
        
        self.btn_env = tk.Button(self.sidebar, text="GENERATE CONSTRUCTION ZONES", command=self.simulate_environment, bg="#e67e22", fg="white", relief="flat", pady=5)
        self.btn_env.pack(fill="x", pady=10)

        # --- ACTION ---
        self.btn_run = tk.Button(self.sidebar, text="EXECUTE AGENT", command=self.execute_agent, bg="#3498db", fg="white", font=("Helvetica", 11, "bold"), height=2, relief="flat")
        self.btn_run.pack(fill="x", pady=20)

        self.output_box = tk.Text(self.sidebar, height=8, bg="#1e1e1e", fg="#2ecc71", font=("Consolas", 9), padx=5, pady=5)
        self.output_box.pack(fill="x")

        # Map View
        self.map_widget = tkintermapview.TkinterMapView(self.map_frame, corner_radius=0)
        self.map_widget.pack(fill="both", expand=True)
        self.map_widget.set_position(19.0760, 72.8777) # Default Mumbai
        self.map_widget.set_zoom(12)
        
        self.map_widget.add_right_click_menu_command(label="Set Start", command=self.set_start, pass_coords=True)
        self.map_widget.add_right_click_menu_command(label="Set End", command=self.set_end, pass_coords=True)

    def set_start(self, coords):
        self.start_coord = coords
        self.map_widget.set_marker(coords[0], coords[1], text="START", marker_color_circle="white", marker_color_outside="#3498db")
        self.log(f"Point A Locked: {coords}")

    def set_end(self, coords):
        self.end_coord = coords
        self.map_widget.set_marker(coords[0], coords[1], text="GOAL", marker_color_circle="white", marker_color_outside="#e74c3c")
        self.log(f"Point B Locked: {coords}")

    def simulate_environment(self):
        # Clear old env
        for m in self.env_markers: m.delete()
        self.env_markers = []
        
        if not self.start_coord:
            messagebox.showinfo("Hint", "Set a start point first to generate local obstacles.")
            return

        for _ in range(3):
            lat = self.start_coord[0] + random.uniform(-0.02, 0.02)
            lon = self.start_coord[1] + random.uniform(-0.02, 0.02)
            marker = self.map_widget.set_marker(lat, lon, text="CONSTRUCTION", marker_color_outside="orange")
            self.env_markers.append(marker)
        self.log("Perceived Environment: 3 Construction Zones detected.")

    def log(self, msg):
        self.output_box.insert(tk.END, f"● {msg}\n")
        self.output_box.see(tk.END)

    def animate_path(self, coords):
        """Simulates an agent 'traversing' the path with a moving marker"""
        if self.path_line: self.path_line.delete()
        self.path_line = self.map_widget.set_path(coords, color="#3498db", width=5)
        
        # Animation placeholder (In production, you'd use a loop with self.root.after)
        self.log("Visualizing optimal trajectory...")

    def execute_agent(self):
        if not self.start_coord or not self.end_coord:
            messagebox.showwarning("Incomplete", "Agent requires Start and Goal coordinates.")
            return

        agent = self.agent_var.get()
        self.log(f"Activating {agent.upper()} Agent...")

        try:
            # OSRM API call
            url = f"http://router.project-osrm.org/route/v1/driving/{self.start_coord[1]},{self.start_coord[0]};{self.end_coord[1]},{self.end_coord[0]}?overview=full&geometries=geojson"
            
            # Logic: Utility agent considers 'Alternatives' to find the best utility
            if agent == "utility":
                url += "&alternatives=true"

            res = requests.get(url).json()

            if res.get("code") == "Ok":
                # Perceiving Environment
                traffic_penalty = 1.5 if self.traffic_var.get() else 1.0
                
                # Selecting Route based on Agent Logic
                if agent == "utility":
                    # Utility = (Time * Weight) + (Distance * Weight)
                    # We pick the route with the lowest "Cost" score
                    best_route = min(res['routes'], key=lambda x: (x['duration'] * self.time_weight.get() * traffic_penalty) + (x['distance'] * self.cost_weight.get()))
                    self.log(f"Utility Score Calculated: Balanced for {self.time_weight.get()} priority.")
                else:
                    # Goal based just takes the first valid path it finds
                    best_route = res['routes'][0]
                    self.log("Goal-Based: Path found. Environment nuances ignored.")

                path_coords = [(p[1], p[0]) for p in best_route['geometry']['coordinates']]
                self.animate_path(path_coords)
                
                dist = best_route['distance'] / 1000
                time = (best_route['duration'] / 60) * traffic_penalty
                self.log(f"Result: {dist:.2f}km | Est. Time: {time:.1f} min")
                
            else:
                self.log("Agent Error: No path in current environment.")
        except Exception as e:
            self.log(f"System Failure: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = RouteFindingSystem(root)
    root.mainloop()