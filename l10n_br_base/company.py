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
import re


class res_company(osv.osv):

    _inherit = "res.company"

    def _get_address_data(
        self, cr, uid, ids, field_names, arg, context=None
        ):
        return super(res_company, self)._get_address_data(
            cr, uid, ids, field_names, arg, context
            )

    def _set_address_data(
        self, cr, uid, company_id, name, value, arg, context=None
        ):
        return super(res_company, self)._set_address_data(
            cr, uid, company_id, name, value, arg, context
            )

    _columns = {
        'l10n_br_city_id': fields.function(
            _get_address_data,
            fnct_inv=_set_address_data,
            type='many2one',
            domain="[('state_id','=',state_id)]",
            relation='l10n_br_base.city',
            string=u'Cidade',
            multi='address'
            ),
        'number': fields.function(
            _get_address_data,
            fnct_inv=_set_address_data,
            size=10,
            type='char',
            string=u'Número',
            multi='address'
            ),
        'district': fields.function(
            _get_address_data,
            fnct_inv=_set_address_data,
            size=32,
            type='char',
            string=u'Bairro',
            multi='address'
            ),
        }

    def onchange_l10n_br_city_id(self, cr, uid, ids, l10n_br_city_id):

        result = {'value': {'city': False, 'l10n_br_city_id': False}}

        if not l10n_br_city_id:
            return result

        obj_city = self.pool.get('l10n_br_base.city').read(cr, uid,
                                                           l10n_br_city_id,
                                                           ['name', 'id'])

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
            zip = "%s-%s" % (val[0:5], val[5:8])
            result['value']['zip'] = zip
        return result


res_company()
