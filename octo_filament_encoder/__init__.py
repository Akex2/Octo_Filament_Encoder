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
		self.distance = 0

	def get_data(self):
		return self.distance

	def set_data(self,ndistance):
		self.distance = ndistance


class encoder():
	"""docstring for encoder"""
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
		return self.distance

	def set_data(self):
		self.my_encoder.setup(counter = 0)  # Initial scale position
		self.distance = 0

class EncoderOctoClass(octoprint.plugin.TemplatePlugin,
						octoprint.plugin.AssetPlugin,
						octoprint.plugin.EventHandlerPlugin,
						octoprint.plugin.StartupPlugin,
						octoprint.plugin.ShutdownPlugin,
						octoprint.plugin.SettingsPlugin,
						octoprint.plugin.OctoPrintPlugin,
						):
	def __init__(self):
		self.oldstep = travel()
		self.step = travel()
		self.encoder = encoder()
		self.ratio = 1
		self.bool = 0
		self.cpt = 0
		self.erreur = 0
		#self._logger.info("init OK")

	def checkEcode(self, comm_instance, phase, cmd, cmd_type, gcode, *args, **kwargs):
		E = 'E'
		if (self._settings.get_boolean(["enable"]) == True ) :
			#self._logger.info(test5)
			if gcode and gcode == "G92" :
				if E in cmd :
					i = (cmd.find('E'))+1
					#i = i+1
					step = float(''.join(cmd[i:].split(" ")))
					self.oldstep.set_data(step)
			else :
				if E in cmd :
					holdstep = self.oldstep.get_data()
					encoder_step = self.encoder.get_data()
					i = (cmd.find('E'))+1
					steplist = cmd[i:].split(" ")
					steplist = steplist[:1]
					step = float(''.join(steplist))					
					stepsend = step - (holdstep)
					self.oldstep.set_data(step)
					olddata = self.step.get_data()
					olddata = (stepsend+olddata)
					self.step.set_data(olddata)
					cprMM = self._settings.get(["cprMM"])
					self.erreur = (olddata-(encoder_step*cprMM))
					#self._logger.info(self.erreur)
					
					if (self._settings.get_boolean(["autocalib"]) == True ) :
						if (self._settings.get(["methode"]) == "nextmove" ) :
							self.timer2.start()
					else :
						if (self.erreur > (self._settings.get_int(["errorMM"]))) :
							#self._logger.info("erreur: trop importante!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
							cmd = self._settings.get(["commande"])
		return cmd,
		
	def on_event(self, event, payload):
		#self._plugin_manager.send_plugin_message(self._identifier, data)
		if event == "PrintStarted":
			self.encoder.set_data()
			self.oldstep.set_data(0)
			self.step.set_data(0)
			if (self._settings.get_boolean(["autocalib"]) == False ) :
				self.timer.start()
			else :
				self._plugin_manager.send_plugin_message(self._identifier, {"type": "popup", "msg": "Autocalibration running!"})
		if event == "PrintDone":
			self.timer.cancel()
			if (self._settings.get_boolean(["autocalib"]) == True ) :
				self.timer2.start()
		if event == "PrintResumed" : #or event == "PrintCanceled" :
			if (self._settings.get_boolean(["autocalib"]) == False ) :
				self.encoder.set_data()
				self.oldstep.set_data(0)
				self.step.set_data(0)


	def get_settings_defaults(self):
		return dict(enable =True,enable_graph =True, cprMM=1000, errorMM=2, autocalib=True, calibrated=False, methode="nextprint", loop=20)

	def on_after_startup(self):
		intervale = self._settings.get_int(["loop"])
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
		octoprint.plugin.SettingsPlugin.on_settings_save(self, data)


	def fromTimer (self):
		self.encoder.set_data()
		self.oldstep.set_data(0)
		self.step.set_data(0)

	def fromTimer3 (self):
		erreur = self.erreur
		data = {
				"type": "x_graph",
				"msg": erreur,
				}
		#self._logger.info(erreur)
		self._plugin_manager.send_plugin_message(self._identifier, data)


	def fromTimer2 (self):
		if self.bool == 0 :
			self.bool = 1


		else :			
			#time.sleep(1)
			self.timer2.cancel()
			self.bool = 0
			olddata = self.step.get_data()
			holdstep = self.oldstep.get_data()
			encoder_step = self.encoder.get_data()
			cprMM = (olddata/encoder_step)
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

	#@staticmethod



__plugin_name__ = "Octo_Filament_Encoder"

def __plugin_load__():

	global __plugin_implementation__

	__plugin_implementation__ = EncoderOctoClass()
	#__plugin_implementation__ = HelloWorldPlugin()


	global __plugin_hooks__

	__plugin_hooks__ = {

		"octoprint.comm.protocol.gcode.queuing": __plugin_implementation__.checkEcode

	}

