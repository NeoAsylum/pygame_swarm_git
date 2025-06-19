import threading
import queue

import matplotlib
import matplotlib.pyplot as plt

matplotlib.use("Qt5Agg")


class GamePlotter:
    """
    Manages the Matplotlib graph window for displaying game statistics.

    Handles opening, closing, updating, and threading for the plot window
    to avoid blocking the main game loop.
    """

    def __init__(self):
        self.fig = None
        self.ax = None
        self.plot_lines = {}
        self.is_graph_showing = False  # Start with graph off by default
        self.graph_data_keys = [
            "AvgCohesion",
            "AvgAlignment",
            "AvgSeparation",
            "AvgAvoidance",
            "AvgFoodAttraction",
            "AvgAvoidanceDistance",
        ]
        self.colors = ["blue", "green", "red", "purple", "orange", "brown"]
        self.plot_data_queue = queue.Queue(maxsize=5)  # Limit queue size
        self.plot_thread = None
        self.stop_event = threading.Event()
        self.graph_lock = threading.Lock()  # For protecting Matplotlib objects
        self.initial_data_to_plot = None

        if self.is_graph_showing:
            self.open_graph_window([], {key: [] for key in self.graph_data_keys})

    def open_graph_window(self, time_steps, data_series_map):
        """
        Opens or activates the Matplotlib graph window.

        Args:
            time_steps (list): List of time steps (x-axis data).
            data_series_map (dict): Dictionary mapping data series labels to lists of values (y-axis data).
        """
        with self.graph_lock:
            if (
                self.is_graph_showing and self.fig
            ):  # If already showing, try to activate
                try:
                    if (
                        self.fig.canvas.manager is not None
                        and hasattr(self.fig.canvas.manager, "window")
                        and self.fig.canvas.manager.window  # type: ignore[attr-defined]
                    ):
                        self.fig.canvas.manager.window.activateWindow()  # type: ignore[attr-defined]
                        self.fig.canvas.manager.window.raise_()  # type: ignore[attr-defined]
                except AttributeError:
                    pass  # Continue if activation fails (e.g. no window manager)
                return

            plt.ion()  # Ensure interactive mode is on
            self.fig, self.ax = plt.subplots(figsize=(10, 6))
            self.plot_lines = {}

            self.ax.set_xlabel("Data Point Index")
            self.ax.set_ylabel("Average Attribute Strength")
            self.ax.set_title("Flocking Behavior Statistics Over Time")
            self.ax.grid(True)

            for i, label_text in enumerate(self.graph_data_keys):
                (self.plot_lines[label_text],) = self.ax.plot(
                    [], [], label=label_text, color=self.colors[i]
                )
            self.ax.legend(loc="upper left")
            self.is_graph_showing = True  # Set state before starting thread
            self.initial_data_to_plot = (time_steps, data_series_map)

        if self.plot_thread is None or not self.plot_thread.is_alive():
            self.stop_event.clear()
            self.plot_thread = threading.Thread(
                target=self._plotting_worker, daemon=True
            )
            self.plot_thread.start()

        if self.initial_data_to_plot:  # Send initial data to the worker
            self.queue_new_plot_data(*self.initial_data_to_plot)
            self.initial_data_to_plot = None

        plt.show(block=False)  # This often needs to be on the main thread
        with self.graph_lock:
            if self.fig and self.fig.canvas.manager is not None:
                self.fig.canvas.manager.set_window_title("Flocking Stats Plot")
            if self.fig:
                self.fig.canvas.draw_idle()
                self.fig.canvas.flush_events()

    def redraw_all_graph_data(self, time_steps, data_series_map):
        """
        Updates the data displayed on the graph and redraws it.

        Args:
            time_steps (list): List of time steps (x-axis data).
            data_series_map (dict): Dictionary mapping data series labels to lists of values (y-axis data).
        """
        with self.graph_lock:  # Ensure thread-safe access to Matplotlib objects
            if not self.fig or not self.ax or not self.is_graph_showing:
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
            self.fig.canvas.draw_idle()  # Request a redraw

    def close_graph_window(self):
        """
        Closes the Matplotlib graph window and stops the plotting thread.
        """
        self.stop_event.set()  # Signal the worker thread to stop
        if self.plot_thread and self.plot_thread.is_alive():
            try:
                self.plot_data_queue.put_nowait(None)  # Sentinel to unblock queue.get
            except queue.Full:
                pass  # If full, thread will see stop_event eventually
            self.plot_thread.join(timeout=1.0)  # Wait for the thread to finish
            self.plot_thread = None

        with self.graph_lock:  # Protect Matplotlib objects
            if self.fig:
                try:
                    plt.close(self.fig)  # Close the Matplotlib figure
                except (AttributeError, TypeError):
                    # These errors can occur if self.fig is None,
                    # not a valid Figure object, or if its internal
                    # state is such that plt.close() cannot operate
                    # on it (e.g., accessing a non-existent attribute).
                    # This covers some "already closed or in a bad state" scenarios.
                    pass  # Ignore such errors
            self.fig = None
            self.ax = None
            self.plot_lines = {}
            self.is_graph_showing = False

        # Clear any remaining items in the queue
        while not self.plot_data_queue.empty():
            try:
                self.plot_data_queue.get_nowait()
            except queue.Empty:
                pass

    def is_window_alive(self):
        """
        Checks if the graph window is currently open and responsive.

        Returns:
            bool: True if the window is alive, False otherwise.
        """
        with self.graph_lock:  # Ensure thread-safe check
            return bool(
                self.fig
                and self.is_graph_showing
                and plt.fignum_exists(self.fig.number)
            )

    def toggle_graph_window(self, time_steps, data_series_map):
        """
        Toggles the visibility of the graph window (opens if closed, closes if open).

        Args: time_steps (list): List of time steps (x-axis data). data_series_map (dict): Dictionary mapping data series labels to lists of values (y-axis data).
        """
        if self.is_graph_showing and self.fig is not None:
            self.close_graph_window()
        elif not self.is_graph_showing:
            self.open_graph_window(time_steps, data_series_map)

    def queue_new_plot_data(self, time_steps, data_series_map):
        """
        Queues new data to be plotted by the worker thread.

        Args:
            time_steps (list): List of time steps (x-axis data).
            data_series_map (dict): Dictionary mapping data series labels to lists of values (y-axis data).
        """

        if self.is_graph_showing and (self.plot_thread and self.plot_thread.is_alive()):
            try:
                # Create copies of data to avoid modification by main thread while in queue
                data_to_queue = (
                    list(time_steps),
                    {k: list(v) for k, v in data_series_map.items()},
                )
                self.plot_data_queue.put_nowait(data_to_queue)
            except queue.Full:
                # Optionally log that the queue is full and data is being skipped
                pass  # Don't block the main game thread

    def _plotting_worker(self):
        """Worker thread function to handle Matplotlib plotting."""
        while not self.stop_event.is_set():
            try:
                plot_job = self.plot_data_queue.get(timeout=0.1)
                if plot_job is None:
                    break

                time_steps, data_series_map = plot_job
                self.redraw_all_graph_data(time_steps, data_series_map)
                with self.graph_lock:
                    if self.fig and self.is_graph_showing:
                        try:
                            pass
                        except (AttributeError, TypeError, RuntimeError):
                            pass
            except queue.Empty:
                continue
            except (RuntimeError, ValueError, TypeError, AttributeError, KeyError) as e:
                print(e.with_traceback)
                break
