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
from openerp.tools.translate import _
from openerp.addons import decimal_precision as dp


class purchase_order(orm.Model):
    _inherit = 'purchase.order'

    def _amount_all(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        cur_obj = self.pool.get('res.currency')
        for order in self.browse(cr, uid, ids, context=context):
            res[order.id] = {
                'amount_untaxed': 0.0,
                'amount_tax': 0.0,
                'amount_total': 0.0,
            }
            val = val1 = 0.0
            cur = order.pricelist_id.currency_id
            for line in order.order_line:
                val1 += line.price_subtotal

                for c in self.pool.get('account.tax').compute_all(
                    cr, uid, line.taxes_id, line.price_unit, line.product_qty,
                    line.product_id.id, order.partner_id,
                    fiscal_position=line.fiscal_position)['taxes']:

                    tax_brw = self.pool.get('account.tax').browse(
                        cr, uid, c['id'])
                    if not tax_brw.tax_code_id.tax_discount:
                        val += c.get('amount', 0.0)
            res[order.id]['amount_tax'] = cur_obj.round(cr, uid, cur, val)
            res[order.id]['amount_untaxed'] = cur_obj.round(cr, uid, cur, val1)
            res[order.id]['amount_total'] = res[order.id]['amount_untaxed'] + res[order.id]['amount_tax']
        return res

    def _get_order(self, cr, uid, ids, context=None):
        result = {}
        for line in self.pool.get('purchase.order.line').browse(
            cr, uid, ids, context=context):
            result[line.order_id.id] = True
        return result.keys()

    def _default_fiscal_category(self, cr, uid, context=None):
        user = self.pool.get('res.users').browse(cr, uid, uid, context=context)
        return user.company_id.purchase_fiscal_category_id and \
        user.company_id.purchase_fiscal_category_id.id or False

    _columns = {
        'fiscal_category_id': fields.many2one(
            'l10n_br_account.fiscal.category', 'Categoria Fiscal',
            domain="[('type', '=', 'input'), \
            ('journal_type', '=', 'purchase')]"),
        'amount_untaxed': fields.function(
            _amount_all, method=True,
            digits_compute=dp.get_precision('Purchase Price'),
            string='Untaxed Amount',
            store={'purchase.order.line': (_get_order, None, 10)},
            multi="sums", help="The amount without tax"),
        'amount_tax': fields.function(
            _amount_all, method=True,
            digits_compute=dp.get_precision('Purchase Price'), string='Taxes',
            store={'purchase.order.line': (_get_order, None, 10)},
            multi="sums", help="The tax amount"),
        'amount_total': fields.function(
            _amount_all, method=True,
            digits_compute=dp.get_precision('Purchase Price'), string='Total',
            store={'purchase.order.line': (_get_order, None, 10)},
            multi="sums", help="The total amount")}

    _defaults = {
        'fiscal_category_id': _default_fiscal_category}

    def _prepare_inv_line(self, cr, uid, account_id, order_line, context=None):

        result = super(purchase_order, self)._prepare_inv_line(
            cr, uid, account_id, order_line, context)

        order = order_line.order_id

        result['fiscal_category_id'] = order_line.fiscal_category_id and \
        order_line.fiscal_category_id.id or order.fiscal_category_id and \
        order.fiscal_category_id.id

        result['fiscal_position'] = order_line.fiscal_position and \
        order_line.fiscal_position.id or order.fiscal_position and \
        order.fiscal_position.id

        result['cfop_id'] = order.fiscal_position and \
        order.fiscal_position.cfop_id and order.fiscal_position.cfop_id.id or \
        order.fiscal_position and order.fiscal_position.cfop_id and \
        order.fiscal_position.cfop_id.id

        result['partner_id'] = order_line.partner_id.id
        result['company_id'] = order_line.company_id.id

        return result

    # TODO ask OpenERP SA for a _prepare_invoice method!
    def action_invoice_create(self, cr, uid, ids, *args):
        inv_id = super(purchase_order, self).action_invoice_create(cr, uid,
                                                                   ids, *args)
        for order in self.browse(cr, uid, ids):
            # REMARK: super method is ugly as it assumes only one invoice
            # for possibly several purchase orders.
            if inv_id:
                company_id = order.company_id
                if not company_id.document_serie_product_ids:
                    raise orm.except_orm(
                        _('No fiscal document serie found!'),
                        _("No fiscal document serie found for selected \
                        company %s") % (order.company_id.name))

                journal_id = order.fiscal_category_id and \
                order.fiscal_category_id.property_journal.id or False

                if not journal_id:
                    raise orm.except_orm(
                        _(u'Nenhuma Diário!'),
                        _(u"Categoria de operação fisca: '%s', não tem um \
                        diário contábil para a empresa %s") % (
                            order.fiscal_category_id.name,
                            order.company_id.name))

                comment = ''
                if order.fiscal_position and order.fiscal_position.inv_copy_note:
                    comment = order.fiscal_position.note or ''
                if order.notes:
                    comment += ' - ' + order.notes

                self.pool.get('account.invoice').write(cr, uid, inv_id, {
                     'fiscal_category_id': order.fiscal_category_id and
                     order.fiscal_category_id.id,
                     'fiscal_position': order.fiscal_position and
                     order.fiscal_position.id,
                     'issuer': '1',
                     'comment': comment,
                     'journal_id': journal_id})
        return inv_id

    def action_picking_create(self, cr, uid, ids, *args):
        picking_id = False
        for order in self.browse(cr, uid, ids):
            picking_id = super(purchase_order, self).action_picking_create(
                cr, uid, ids, *args)
            self.pool.get('stock.picking').write(
                cr, uid, picking_id,
                {'fiscal_category_id': order.fiscal_category_id.id,
                 'fiscal_position': order.fiscal_position.id})
        return picking_id


class purchase_order_line(orm.Model):
    _inherit = 'purchase.order.line'
    _columns = {
        'fiscal_category_id': fields.many2one(
            'l10n_br_account.fiscal.category', 'Categoria Fiscal',
            domain="[('type', '=', 'input'), \
            ('journal_type', '=', 'purchase')]"),
        'fiscal_position': fields.many2one(
            'account.fiscal.position', u'Posição Fiscal',
            domain="[('fiscal_category_id', '=', fiscal_category_id)]")
    }

    
