# -*- coding: utf-8 -*-
###############################################################################
#                                                                             #
# Copyright (C) 2010  Renato Lima - Akretion                                  #
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

class l10n_br_delivery_carrier_vehicle(osv.osv):    
    
    _name = 'l10n_br_delivery.carrier.vehicle'
    _description = u'Veículos das Transportadoras'
    
    _columns = {
        'name': fields.char(u'Nome', required=True, size=32),
        'description': fields.char(u'Descrição', size=132),
        'plate': fields.char(u'Placa', size=7),
        'driver': fields.char(u'Condutor', size=64),
        'rntc_code': fields.char(u'Código ANTT', size=32),
        'country_id': fields.many2one('res.country', u'País'),
        'state_id': fields.many2one(
            'res.country.state',
            u'Estado',
            domain="[('country_id','=',country_id)]",
            ),
        'l10n_br_city_id': fields.many2one(
            'l10n_br_base.city',
            u'Cidade',
            domain="[('state_id','=',state_id)]",
            ),
        'active': fields.boolean(u'Ativo'),
        'manufacture_year': fields.char(u'Ano de Fabricação', size=4),
        'model_year': fields.char(u'Ano do Modelo', size=4),
        'type': fields.selection([('bau', u'Caminhão Baú')], u'Ano do Modelo'),
        'carrier_id': fields.many2one(
            'delivery.carrier',
            u'Transportadora',
            select=True,
            required=True,
            ondelete='cascade',
            ),
        }

l10n_br_delivery_carrier_vehicle()

class l10n_br_delivery_shipment(osv.osv):    

    _name = 'l10n_br_delivery.shipment'

    _columns = {
        'code': fields.char(u'Nome', size=32),
        'description': fields.char(u'Descrição', size=132),
        'carrier_id': fields.many2one(
            'delivery.carrier', u'Transportadora', select=True, required=True
            ),
        'vehicle_id': fields.many2one(
            'l10n_br_delivery.carrier.vehicle',
            u'Veículo',
            select=True,
            required=True,
            ),
        'volume': fields.float(u'Volume'),
        'carrier_tracking_ref': fields.char(
            u'Referência de Rastreamento da Transportadora', size=32
            ),
        'number_of_packages': fields.integer(u'Número de Pacotes'),
        }

    def _cal_weight(self, cr, uid, ids, name, args, context=None):
        res = {}
        uom_obj = self.pool.get('product.uom')
        for picking in self.browse(cr, uid, ids, context):
            total_weight = total_weight_net = 0.00

            for move in picking.move_lines:
                total_weight += move.weight
                total_weight_net += move.weight_net

            res[picking.id] = {
                                'weight': total_weight,
                                'weight_net': total_weight_net,
                              }
        return res

    def _get_picking_line(self, cr, uid, ids, context=None):
            result = {}
            for line in self.pool.get('stock.move').browse(cr, uid, ids,
                                                           context=context):
                result[line.picking_id.id] = True
            return result.keys()

l10n_br_delivery_shipment()
