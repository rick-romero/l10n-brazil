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


class purchase_order(orm.Model):
    _inherit = 'purchase.order'

    def onchange_partner_id(self, cr, uid, ids, partner_id=False,
                            company_id=False, context=None,
                            fiscal_category_id=False, **kwargs):
        return super(purchase_order, self).onchange_partner_id(
            cr, uid, ids, partner_id, company_id, context=None,
            fiscal_category_id=fiscal_category_id)

    def onchange_dest_address_id(self, cr, uid, ids, partner_id,
                                 dest_address_id, company_id, context,
                                 fiscal_category_id, **kwargs):
        return super(purchase_order, self).onchange_dest_address_id(
            cr, uid, ids, partner_id, dest_address_id, company_id, context,
            fiscal_category_id=fiscal_category_id)

    def onchange_company_id(self, cr, uid, ids, partner_id,
                                 dest_address_id, company_id, context,
                                 fiscal_category_id, **kwargs):
        return super(purchase_order, self).onchange_company_id(
            cr, uid, ids, partner_id, dest_address_id, company_id, context,
            fiscal_category_id=fiscal_category_id)

    def onchange_fiscal_category_id(self, cr, uid, ids, partner_id=False,
                                    dest_address_id=False, company_id=False,
                                    context=None, fiscal_category_id=False,
                                    **kwargs):
        if not context:
            context = {}

        result = {'value': {'fiscal_position': False}}

        if not partner_id or not company_id:
            return result

        kwargs.update({
            'company_id': company_id,
            'partner_id': partner_id,
            'partner_invoice_id': partner_id,
            'partner_shipping_id': dest_address_id,
            'context': context
        })
        return self._fiscal_position_map(cr, uid, result, **kwargs)

class purchase_order_line(orm.Model):
    _inherit = 'purchase.order.line'


    def _fiscal_position_map(self, cr, uid, result, **kwargs):

        kwargs['context'].update({'use_domain': ('use_purchase', '=', True)})
        fp_rule_obj = self.pool.get('account.fiscal.position.rule')
        result_rule = fp_rule_obj.apply_fiscal_mapping(cr, uid, result, kwargs)
        if kwargs.get('product_id', False) and \
        result_rule.get('fiscal_position', False):
            obj_fposition = self.pool.get('account.fiscal.position').browse(
                cr, uid, result_rule['fiscal_position'])
            obj_product = self.pool.get('product.product').browse(
                cr, uid, kwargs.get('product_id', False))
            kwargs['context'].update({'fiscal_type': obj_product.fiscal_type,
                            'type_tax_use': 'purchase'})
            taxes = obj_product.supplier_taxes_id or False
            tax_ids = self.pool.get('account.fiscal.position').map_tax(
                cr, uid, obj_fposition, taxes, kwargs.get('context'))

            result_rule['taxes_id'] = tax_ids

        return result_rule

    def product_id_change(self, cr, uid, ids, pricelist_id, product_id, qty,
                          uom_id, partner_id, date_order=False,
                          fiscal_position_id=False, date_planned=False,
                          name=False, price_unit=False, context=None,
                          company_id=False, parent_fiscal_position_id=False,
                          parent_fiscal_category_id=False, **kwargs):

        if context is None:
            context = {}

        result = super(purchase_order_line, self).product_id_change(
            cr, uid, ids, pricelist_id, product_id, qty, uom_id, partner_id,
            date_order, fiscal_position_id, date_planned, name, price_unit,
            context)

        if not product_id or not parent_fiscal_category_id:
            return result

        obj_fp_rule = self.pool.get('account.fiscal.position.rule')
        product_fiscal_category_id = obj_fp_rule.product_fiscal_category_map(
            cr, uid, product_id, parent_fiscal_category_id)

        if product_fiscal_category_id:
            parent_fiscal_category_id = product_fiscal_category_id

        result['value']['fiscal_category_id'] = parent_fiscal_category_id

        kwargs.update({
            'company_id': company_id,
            'product_id': product_id,
            'partner_id': partner_id,
            'partner_invoice_id': partner_id,
            'fiscal_category_id': parent_fiscal_category_id,
            'context': context,
        })
        return self._fiscal_position_map(cr, uid, result, **kwargs)

    def onchange_fiscal_category_id(self, cr, uid, ids, partner_id,
                                        dest_address_id=False,
                                        product_id=False,
                                        fiscal_category_id=False,
                                        company_id=False, context=None,
                                        **kwargs):
        result = {'value': {}}
        if not company_id or not partner_id:
            return result

        kwargs.update({
            'company_id': company_id,
            'product_id': product_id,
            'partner_id': partner_id,
            'partner_invoice_id': partner_id,
            'fiscal_category_id': fiscal_category_id,
            'context': context,
        })
        return self._fiscal_position_map(cr, uid, result, **kwargs)

    def onchange_fiscal_position(self, cr, uid, ids, partner_id,
                                 dest_address_id=False, product_id=False,
                                 fiscal_position=False,
                                 fiscal_category_id=False, company_id=False,
                                 context=None, **kwargs):
        result = {'value': {}}
        if not company_id or not partner_id or not fiscal_position:
            return result

        kwargs.update({
            'company_id': company_id,
            'product_id': product_id,
            'partner_id': partner_id,
            'partner_invoice_id': partner_id,
            'fiscal_category_id': fiscal_category_id,
            'context': context,
        })
        return self._fiscal_position_map(cr, uid, result, **kwargs)