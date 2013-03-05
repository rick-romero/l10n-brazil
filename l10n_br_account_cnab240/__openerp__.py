# -*- coding: utf-8 -*-

##############################################################################
#                                                                            #
#  Copyright (C) 2013 Proge Informática Ltda (<http://www.proge.com.br>).    #
#                                                                            #
#  Author Daniel Hartmann <daniel@proge.com.br>                              #
#                                                                            #
#  This program is free software: you can redistribute it and/or modify      #
#  it under the terms of the GNU Affero General Public License as            #
#  published by the Free Software Foundation, either version 3 of the        #
#  License, or (at your option) any later version.                           #
#                                                                            #
#  This program is distributed in the hope that it will be useful,           #
#  but WITHOUT ANY WARRANTY; without even the implied warranty of            #
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the             #
#  GNU Affero General Public License for more details.                       #
#                                                                            #
#  You should have received a copy of the GNU Affero General Public License  #
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.     #
#                                                                            #
##############################################################################

{
    "name": "CNAB 240",
    "version": "0.1",
    "author": "PROGE",
    "category": "Localization",
    "website": "http://proge.com.br",
    "description": """
    Module to communicate OpenERP with banks via CNAB240.
    By now only supports the generation of delivery files to Banco do Brasil
    (blocks A, B and C).
    """,
    'depends': [
        'l10n_br_account',
        ],
    'init_xml': [],
    'update_xml': [
        'l10n_br_account_cnab240_view.xml',
        ],
    'demo_xml': [],
    'test': [],
    'installable': True,
    'active': False,
}

