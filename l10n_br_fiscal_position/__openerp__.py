# -*- encoding: utf-8 -*-
###############################################################################
#                                                                             #
# Copyright (C) 2009-2013  Renato Lima - Akretion                             #
#                                                                             #
#This program is free software: you can redistribute it and/or modify         #
#it under the terms of the GNU Affero General Public License as published by  #
#the Free Software Foundation, either version 3 of the License, or            #
#(at your option) any later version.                                          #
#                                                                             #
#This program is distributed in the hope that it will be useful,              #
#but WITHOUT ANY WARRANTY; without even the implied warranty of               #
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the                #
#GNU Affero General Public License for more details.                          #
#                                                                             #
#You should have received a copy of the GNU Affero General Public License     #
#along with this program.  If not, see <http://www.gnu.org/licenses/>.        #
###############################################################################

{
    'name': 'Brazilian Localization - Fiscal Position',
    'description': '''
        Brazilian Localization - Module implementing the "fiscal_position" method for defining tax-related properties.
        The fiscal_position method is the default method used by OpenERP for defining taxes on invoices. To ease the 
        selection of fiscal positions, the Brazillian Localization uses a "rules" system, defined in the 
        "account_fiscal_position_rule*" modules.  
    ''',
    'category': 'Localisation',
    'license': 'AGPL-3',
    'author': 'Akretion, OpenERP Brasil, Brblue',
    'website': 'http://openerpbrasil.org',
    'version': '0.6',
    'depends': [
        'l10n_br',
        'l10n_br_base',
        'l10n_br_product',
        'l10n_br_account',
        'l10n_br_stock',
        'l10n_br_sale_stock',
        'l10n_br_purchase',
        'account_fiscal_position_rule',
        'account_fiscal_position_rule_purchase',
        'account_fiscal_position_rule_sale',
        'account_fiscal_position_rule_stock',
    ],
    'data': [
        'account_fiscal_position_rule_view.xml',
        'account_invoice_view.xml',
        'purchase_view.xml',
        'sale_view.xml',
        'stock_view.xml',
        'l10n_br_account_view.xml',
        'account_fiscal_position_view.xml',
        'account_fiscal_position_rule_data.xml',
        'security/ir.model.access.csv',
    ],
    'demo': [
        'account_fiscal_position_rule_demo.xml',
    ],
    'test': [],
    'installable': True,
    'auto_install': True,
}
