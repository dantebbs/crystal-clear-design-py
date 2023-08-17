"""
Copyright (c) 2023 by Crystal Clear Design

This intellectual property is shared to the public domain under the MIT License.
Crystal Clear Design offers no warranty and accepts no liability.
The only requirement for use is that this copyright notice remains intact.

This file is an example to help illustrate the use of the state_machine.py
library module. It simulates the common crosswalk signaling system used to
help pedestrians cross a busy street by stopping the vehicle traffic.

DISCLAIMER: This example must not be used for an actual, safety-critical
implementation of a crosswalk! It was selected for its familiarity to anyone
learning about the library, and is only to be used for demonstrating the various
features of the state_machine library module, and its use. This example does not
meet necessary safety requirements such as handling power outages, burned out
lights, emergency vehicle approaches, nor other possible events and usages.
"""

pedestrian_crosswalk_signals = """
{
  "events": [
    "button_push",
    "countdown_complete",
    "one_second"
  ],
  "states": {
    "start": {
      "tran": {
        "auto": {
          "dest": "Traffic Flowing"
        }
      }
    },
    "Traffic Flowing": {
      "entry": [
        "set_traf_light(yel)",
        "set_ped_light(red)"
      ],
      "tran": {
        "button_push": {
          "dest": "Traffic Stopping"
        }
      }
    },
    "Traffic Stopping": {
      "entry": [
        "set_traf_light(yel)",
        "start_countdown(5)"
      ],
      "tran": {
        "countdown_complete": {
          "dest": "Pedestrian Crossing"
        }
      }
    },
    "Pedestrian Crossing": {
      "entry": [
        "set_traf_light(red)",
        "set_ped_light(grn)",
        "start_countdown(5)"
      ],
      "tran": {
        "countdown_complete": {
          "acts": [
            "set_ped_light(yel)",
            "start_countdown(10)",
            "start_ped_time(10)"
          ],
          "dest": "Crossing Countdown"
        }
      }
    },
    "Crossing Countdown": {
      "tran": {
        "one_second": {
          "acts": [
            "update_ped_time()"
          ],
          "dest": "Crossing Countdown"
        },
        "countdown_complete": {
          "acts": [
            "update_ped_time()"
          ],
          "dest": "Traffic Flowing"
        }
      }
    }
  }
}
"""

import state_machine
import sys
try:
    import curses
except:
    print("This test script requires the 'curses' module. Before trying again, run: pip install windows-curses")
    exit(1)
import ascii_crosswalk


callbacks_module = sys.modules[__name__]

proc_period_ms = 50
crosswalk = None
ascii = None
quit = False

def set_traf_light(color: str) -> bool:
    global ascii
    ascii.print_status(f"Setting traffic light to {color}.")
    ascii.set_traf_light(color)
    ascii.print_display()
    return True

def set_ped_light(color: str) -> bool:
    global ascii
    ascii.print_status(f"Setting pedestrian light to {color}.")
    ascii.set_ped_light(color)
    ascii.print_display()
    return True

def start_countdown(time_s: str) -> bool:
    time_s_int = int(time_s, 10)
    #global ascii
    #ascii.print_status(f"Starting countdown of {time_s_int} seconds.")
    crosswalk.add_timer("countdown_complete", time_s_int * 1000)
    return True

ped_count_down_s = 0
def start_ped_time(time_s: str) -> bool:
    time_s_int = int(time_s, 10)
    global ped_count_down_s
    ped_count_down_s = time_s_int
    crosswalk.add_timer("one_second", 1000, time_s_int)
    update_ped_time()
    return True

def update_ped_time(unused = "") -> bool:
    global ped_count_down_s
    ped_count_down_s -= 1
    global ascii
    ascii.print_status(f"Showing pedestrian countdown of {ped_count_down_s} seconds.")
    ascii.set_ped_time(ped_count_down_s)
    ascii.draw_ped_sig()
    return True

def main(stdscr):
    # Allow for fancy display.
    global ascii
    ascii = ascii_crosswalk.ascii_crosswalk(stdscr)

    # Set desired flags before instantiation.
    #state_machine.debug_flags.set("machine_parse")
    #state_machine.debug_flags.set("execution_details")

    # Now that all the call-back functions are defined, create the machine.
    global crosswalk
    crosswalk = state_machine.state_machine( pedestrian_crosswalk_signals, callbacks_module, proc_period_ms )

    ascii.print_status("-----------------------------")
    ascii.print_status("| Crosswalk Light Simulator |")
    ascii.print_status("-----------------------------")
    ascii.print_status("")
    ascii.print_status("Press 'b' to request a crossing, press 'esc' to exit simulation.")
    ascii.print_status("")

    global quit
    while (not quit):
        crosswalk.process_events_rate_limited()
        c = stdscr.getch()
        if c == ord('b'):
            crosswalk.enqueue_event("button_push")
            ascii.print_status("You pressed the crossing request button.")
        #elif c == curses.ascii.ESC or c == ord('q'):
        elif c == 27 or c == ord('q'):
            quit = True

    ascii.print_status("Exiting simulation.")
    crosswalk.cleanup()

# Execute with proper curses lib set-up and clean-up.
curses.wrapper(main)
