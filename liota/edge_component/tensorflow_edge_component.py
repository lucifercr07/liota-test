# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------#
#  Copyright © 2015-2016 VMware, Inc. All Rights Reserved.                    #
#                                                                             #
#  Licensed under the BSD 2-Clause License (the “License”); you may not use   #
#  this file except in compliance with the License.                           #
#                                                                             #
#  The BSD 2-Clause License                                                   #
#                                                                             #
#  Redistribution and use in source and binary forms, with or without         #
#  modification, are permitted provided that the following conditions are met:#
#                                                                             #
#  - Redistributions of source code must retain the above copyright notice,   #
#      this list of conditions and the following disclaimer.                  #
#                                                                             #
#  - Redistributions in binary form must reproduce the above copyright        #
#      notice, this list of conditions and the following disclaimer in the    #
#      documentation and/or other materials provided with the distribution.   #
#                                                                             #
#  THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"#
#  AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE  #
#  IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE #
#  ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE  #
#  LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR        #
#  CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF       #
#  SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS   #
#  INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN    #
#  CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)    #
#  ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF     #
#  THE POSSIBILITY OF SUCH DAMAGE.                                            #
# ----------------------------------------------------------------------------#

import tensorflow as tf
import logging
import numpy as np
from liota.edge_component.edge_component import EdgeComponent
from liota.entities.registered_entity import RegisteredEntity
from liota.entities.edge_systems.edge_system import EdgeSystem
from liota.entities.devices.device import Device
from liota.entities.metrics.metric import Metric
from liota.entities.metrics.registered_metric import RegisteredMetric

log = logging.getLogger(__name__)

class TensorFlowEdgeComponent(EdgeComponent):

	def __init__(self, model_path, features=None, actuator_udm=None):
		self.model = None
		self.features = features
		self.model_path = model_path
		self.actuator_udm = actuator_udm
		self.load_model(self.model_path)

	def load_model(self,model_path):
		with tf.Session() as sess:
			feature_cols = [tf.contrib.layers.real_valued_column("", dimension=1)]
			self.model = tf.contrib.learn.LinearClassifier(feature_columns=feature_cols, model_dir=self.model_path)
			
	def register(self, entity_obj):
		if isinstance(entity_obj, Metric):
			return RegisteredMetric(entity_obj, self, None)
		else:
			return RegisteredEntity(entity_obj, self, None)

	def create_relationship(self, reg_entity_parent, reg_entity_child):
		reg_entity_child.parent = reg_entity_parent

	def input_fn(self, message):
		return np.array([message], dtype=np.float32)

	def process(self, message):
		self.actuator_udm(list(self.model.predict_classes(input_fn=lambda:self.input_fn(message))))

	def _format_data(self, reg_metric):
		met_cnt = reg_metric.values.qsize()
		if met_cnt == 0:
			return
		for _ in range(met_cnt):
			m = reg_metric.values.get(block=True)
			if m is not None:
				return m[1]

	def set_properties(self, reg_entity, properties):
		super(TensorFlowEdgeComponent, self).set_properties(reg_entity, properties)

	def unregister(self, entity_obj):
		pass

	def build_model(self):
		pass


