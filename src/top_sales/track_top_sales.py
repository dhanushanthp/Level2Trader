#!/usr/bin/python
import time
from watchdog.observers import Observer
from watchdog.events import FileModifiedEvent
from watchdog.events import FileSystemEventHandler
from src.top_sales import top_sales_tracker


class TriggerOnChange(FileSystemEventHandler):
    def __init__(self):
        self.top_tracker_obj = top_sales_tracker.TopSalesTracker()

    def on_modified(self, event: FileModifiedEvent):
        # Call the function to update the terminal
        path_to_file = event.src_path
        self.top_tracker_obj.generate_terminal_data(path_to_file)


if __name__ == "__main__":
    event_handler = TriggerOnChange()
    observer = Observer()
    observer.schedule(event_handler, path='data/tape_data/top_sales_on_bids_ask.json', recursive=False)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
