# -*- encoding: utf-8 -*-
###############################################################################
#                                                                             #
# Copyright (C) 2009  Renato Lima - Akretion, Gabriel C. Stabel               #
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


class sale_order(orm.Model):
    _inherit = 'sale.order'

    def onchange_fiscal_category_id(self, cr, uid, ids, partner_id,
                                    partner_invoice_id=False, shop_id=False,
                                    fiscal_category_id=False, context=None):

        result = {'value': {'fiscal_position': False}}

        if not shop_id or not partner_id or not fiscal_category_id:
            return result

        obj_shop = self.pool.get('sale.shop').browse(cr, uid, shop_id)
        company_id = obj_shop.company_id.id
        context.update({'use_domain': ('use_sale', '=', True)})
        kwargs = {
            'partner_id': partner_id,
            'partner_invoice_id': partner_invoice_id,
            'company_id': company_id,
            'context': context
        }
        fp_rule_obj = self.pool.get('account.fiscal.position.rule')
        return fp_rule_obj.apply_fiscal_mapping(cr, uid, result, kwargs)
    
    def onchange_partner_id(self, cr, uid, ids, partner_id, context=None):
        return super(sale_order, self).onchange_partner_id(
            cr, uid, ids, partner_id, context)

    def onchange_address_id(self, cr, uid, ids, partner_invoice_id,
                            partner_shipping_id, partner_id,
                            shop_id=None, context=None,
                            fiscal_category_id=None, **kwargs):
        return super(sale_order, self).onchange_address_id(
            cr, uid, ids, partner_invoice_id, partner_shipping_id,
            partner_id, shop_id, context,
            fiscal_category_id=fiscal_category_id)

    def onchange_shop_id(self, cr, uid, ids, shop_id=None, context=None,
                         partner_id=None, partner_invoice_id=None,
                         partner_shipping_id=None,
                         fiscal_category_id=None, **kwargs):
        return super(sale_order, self).onchange_shop_id(
            cr, uid, ids, shop_id, context, partner_id, partner_invoice_id,
            partner_shipping_id, fiscal_category_id=fiscal_category_id)
    
class sale_order_line(orm.Model):
    _inherit = 'sale.order.line'
    
    
    def _fiscal_position_map(self, cr, uid, result, **kwargs):

        kwargs['context'].update({'use_domain': ('use_sale', '=', True)})
        obj_shop = self.pool.get('sale.shop').browse(
            cr, uid, kwargs.get('shop_id'))
        company_id = obj_shop.company_id.id
        kwargs.update({'company_id': company_id})
        fp_rule_obj = self.pool.get('account.fiscal.position.rule')

        return fp_rule_obj.apply_fiscal_mapping(cr, uid, result, kwargs)

    def product_id_change(self, cr, uid, ids, pricelist, product, qty=0,
                          uom=False, qty_uos=0, uos=False, name='',
                          partner_id=False, lang=False, update_tax=True,
                          date_order=False, packaging=False,
                          fiscal_position=False, flag=False, context=None,
                          parent_fiscal_category_id=False, shop_id=False,
                          parent_fiscal_position=False,
                          partner_invoice_id=False, **kwargs):

        result = super(sale_order_line, self).product_id_change(
            cr, uid, ids, pricelist, product, qty, uom, qty_uos, uos, name,
            partner_id, lang, update_tax, date_order, packaging,
            fiscal_position, flag, context)

        if not parent_fiscal_category_id or not product or not partner_invoice_id:
            return result

        obj_fp_rule = self.pool.get('account.fiscal.position.rule')
        product_fiscal_category_id = obj_fp_rule.product_fiscal_category_map(
            cr, uid, product, parent_fiscal_category_id)

        if product_fiscal_category_id:
            parent_fiscal_category_id = product_fiscal_category_id

        result['value']['fiscal_category_id'] = parent_fiscal_category_id

        kwargs = {
            'shop_id': shop_id,
            'partner_id': partner_id,
            'partner_invoice_id': partner_invoice_id,
            'fiscal_category_id': parent_fiscal_category_id,
            'context': context
        }
        return self._fiscal_position_map(cr, uid, result, **kwargs)

    def onchange_fiscal_category_id(self, cr, uid, ids, partner_id,
                                        partner_invoice_id=False,
                                        shop_id=False, product_id=False,
                                        fiscal_category_id=False,
                                        context=None):

        if not context:
            context = {}

        result = {'value': {}}

        if not shop_id or not partner_id or not fiscal_category_id:
            return result

        kwargs = {
            'shop_id': shop_id,
            'partner_id': partner_id,
            'partner_invoice_id': partner_invoice_id,
            'fiscal_category_id': fiscal_category_id,
            'context': context
        }
        return self._fiscal_position_map(cr, uid, result, **kwargs)

    def onchange_fiscal_position(self, cr, uid, ids, partner_id,
                                 partner_invoice_id=False, shop_id=False,
                                 product_id=False, fiscal_position=False,
                                 fiscal_category_id=False):

        result = {'value': {'tax_id': False}}
        if not shop_id or not partner_id or not fiscal_position:
            return result

        if product_id:
            obj_fposition = self.pool.get('account.fiscal.position').browse(
                cr, uid, fiscal_position)
            obj_product = self.pool.get('product.product').browse(
                cr, uid, product_id)
            context = {'fiscal_type': obj_product.fiscal_type,
                       'type_tax_use': 'sale'}
            taxes = obj_product.taxes_id or False
            tax_ids = self.pool.get('account.fiscal.position').map_tax(
                cr, uid, obj_fposition, taxes, context)

            result['value']['tax_id'] = tax_ids

        kwargs = {
            'shop_id': shop_id,
            'partner_id': partner_id,
            'partner_invoice_id': partner_invoice_id,
            'fiscal_category_id': fiscal_category_id,
            'context': {}
        }
        return self._fiscal_position_map(cr, uid, result, **kwargs)