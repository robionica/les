# Copyright (c) 2012-2013 Oleksandr Sviridenko
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import absolute_import

from logging import *


basic_config = basicConfig
capture_warnings = captureWarnings
get_logger = getLogger

DEFAULT_LOG_FORMAT = "[%(asctime)s][%(levelname).1s][%(module)-25s] %(message)s"
basic_config(level=CRITICAL, format=DEFAULT_LOG_FORMAT)
capture_warnings(True)
