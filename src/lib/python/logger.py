from proglog import ProgressBarLogger
import streamlit as st

class MoviePyStreamlitLogger(ProgressBarLogger):
    def __init__(self, progress_bar=None, label_widget=None):
        super().__init__()
        self.progress_bar = progress_bar
        self.label_widget = label_widget
        self.last_message = ""

    def callback(self, **changes):
        # Every time the logger is updated, this function is called
        for (parameter, value) in changes.items():
            pass # We don't really use this much in basic bars

    def bars_callback(self, bar, attr, value, old_value=None):
        # Every time a progress bar is updated, this function is called
        percentage = (value / self.bars[bar]['total'])
        if self.progress_bar:
            self.progress_bar.progress(percentage)
    
        if self.label_widget:
            self.label_widget.text(f"Processing {bar}: {int(percentage * 100)}%")

    def message(self, message):
        # When a message is printed
        self.last_message = message
        if self.label_widget:
            self.label_widget.text(message)
