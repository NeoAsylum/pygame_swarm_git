import matplotlib
matplotlib.use('Qt5Agg') # Ensure this is before pyplot import if needed
from matplotlib import pyplot as plt

class GamePlotter:
    def __init__(self, initial_is_showing=False):
        self.fig = None
        self.ax = None
        self.plot_lines = {}
        self.is_graph_showing = initial_is_showing
        self.graph_data_keys = ["AvgCohesion", "AvgAlignment", "AvgSeparation", "AvgAvoidance", "AvgFoodAttraction","AvgAvoidanceDistance"]
        self.colors = ["blue", "green", "red", "purple", "orange", "brown"]

        if self.is_graph_showing:
            self.open_graph_window([], {key: [] for key in self.graph_data_keys}) # Pass empty initial data

    def open_graph_window(self, time_steps, data_series_map):
        if self.fig is not None:
            try:
                plt.close(self.fig)
            except Exception:
                pass 
        plt.ion() # Interactive mode on
        self.fig, self.ax = plt.subplots(figsize=(10, 6))
        self.plot_lines = {}

        self.ax.set_xlabel("Data Point Index")
        self.ax.set_ylabel("Average Strength")
        self.ax.set_title("Flocking Behavior Statistics (In-Memory)")
        self.ax.grid(True)

        for i, label_text in enumerate(self.graph_data_keys):
            self.plot_lines[label_text], = self.ax.plot([], [], label=label_text, color=self.colors[i])
        self.ax.legend(loc="upper left")

        self.redraw_all_graph_data(time_steps, data_series_map) # Plot existing data

        plt.show(block=False)
        self.is_graph_showing = True
        self.fig.canvas.manager.set_window_title("Flocking Stats Plot (Memory)")


    def redraw_all_graph_data(self, time_steps, data_series_map):
        if not self.is_graph_showing or self.fig is None or self.ax is None:
            return

        max_points_to_show = 200
        current_len_hist = len(time_steps)
        start_index_hist = max(0, current_len_hist - max_points_to_show)
        display_time_steps_hist = time_steps[start_index_hist:]

        for label_text, line_obj in self.plot_lines.items():
            if label_text in data_series_map:
                display_data_hist = data_series_map[label_text][start_index_hist:]
                line_obj.set_data(display_time_steps_hist, display_data_hist)
            else:
                line_obj.set_data([], [])

        self.ax.relim()
        self.ax.autoscale_view(True, True, True)
        try:
            self.fig.canvas.draw_idle()
            self.fig.canvas.flush_events()
        except Exception as e:
            print(f"Error redrawing all graph data: {e}")
            self.close_graph_window()

    def close_graph_window(self):
        if self.fig is not None:
            try:
                plt.close(self.fig)
            except Exception as e:
                print(f"Error closing fig: {e}")
        self.fig = None
        self.ax = None
        self.plot_lines = {}
        self.is_graph_showing = False

    def toggle_graph_window(self, time_steps, data_series_map):
        if self.is_graph_showing and self.fig is not None:
            self.close_graph_window()
        else:
            self.open_graph_window(time_steps, data_series_map)

    def update_plot_with_new_data(self, time_steps, data_series_map):
        if not self.is_graph_showing or self.fig is None or not hasattr(self.fig.canvas.manager, 'window') or not self.fig.canvas.manager.window:
            # Added check for window existence, as it can be None if closed by user
            if self.is_graph_showing and self.fig and (not hasattr(self.fig.canvas.manager, 'window') or not self.fig.canvas.manager.window):
                self.is_graph_showing = False # Mark as not showing if user closed it
            return

        max_points_to_show = 200
        current_len = len(time_steps)
        start_index = max(0, current_len - max_points_to_show)

        display_time_steps = time_steps[start_index:]
        for label, line_obj in self.plot_lines.items():
            if label in data_series_map:
                display_data = data_series_map[label][start_index:]
                line_obj.set_data(display_time_steps, display_data)

        self.ax.relim()
        self.ax.autoscale_view(True, True, True)
        try:
            self.fig.canvas.draw_idle()
            self.fig.canvas.flush_events()
        except Exception as e:
            print(f"Error updating plot: {e}")
            self.close_graph_window() # Close if there's an error (e.g., window closed)
