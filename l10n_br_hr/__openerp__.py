# -*- coding: utf-8 -*-

##############################################################################
#                                                                            #
#  Copyright (C) 2012 Proge Informática Ltda (<http://www.proge.com.br>).    #
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
    "name": "Brazilian Localization for Human Resources",
    "version": "0.1",
    "author": "PROGE",
    "category": "Localisation",
    "website": "http://proge.com.br",
    "description": """
    Brazilian Localization for Human Resources
    Currently it doesn't support companies with CEI subscriptions.

    Generates the following files through wizards:
    - RAIS
    - SEFIP*
    
    * Currently does not support 650 and 660 "recolhimento" codes
    """,
    'depends': [
        'l10n_br_account',
        'hr_contract',
        'hr_holidays',
        'hr_payroll',
        ],
    'init_xml': [],
    'update_xml': [
        'data/hr.contract.type.csv',
        'data/hr.holidays.status.csv',
        'data/hr_payroll_data.xml',
        'data/l10n_br_hr.etnia.csv',
        'data/l10n_br_hr.grau_de_instrucao.csv',
        'data/l10n_br_hr.motivo_de_desligamento.csv',
        'data/l10n_br_hr.nationality.csv',
        'data/l10n_br_hr.ocupacao.csv',
        'data/l10n_br_hr.ocorrencia.csv',
        'data/l10n_br_hr.recolhimento.csv',
        'data/l10n_br_hr.tipo_de_admissao.csv',
        'data/l10n_br_hr.vinculo.csv',
        'security/ir.model.access.csv',

        'hr_employee_sequence.xml',
        'l10n_br_hr_view.xml',
        'wizard/rais_view.xml',
        'wizard/sefip_view.xml',
        ],
    'demo_xml': [],
    'test': [],
    'installable': True,
    'active': False,
}
