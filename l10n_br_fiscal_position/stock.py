# -*- encoding: utf-8 -*-
###############################################################################
#                                                                             #
# Copyright (C) 2009  Renato Lima - Akretion                                  #
# Copyright (C) 2012  Raphaël Valyi - Akretion                                #
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

from openerp.osv import orm, fields

class stock_picking(orm.Model):
    _inherit = 'stock.picking'
    
    def onchange_partner_in(self, cr, uid, ids, partner_id=None,
                            company_id=None, context=None,
                            fiscal_category_id=None):
        if not context:
            context = {}

        return super(stock_picking, self).onchange_partner_in(
            cr, uid, ids, partner_id=partner_id, company_id=company_id,
            context=context, fiscal_category_id=fiscal_category_id)

    def onchange_fiscal_category_id(self, cr, uid, ids,
                                    partner_id, company_id=False,
                                    fiscal_category_id=False,
                                    context=None, **kwargs):
        if not context:
            context = {}

        result = {'value': {'fiscal_position': False}}

        if not partner_id or not company_id:
            return result

        partner_invoice_id = self.pool.get('res.partner').address_get(
            cr, uid, [partner_id], ['invoice'])['invoice']
        partner_shipping_id = self.pool.get('res.partner').address_get(
            cr, uid, [partner_id], ['delivery'])['delivery']

        kwargs = {
           'partner_id': partner_id,
           'partner_invoice_id': partner_invoice_id,
           'partner_shipping_id': partner_shipping_id,
           'company_id': company_id,
           'context': context,
           'fiscal_category_id': fiscal_category_id
        }
        return self._fiscal_position_map(cr, uid, result, **kwargs)
    
    
    def _get_fiscal_data(self, cr, uid, move_line, fiscal_category):
        return self._fiscal_position_map(
                cr, uid, move_line.picking_id.partner_id.id,
                move_line.picking_id.address_id.id,
                move_line.picking_id.company_id.id,
                fiscal_category.id)
    

    def onchange_company_id(self, cr, uid, ids, partner_id, company_id=False,
                            fiscal_category_id=False, context=None, **kwargs):
        if not context:
            context = {}

        result = {'value': {'fiscal_position': False}}

        if not partner_id or not company_id:
            return result

        partner_invoice_id = self.pool.get('res.partner').address_get(
            cr, uid, [partner_id], ['invoice'])['invoice']
        partner_shipping_id = self.pool.get('res.partner').address_get(
            cr, uid, [partner_id], ['delivery'])['delivery']

        kwargs = {
           'partner_id': partner_id,
           'partner_invoice_id': partner_invoice_id,
           'partner_shipping_id': partner_shipping_id,
           'company_id': company_id,
           'context': context,
           'fiscal_category_id': fiscal_category_id
        }
        return self._fiscal_position_map(cr, uid, result, **kwargs)
    
class stock_picking_in(stock_picking):
    _inherit = 'stock.picking.in'
    
    def _fiscal_position_map(self, cr, uid, result, **kwargs):
        kwargs['context'].update({'use_domain': ('use_picking', '=', True)})
        fp_rule_obj = self.pool.get('account.fiscal.position.rule')
        return fp_rule_obj.apply_fiscal_mapping(cr, uid, result, kwargs)
    
    
    def onchange_partner_in(self, cr, uid, ids, partner_id=None,
                            company_id=None, context=None,
                            fiscal_category_id=None):

        result = super(stock_picking, self).onchange_partner_in(
            cr, uid, partner_id, context)

        if not result:
            result = {'value': {'fiscal_position': False}}

        if not partner_id or not company_id:
            return result

        partner_invoice_id = self.pool.get('res.partner').address_get(
            cr, uid, [partner_id], ['invoice'])['invoice']
        partner_shipping_id = self.pool.get('res.partner').address_get(
            cr, uid, [partner_id], ['delivery'])['delivery']

        kwargs = {
           'partner_id': partner_id,
           'partner_invoice_id': partner_invoice_id,
           'partner_shipping_id': partner_shipping_id,
           'company_id': company_id,
           'fiscal_category_id': fiscal_category_id,
           'context': context
        }
        return self._fiscal_position_map(cr, uid, result, **kwargs)

class stock_picking_out(stock_picking):
    _inherit = 'stock.picking.out'

    def _fiscal_position_map(self, cr, uid, result, **kwargs):
        kwargs['context'].update({'use_domain': ('use_picking', '=', True)})
        fp_rule_obj = self.pool.get('account.fiscal.position.rule')
        return fp_rule_obj.apply_fiscal_mapping(cr, uid, result, kwargs)

    def onchange_partner_in(self, cr, uid, ids, partner_id=None,
                            company_id=None, context=None,
                            fiscal_category_id=None):

        result = super(stock_picking, self).onchange_partner_in(
            cr, uid, partner_id, context)

        if not result:
            result = {'value': {'fiscal_position': False}}

        if not partner_id or not company_id:
            return result

        partner_invoice_id = self.pool.get('res.partner').address_get(
            cr, uid, [partner_id], ['invoice'])['invoice']
        partner_shipping_id = self.pool.get('res.partner').address_get(
            cr, uid, [partner_id], ['delivery'])['delivery']

        kwargs = {
           'partner_id': partner_id,
           'partner_invoice_id': partner_invoice_id,
           'partner_shipping_id': partner_shipping_id,
           'company_id': company_id,
           'fiscal_category_id': fiscal_category_id,
           'context': context
        }
        return self._fiscal_position_map(cr, uid, result, **kwargs)