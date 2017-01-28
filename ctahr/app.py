
import time
import monotonic
import signal
import threading
import configuration
import RPi.GPIO as GPIO
from display import CtahrDisplay
from th_sensor import CtahrThermoHygroSensor
from logic import CtahrLogic
from safety import CtahrSafety
from stats import CtahrStats
from buttons import CtahrButtons
from fan import CtahrFan
from heater import CtahrHeater
from dehum import CtahrDehum
from rrd_logging import CtahrLogging

class CtahrApplication:

    def __init__(self):
        self.not_running = threading.Event()

        print "[+] Starting Ctahr"

        # gracefull shutdown signal handler
        signal.signal(signal.SIGTERM, self.shutdown)
        signal.signal(signal.SIGINT, self.shutdown)

        # Starting interior sensor daemon
        self.thermohygro_interior = CtahrThermoHygroSensor(
            configuration.thermohygro_sensor_interior_pin, 'interior')
        self.thermohygro_interior.start()

        # Starting exterior sensor daemon
        self.thermohygro_exterior = CtahrThermoHygroSensor(
            configuration.thermohygro_sensor_exterior_pin, 'exterior')
        self.thermohygro_exterior.start()

        # Create rrd log object
        self.rrd = CtahrLogging(self)

        # Starting stats daemon
        self.stats = CtahrStats(self)
        self.stats.start()

        # Starting regulation daemon
        self.logic = CtahrLogic(self)
        self.logic.start()

        # Starting buttons manager
        self.buttons = CtahrButtons(self)
        self.buttons.start()

        # Starting fan manager
        self.fan = CtahrFan(self)
        self.fan.start()

        # Starting heater manager
        self.heater = CtahrHeater(self)
        self.heater.start()

        # Starting dehum manager
        self.dehum = CtahrDehum(self)
        self.dehum.start()

        # Starting display manager
        self.display = CtahrDisplay(self)
        self.display.start()

        # Starting safety daemon
        self.safety = CtahrSafety(self)
        self.safety.start()

        self.led_run_status = False


    def shutdown(self, signum, frame):
        # perform a gracefull shutdown here ;)

        print "[-] SIGNAL",signum,"received, shutting down gracefully"
        #
        self.not_running.set()

    def run(self):
        while not self.not_running.is_set():
            self.not_running.wait(1)

        self.safety.stop()
        self.safety.join()
        self.display.stop()
        self.display.join()
        self.dehum.stop()
        self.dehum.join()
        self.heater.stop()
        self.heater.join()
        self.fan.stop()
        self.fan.join()
        self.buttons.stop()
        self.buttons.join()
        self.logic.stop()
        self.logic.join()
        self.stats.stop()
        self.stats.join()
        self.thermohygro_exterior.stop()
        self.thermohygro_interior.stop()

        GPIO.cleanup()
        print "[-] Ctahr as stopped"
