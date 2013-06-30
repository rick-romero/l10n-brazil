# -*- encoding: utf-8 -*-
###############################################################################
#                                                                             #
# Copyright (C) 2009  Renato Lima - Akretion                                  #
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

class account_invoice(orm.Model):
    _inherit = 'account.invoice'

    def onchange_partner_id(self, cr, uid, ids, type, partner_id,
                            date_invoice=False, payment_term=False,
                            partner_bank_id=False, company_id=False,
                            fiscal_category_id=False):

        result = super(account_invoice, self).onchange_partner_id(
            cr, uid, ids, type, partner_id, date_invoice, payment_term,
            partner_bank_id, company_id)

        return self._fiscal_position_map(
            cr, uid, result, False, partner_id=partner_id,
            partner_invoice_id=partner_id, company_id=company_id,
            fiscal_category_id=fiscal_category_id)

    def onchange_company_id(self, cr, uid, ids, company_id, partner_id, type,
                            invoice_line, currency_id,
                            fiscal_category_id=False):

        result = super(account_invoice, self).onchange_company_id(
            cr, uid, ids, company_id, partner_id, type, invoice_line,
            currency_id)

        return self._fiscal_position_map(
            cr, uid, result, False, partner_id=partner_id,
            partner_invoice_id=partner_id, company_id=company_id,
            fiscal_category_id=fiscal_category_id)

    def onchange_fiscal_category_id(self, cr, uid, ids,
                                    partner_address_id=False,
                                    partner_id=False, company_id=False,
                                    fiscal_category_id=False):
        result = {'value': {}}
        return self._fiscal_position_map(
            cr, uid, result, False, partner_id=partner_id,
            partner_invoice_id=partner_id, company_id=company_id,
            fiscal_category_id=fiscal_category_id)
    
    def _fiscal_position_map(self, cr, uid, result, context=None, **kwargs):

        if not context:
            context = {}
        context.update({'use_domain': ('use_invoice', '=', True)})
        kwargs.update({'context': context})

        if not kwargs.get('fiscal_category_id', False):
            return result

        obj_company = self.pool.get('res.company').browse(
            cr, uid, kwargs.get('company_id', False))
        obj_fcategory = self.pool.get('l10n_br_account.fiscal.category')

        fcategory = obj_fcategory.browse(
            cr, uid, kwargs.get('fiscal_category_id'))
        result['value']['journal_id'] = fcategory.property_journal and \
        fcategory.property_journal.id or False
        if not result['value'].get('journal_id', False):
            raise orm.except_orm(
                _('Nenhum Diário !'),
                _("Categoria fiscal: '%s', não tem um diário contábil para a \
                empresa %s") % (fcategory.name, obj_company.name))

        obj_fp_rule = self.pool.get('account.fiscal.position.rule')
        return obj_fp_rule.apply_fiscal_mapping(cr, uid, result, kwargs)


class account_invoice_line(orm.Model):
    _inherit = 'account.invoice.line'
    
    def _fiscal_position_map(self, cr, uid, result, context=None, **kwargs):

        if not context:
            context = {}
        context.update({'use_domain': ('use_invoice', '=', True)})
        kwargs.update({'context': context})
        result['value']['cfop_id'] = False
        obj_fp_rule = self.pool.get('account.fiscal.position.rule')
        result_rule = obj_fp_rule.apply_fiscal_mapping(
            cr, uid, result, kwargs)
        if result['value'].get('fiscal_position', False):
            obj_fp = self.pool.get('account.fiscal.position').browse(
                cr, uid, result['value'].get('fiscal_position', False))
            result_rule['value']['cfop_id'] = obj_fp.cfop_id and obj_fp.cfop_id.id or False
            if kwargs.get('product_id', False):
                obj_product = self.pool.get('product.product').browse(
                cr, uid, kwargs.get('product_id', False), context=context)
                context['fiscal_type'] = obj_product.fiscal_type
                if context.get('type') in ('out_invoice', 'out_refund'):
                    context['type_tax_use'] = 'sale'
                    taxes = obj_product.taxes_id and obj_product.taxes_id or (kwargs.get('account_id', False) and self.pool.get('account.account').browse(cr, uid, kwargs.get('account_id', False), context=context).tax_ids or False)
                else:
                    context['type_tax_use'] = 'purchase'
                    taxes = obj_product.supplier_taxes_id and obj_product.supplier_taxes_id or (kwargs.get('account_id', False) and self.pool.get('account.account').browse(cr, uid, kwargs.get('account_id', False), context=context).tax_ids or False)
                tax_ids = self.pool.get('account.fiscal.position').map_tax(
                    cr, uid, obj_fp, taxes, context)

                result_rule['value']['invoice_line_tax_id'] = tax_ids

                result['value'].update(self._get_tax_codes(
                    cr, uid, kwargs.get('product_id'),
                    obj_fp, tax_ids, kwargs.get('company_id'),
                    context=context))

        return result_rule
    
    def product_id_change(self, cr, uid, ids, product, uom, qty=0, name='',
                          type='out_invoice', partner_id=False,
                          fposition_id=False, price_unit=False,
                          currency_id=False, context=None, company_id=False,
                          parent_fiscal_category_id=False,
                          parent_fposition_id=False):

        result = super(account_invoice_line, self).product_id_change(
            cr, uid, ids, product, uom, qty, name, type, partner_id,
            fposition_id, price_unit, currency_id, context, company_id)

        fiscal_position = fposition_id or parent_fposition_id or False

        if not parent_fiscal_category_id or not product or not fiscal_position:
            return result
        obj_fp_rule = self.pool.get('account.fiscal.position.rule')
        product_fiscal_category_id = obj_fp_rule.product_fiscal_category_map(
            cr, uid, product, parent_fiscal_category_id)

        if product_fiscal_category_id:
            parent_fiscal_category_id = product_fiscal_category_id

        result['value']['fiscal_category_id'] = parent_fiscal_category_id

        result = self._fiscal_position_map(cr, uid, result, context,
            partner_id=partner_id, partner_invoice_id=partner_id,
            company_id=company_id, product_id=product,
            fiscal_category_id=parent_fiscal_category_id,
            account_id=result['value'].get('account_id'))

        values = {
            'partner_id': partner_id,
            'company_id': company_id,
            'product_id': product,
            'quantity': qty,
            'price_unit': price_unit,
            'fiscal_position': result['value'].get('fiscal_position'),
            'invoice_line_tax_id': [[6, 0, result['value'].get('invoice_line_tax_id')]],
        }
        result['value'].update(self._validate_taxes(cr, uid, values, context))
        return result

    def onchange_fiscal_category_id(self, cr, uid, ids, partner_id,
                                    company_id, product_id, fiscal_category_id,
                                    account_id, context):
        result = {'value': {}}
        return self._fiscal_position_map(
            cr, uid, result, context, partner_id=partner_id,
            partner_invoice_id=partner_id, company_id=company_id,
            fiscal_category_id=fiscal_category_id, product_id=product_id,
            account_id=account_id)

    def onchange_fiscal_position(self, cr, uid, ids, partner_id, company_id,
                                product_id, fiscal_category_id,
                                account_id, context):
        result = {'value': {}}
        return self._fiscal_position_map(
            cr, uid, result, context, partner_id=partner_id,
            partner_invoice_id=partner_id, company_id=company_id,
            fiscal_category_id=fiscal_category_id, product_id=product_id,
            account_id=account_id)

    def onchange_account_id(self, cr, uid, ids, product_id, partner_id,
                            inv_type, fposition_id, account_id=False,
                            context=None, fiscal_category_id=False,
                            company_id=False):

        result = super(account_invoice_line, self).onchange_account_id(
            cr, uid, ids, product_id, partner_id, inv_type, fposition_id,
            account_id)
        return self._fiscal_position_map(
            cr, uid, result, context, partner_id=partner_id,
            partner_invoice_id=partner_id, company_id=company_id,
            fiscal_category_id=fiscal_category_id, product_id=product_id,
            account_id=account_id)

    def uos_id_change(self, cr, uid, ids, product, uom, qty=0, name='',
                    type='out_invoice', partner_id=False, fposition_id=False,
                    price_unit=False, currency_id=False, context=None,
                    company_id=None, fiscal_category_id=False):

        result = super(account_invoice_line, self).uos_id_change(
            cr, uid, ids, product, uom, qty, name, type, partner_id,
            fposition_id, price_unit, currency_id, context, company_id)
        return self._fiscal_position_map(
            cr, uid, result, context, partner_id=partner_id,
            partner_invoice_id=partner_id, company_id=company_id,
            fiscal_category_id=fiscal_category_id, product_id=product,
            account_id=False)

    def _get_tax_codes(self, cr, uid, product_id, fiscal_position,
                        taxes, company_id, context=None):

        if not context:
            context = {}

        result = {}

        if fiscal_position.fiscal_category_id.journal_type in ('sale', 'sale_refund'):
            context['type_tax_use'] = 'sale'
        else:
            context['type_tax_use'] = 'purchase'

        context['fiscal_type'] = fiscal_position.fiscal_category_fiscal_type

        tax_codes = self.pool.get('account.fiscal.position').map_tax_code(
            cr, uid, product_id, fiscal_position, company_id,
            taxes, context=context)

        result['icms_cst_id'] = tax_codes.get('icms', False)
        result['ipi_cst_id'] = tax_codes.get('ipi', False)
        result['pis_cst_id'] = tax_codes.get('pis', False)
        result['cofins_cst_id'] = tax_codes.get('cofins', False)
        return result

    def _validate_taxes(self, cr, uid, values, context=None):
        """Verifica se o valor dos campos dos impostos estão sincronizados
        com os impostos do OpenERP"""
        if not context:
            context = {}

        tax_obj = self.pool.get('account.tax')

        if not values.get('product_id') or not values.get('quantity') \
        or not values.get('fiscal_position'):
            return {}

        result = {
            'product_type': 'product',
            'service_type_id': False,
            'fiscal_classification_id': False
        }

        if values.get('partner_id') and values.get('company_id'):
            partner_id = values.get('partner_id')
            company_id = values.get('company_id')
        else:
            if values.get('invoice_id'):
                inv = self.pool.get('account.invoice').read(
                    cr, uid, values.get('invoice_id'),
                    ['partner_id', 'company_id'])

                partner_id = inv.get('partner_id', [False])[0]
                company_id = inv.get('company_id', [False])[0]

        taxes = tax_obj.browse(
            cr, uid, values.get('invoice_line_tax_id')[0][2])
        fiscal_position = self.pool.get('account.fiscal.position').browse(
            cr, uid, values.get('fiscal_position'))

        price_unit = values.get('price_unit', 0.0)
        price = price_unit * (1 - values.get('discount', 0.0) / 100.0)

        taxes_calculed = tax_obj.compute_all(
            cr, uid, taxes, price, values.get('quantity', 0.0),
            values.get('product_id'), partner_id,
            fiscal_position=fiscal_position,
            insurance_value=values.get('insurance_value', 0.0),
            freight_value=values.get('freight_value', 0.0),
            other_costs_value=values.get('other_costs_value', 0.0))

        if values.get('product_id'):
            obj_product = self.pool.get('product.product').browse(
                cr, uid, values.get('product_id'), context=context)
            if obj_product.type == 'service':
                result['product_type'] = 'service'
                result['service_type_id'] = obj_product.service_type_id.id
            else:
                result['product_type'] = 'product'
            if obj_product.property_fiscal_classification:
                result['fiscal_classification_id'] = obj_product.property_fiscal_classification.id

            result['icms_origin'] = obj_product.origin

        for tax in taxes_calculed['taxes']:
            try:
                amount_tax = getattr(
                    self, '_amount_tax_%s' % tax.get('domain', ''))
                result.update(amount_tax(cr, uid, tax))
            except AttributeError:
                # Caso não exista campos especificos dos impostos
                # no documento fiscal, os mesmos são calculados.
                continue

        result.update(self._get_tax_codes(
            cr, uid, values.get('product_id'), fiscal_position,
            values.get('invoice_line_tax_id')[0][2],
            company_id, context=context))
        return result
