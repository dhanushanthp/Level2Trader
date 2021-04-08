#!/usr/bin/python
import time
from watchdog.observers import Observer
from watchdog.events import FileModifiedEvent
from watchdog.events import FileSystemEventHandler
from src.higher_timeframe.read_higher_data import HigherScale


class TriggerOnChange(FileSystemEventHandler):
    def __init__(self):
        self.top_tracker_obj = HigherScale()

    def on_modified(self, event: FileModifiedEvent):
        # Call the function to update the terminal
        # path_to_file = event.src_path
        # print(path_to_file)
        self.top_tracker_obj.generate_output()


if __name__ == "__main__":
    event_handler = TriggerOnChange()
    observer = Observer()
    observer.schedule(event_handler, path='data/tape_data/tape_data_higher_frame.csv', recursive=False)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
