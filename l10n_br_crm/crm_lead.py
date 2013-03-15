# -*- encoding: utf-8 -*-
###############################################################################
#                                                                             #
# Copyright (C) 2012  Renato Lima - Akretion                                  #
#                                                                             #
# This program is free software: you can redistribute it and/or modify        #
# it under the terms of the GNU Affero General Public License as published by #
# the Free Software Foundation, either version 3 of the License, or           #
# (at your option) any later version.                                         #
#                                                                             #
# This program is distributed in the hope that it will be useful,             #
# but WITHOUT ANY WARRANTY; without even the implied warranty of              #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the               #
# GNU Affero General Public License for more details.                         #
#                                                                             #
# You should have received a copy of the GNU Affero General Public License    #
# along with this program.  If not, see <http://www.gnu.org/licenses/>.       #
###############################################################################

from osv import fields, osv
import re


class crm_lead(osv.osv):
    """CRM Lead Case"""
    _inherit = "crm.lead"
    _columns = {
        'l10n_br_city_id': fields.many2one(
            'l10n_br_base.city',
            u'Cidade',
            domain="[('state_id','=',state_id)]"
            ),
        'district': fields.char(u'Bairro', size=32),
        'number': fields.char(u'Número', size=10),
        }

    def onchange_l10n_br_city_id(self, cr, uid, ids, l10n_br_city_id):
        result = {'value': {'city': False, 'l10n_br_city_id': False}}

        if not l10n_br_city_id:
            return result

        obj_city = self.pool.get('l10n_br_base.city').read(cr, uid, l10n_br_city_id, ['name','id'])

        if obj_city:
            result['value']['city'] = obj_city['name']
            result['value']['l10n_br_city_id'] = obj_city['id']

        return result

    def onchange_mask_zip(self, cr, uid, ids, zip):
        result = {'value': {'zip': False}}

        if not zip:
            return result

        val = re.sub('[^0-9]', '', zip)

        if len(val) == 8:
            result['value']['zip'] = "%s-%s" % (val[0:5], val[5:8])

        return result


crm_lead()
