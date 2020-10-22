
# Copyright (C) 2018 Intel Corporation
#
# SPDX-License-Identifier: MIT

default_app_config = 'authentication.apps.AuthenticationConfig'

from enum import Enum

class AUTH_ROLE(Enum):
    ADMIN = 'admin'
    ACCOUNTANT = 'accountant'
    CASHIER = 'cashier'
    ASSISTANT = 'shop assistant'

    def __str__(self):
        return self.value
