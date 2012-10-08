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


class res_company(osv.osv):

    _inherit = "res.company"

    def _get_address_data(self, cr, uid, ids, field_names, arg, context=None):
        """ Read the 'address' functional fields. """
        result = {}
        part_obj = self.pool.get('res.partner')
        address_obj = self.pool.get('res.partner.address')
        for company in self.browse(cr, uid, ids, context=context):
            result[company.id] = {}.fromkeys(field_names, False)
            if company.partner_id:
                address_data = part_obj.address_get(cr, uid,
                                                    [company.partner_id.id],
                                                    adr_pref=['default'])
                if address_data['default']:
                    address = address_obj.read(cr, uid,
                                               address_data['default'],
                                               field_names, context=context)
                    for field in field_names:
                        result[company.id][field] = address[field] or False
        return result

    def _set_address_data(self, cr, uid, company_id, name, value, arg,
                          context=None):
        """ Write the 'address' functional fields. """
        company = self.browse(cr, uid, company_id, context=context)
        if company.partner_id:
            part_obj = self.pool.get('res.partner')
            address_obj = self.pool.get('res.partner.address')
            address_data = part_obj.address_get(cr, uid,
                                                [company.partner_id.id],
                                                adr_pref=['default'])
            address = address_data['default']
            if address:
                address_obj.write(cr, uid, [address], {name: value or False})
            else:
                address_obj.create(cr, uid, {
                    name: value or False,
                    'partner_id': company.partner_id.id,
                    }, context=context)
        return True

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

res_company()
