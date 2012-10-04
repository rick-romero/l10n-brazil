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

from osv import osv, fields
from tools.translate import _

class l10n_br_hr_nationality(osv.osv):
    _name = 'l10n_br_hr.nationality'
    _description = u'Nacionalidade'
    _columns = {
        'code': fields.char(u'Código', size=2, required=True),
        'name': fields.char(u'Nacionalidade', size=60, required=True),
        }

l10n_br_hr_nationality()


class l10n_br_hr_etnia(osv.osv):
    _name = 'l10n_br_hr.etnia'
    _description = u'Etnia'
    _columns = {
        'code': fields.char(u'Código', size=2, required=True),
        'name': fields.char(u'Descrição', size=60, required=True),
        }

l10n_br_hr_etnia()


class hr_employee(osv.osv):
    _inherit = 'hr.employee'
    _columns = {
        'nationality_id': fields.many2one(
            'l10n_br_hr.nationality', _(u'Nacionalidade')
            ),
        'etnia_id': fields.many2one('l10n_br_hr.etnia', _(u'Etnia')),
        'deficiencia': fields.selection((
            ('0', u'Não Possui'),
            ('1', u'Física'),
            ('2', u'Auditiva'),
            ('3', u'Visual'),
            ('4', u'Intelectual (Mental)'),
            ('5', u'Múltipla'),
            ('6', u'Reabilitado'),
            ), u'Deficiência'),
        }

hr_employee()
