# coding=utf-8
from __future__ import absolute_import

__author__ = "Gina Häußge <gina@octoprint.org>"
__license__ = 'GNU Affero General Public License http://www.gnu.org/licenses/agpl.html'
__copyright__ = "Copyright (C) 2015 The OctoPrint Project - Released under terms of the AGPLv3 License"

import os
import json
import time
import octoprint.util
import octoprint.plugin
import octoprint.settings

from octoprint.events import Events
from octoprint.server import admin_permission
from flask.ext.login import current_user


import datetime
import threading
from threading import Timer
from octoprint.util import RepeatedTimer
from Rpi_encoder import Rpi_encoder
#import time
class travel():
	"""docstring for travel"""
	def __init__(self):
		#super(travel, self).__init__()
		self.distance = 0

	def get_data(self):
		#self.distance = distance
		return self.distance

	def set_data(self,ndistance):
		self.distance = ndistance
		#print ndistance
		#self.distance=ndistance
class encoder():
	"""docstring for travel"""
	def __init__(self):
		def my_callback(scale_position):
			self.distance = scale_position
		# Init the encoder pins
		self.my_encoder = Rpi_encoder.Encoder(CLK=17, DT=18, SW=26)
		self.my_encoder.setup(scale_min=(-1000), scale_max=100000, step=1, chg_callback=my_callback, counter = 0)

		# Create the thread
		self.my_thread = threading.Thread(target=self.my_encoder.watch)
		self.my_thread.setDaemon(True)

		# Launch the thread
		self.my_thread.start()


	def get_data(self):
		#self.distance = distance
		return self.distance

	def set_data(self):
		self.my_encoder.setup(counter = 0)  # Initial scale position
		self.distance = 0
		#print ndistance
		#self.distance=ndistance

	def stop_thread(self):
		self._logger.info("Stop Plugin")
		self.my_thread.stop()  # Initial scale position

class EncoderOctoClass(octoprint.plugin.TemplatePlugin,
						octoprint.plugin.AssetPlugin,
						octoprint.plugin.EventHandlerPlugin,
						octoprint.plugin.StartupPlugin,
						octoprint.plugin.ShutdownPlugin,
						octoprint.plugin.SettingsPlugin,
						octoprint.plugin.OctoPrintPlugin,
						):
	def __init__(self):
		#super(travel, self).__init__()
		self.oldstep = travel()
		self.step = travel()
		self.encoder = encoder()
		#self.timeout = timeralex()
		#self.t = Timer(20, self.timeout.alextimer())
		
		#self.t.start()
		self.ratio = 1
		self.bool = 0
		self.cpt = 0
		self.erreur = 0
		#self._logger.info("init OK")

	def checkEcode(self, comm_instance, phase, cmd, cmd_type, gcode, *args, **kwargs):
		E = 'E'
		#self._logger.info("phase: {phase}".format(**locals()))
		#self._logger.info("cmd: {cmd}".format(**locals()))
		#url=self._settings.get(["url"])
		if (self._settings.get_boolean(["enable"]) == True ) :
			#self._logger.info(test5)
			if gcode and gcode == "G92" :
				#self._logger.info("G92 opertaionel")
				if E in cmd :
					i = (cmd.find('E'))+1
					#i = i+1
					step = float(''.join(cmd[i:].split(" ")))
					self.oldstep.set_data(step)
					'''
					#self._logger.info("Just sent M106: {cmd}".format(**locals()))
					'''
			#self._logger.info("Just sent M106: {cmd}".format(**locals()))
		
			#self._logger.info("cmd_type: {cmd_type}".format(**locals()))
			#self._logger.info("gcode: {gcode}".format(**locals()))

			

			else :
				if E in cmd :
					#self._logger.info("cmd: preumsssssss")
					holdstep = self.oldstep.get_data()
					encoder_step = self.encoder.get_data()
					#self._logger.info(cmd)
					i = (cmd.find('E'))+1
					steplist = cmd[i:].split(" ")
					steplist = steplist[:1]
					step = float(''.join(steplist))
					#self._logger.info(steplist)
					
					stepsend = step - (holdstep)
					#self._logger.info(step)
					self.oldstep.set_data(step)
					olddata = self.step.get_data()
					olddata = (stepsend+olddata)
					self.step.set_data(olddata)
					self.erreur = (olddata-encoder_step)
					self._logger.info(olddata)
					
					if (self._settings.get_boolean(["autocalib"]) == True ) :
						self._logger.info("apres if autocalib")
						if (self._settings.get(["methode"]) == "nextmove" ) :
							self.timer2.start()
					else :
						self._logger.info("calibrated do job")
						self._logger.info("erreur: {erreur}".format(**locals()))
						self._logger.info("erreur: {olddata}".format(**locals()))
						self._logger.info("erreur: {encoder_step}".format(**locals()))

						if (erreur > (self._settings.get_int(["errorMM"]))) :
							self._logger.info("erreur: trop importante!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
							cmd = self._settings.get(["commande"])
							
							#self._logger.info(type(step))
							#self._logger.info(step)
							#self._logger.info("index: {i}".format(**locals()))
							#self._logger.info("B E step: {step}".format(**locals()))
							#self._logger.info("B E holdstep: {holdstep}".format(**locals()))
							#self._logger.info("B E stepsend: {stepsend}".format(**locals()))
		#olddata=(self.encoder.get_data())
		#self._logger.info("compteur: {olddata}".format(**locals()))
		return cmd,
		
	def on_event(self, event, payload):
		#self._logger.info("test strart print {event}".format(**locals()))
		#result = self.start_timelapse()
		message = "test akex on popup"
		data = {
			"type": "popup",
			"msg": message,
		}
		#self.send_popup_message(self._identifier, message)
		#self._plugin_manager.send_plugin_message(self._identifier, data)
		if event == "PrintStarted":
			self._plugin_manager.send_plugin_message(self._identifier, {"type": "popup", "msg": message})
			#self._plugin_manager.send_plugin_message(self._identifier, {"type": "popup_success", "msg": message})
			#self._plugin_manager.send_plugin_message(self._identifier, {"type": "popup_info", "msg": message})
			#self._plugin_manager.send_plugin_message(self._identifier, {"type": "popup_error", "msg": message})
			self.encoder.set_data()
			self.oldstep.set_data(0)
			self.step.set_data(0)
			self._logger.info("test strart print {event}".format(**locals()))
			self.send_popup_message(self._identifier, event)
			if (self._settings.get_boolean(["autocalib"]) == False ) :
				self._logger.info("timer start")
				#self.timer.start()
			else :
				self._plugin_manager.send_plugin_message(self._identifier, {"type": "popup", "msg": "Autocalibration running!"})
		if event == "PrintDone":
			localtime = time.localtime(time.time())
			self._logger.info(localtime)
			self.timer.cancel()
			#self._logger.info("compteur: {olddata}".format(**locals()))
			if (self._settings.get_boolean(["autocalib"]) == True ) :
				self._logger.info("apres if autocalib")
				self.timer2.start()
		if event == "PrintResumed" : #or event == "PrintCanceled" :
			if (self._settings.get_boolean(["autocalib"]) == False ) :
				self._logger.info("reset resumed")
				self.encoder.set_data()
				self.oldstep.set_data(0)
				self.step.set_data(0)

				



	def on_shutdown(self):
		self._logger.info("Stop Plugin!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
		#self.encoder.stop_thread()

	def get_settings_defaults(self):

		self._logger.info("get_settings_defaults!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
		return dict(enable =True,enable_graph =True, cprMM=1000, errorMM=2, autocalib=True, calibrated=False, methode="nextprint", loop=20)

	def on_after_startup(self):
		intervale = self._settings.get(["loop"])
		self.timer = RepeatedTimer(intervale, self.fromTimer, run_first=True,)
		self.timer2 = RepeatedTimer(2, self.fromTimer2, run_first=True,)
		self.timer3 = RepeatedTimer(2, self.fromTimer3, run_first=True,)
		self.timer3.start()

	def get_template_configs(self):
		return [
			#dict(type="navbar", custom_bindings=False),
			dict(type="settings", custom_bindings=False)
		]

	def get_assets(self):
		return dict(
		js=["js/octo_encoder.js","js/plotly-latest.min.js"],
		)

	def on_settings_save(self, data):
		self.encoder.set_data()
		self.oldstep.set_data(0)
		self.step.set_data(0)
		self._logger.info("save setinnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnng")
		octoprint.plugin.SettingsPlugin.on_settings_save(self, data)


	def fromTimer (self):
		self.encoder.set_data()
		self.oldstep.set_data(0)
		self.step.set_data(0)
		self._logger.info("reset all data ")

	def fromTimer3 (self):
		#self._logger.info("timer error ")
		erreur = self.erreur
		data = {
						"type": "x_graph",
						"msg": erreur,
					}
		self._plugin_manager.send_plugin_message(self._identifier, data)


	def fromTimer2 (self):
		'''
		self.encoder.set_data()
		self.oldstep.set_data(0)
		self.step.set_data(0)
		'''
		
		if self.bool == 0 :
			self.bool = 1
			self._logger.info("je fait rien")
			localtime = time.localtime(time.time())
			self._logger.info(localtime)

		else :			
			#time.sleep(1)
			localtime = time.localtime(time.time())
			self._logger.info(localtime)
			self.timer2.cancel()
			self.bool = 0
			olddata = self.step.get_data()
			holdstep = self.oldstep.get_data()
			encoder_step = self.encoder.get_data()
			cprMM = (olddata/encoder_step)
			self._logger.info("olddata {olddata}".format(**locals()))
			self._logger.info("holdstep {holdstep}".format(**locals()))
			self._logger.info("encoder_step {encoder_step}".format(**locals()))
			self._logger.info("cprMM {cprMM}".format(**locals()))
			self.encoder.set_data()
			self.oldstep.set_data(0)
			self.step.set_data(0)
			self._settings.set(['cprMM'], cprMM)
			self._settings.set(['autocalib'], False)
			self._settings.set(['calibrated'], True)
			self._settings.save()
			self._plugin_manager.send_plugin_message(self._identifier, {"type": "popup_success", "msg": "Autocalibration Done!"})

	def get_update_information(self):
		return dict(
			automaticshutdown=dict(
			displayName="Octo_Filament_Encoder",
			displayVersion=self._plugin_version,

			# version check: github repository
			type="github_release",
			user="Akex2",
			repo="Octo_Filament_Encoder",
			current=self._plugin_version,

			# update method: pip w/ dependency links
			pip="https://github.com/Akex2/Octo_Filament_Encoder/archive/{target_version}.zip"
		)
	)

	@staticmethod
	def send_popup_message(self, msg):
		self.send_plugin_message("popup", msg)

	def start_timelapse(self):
		return {'success': False,
				'error': "Octolapse requires Octoprint v1.3.7 or above, but version v{0} is installed."
				"  Please update Octoprint to use Octolapse.".format(octoprint.server.DISPLAY_VERSION),
				'warning': False}



__plugin_name__ = "Octo_Filament_Encoder"

def __plugin_load__():

	global __plugin_implementation__

	__plugin_implementation__ = EncoderOctoClass()
	#__plugin_implementation__ = HelloWorldPlugin()


	global __plugin_hooks__

	__plugin_hooks__ = {

		"octoprint.comm.protocol.gcode.queuing": __plugin_implementation__.checkEcode

	}

