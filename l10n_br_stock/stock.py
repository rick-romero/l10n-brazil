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
from openerp.tools.translate import _


class stock_incoterms(orm.Model):
    _inherit = 'stock.incoterms'
    _columns = {
        'freight_responsibility': fields.selection(
            [('0', 'Emitente'),
            ('1', u'Destinatário'),
            ('2', 'Terceiros'),
            ('9', 'Sem Frete')],
            'Frete por Conta', required=True)
    }
    _defaults = {
        'freight_responsibility': 0
    }


class stock_picking(orm.Model):
    _inherit = 'stock.picking'

    def _default_fiscal_category(self, cr, uid, context=None):
        user = self.pool.get('res.users').browse(
            cr, uid, uid, context=context)
        return user.company_id.stock_fiscal_category_id and \
        user.company_id.stock_fiscal_category_id.id or False

    _columns = {
        'fiscal_category_id': fields.many2one(
            'l10n_br_account.fiscal.category', 'Categoria Fiscal'),
        'fiscal_position': fields.many2one(
            'account.fiscal.position', u'Posição Fiscal',
            domain="[('fiscal_category_id','=',fiscal_category_id)]")
    }
    _defaults = {
        'fiscal_category_id': _default_fiscal_category
    }

    
    def _get_fiscal_data(self, cr, uid, move_line, fiscal_category):
        ''' Reserved method for getting fiscal data from account.fiscal.position.rule.stock '''
        return []

    def _prepare_invoice_line(self, cr, uid, group, picking, move_line,
                              invoice_id, invoice_vals, context=None):
        result = super(stock_picking, self)._prepare_invoice_line(
            cr, uid, group, picking, move_line, invoice_id, invoice_vals,
            context)
        if move_line.sale_line_id:
            fiscal_position = move_line.sale_line_id.fiscal_position or \
            move_line.sale_line_id.order_id.fiscal_position
            fiscal_category_id = move_line.sale_line_id.fiscal_category_id or \
            move_line.sale_line_id.order_id.fiscal_category_id
            refund_fiscal_category = fiscal_category_id.refund_fiscal_category_id or False
        elif move_line.purchase_line_id:
            fiscal_position = move_line.purchase_line_id.fiscal_position or \
            move_line.purchase_line_id.order_id.fiscal_position
            fiscal_category_id = move_line.purchase_line_id.fiscal_category_id or move_line.purchase_line_id.order_id.fiscal_category_id
            refund_fiscal_category = fiscal_category_id.refund_fiscal_category_id or False
        else:
            fiscal_position = move_line.picking_id.fiscal_position
            fiscal_category_id = move_line.picking_id.fiscal_category_id

        if context.get('inv_type') in ('in_refund', 'out_refund'):
            if not refund_fiscal_category:
                raise orm.except_orm(
                    _('Error!'),
                    _("This Fiscal Operation does not has Fiscal Operation \
                    for Returns!"))

            fiscal_category_id = refund_fiscal_category
            fiscal_data = self._get_fiscal_data(cr, uid, move_line, fiscal_category_id)
            

            fiscal_position = self.pool.get('account.fiscal.position').browse(
                cr, uid, fiscal_data.get('fiscal_position', 0))

        result['cfop_id'] = fiscal_position and \
        fiscal_position.cfop_id and fiscal_position.cfop_id.id
        result['fiscal_category_id'] = fiscal_category_id and \
        fiscal_category_id.id
        result['fiscal_position'] = fiscal_position and \
        fiscal_position.id

        result['partner_id'] = picking.partner_id.id
        result['company_id'] = picking.company_id.id

        return result

    def _prepare_invoice(self, cr, uid, picking, partner,
                        inv_type, journal_id, context=None):
        result = super(stock_picking, self)._prepare_invoice(
            cr, uid, picking, partner, inv_type, journal_id, context)

        comment = ''
        if picking.fiscal_position and picking.fiscal_position.inv_copy_note:
            comment += picking.fiscal_position.note or ''

        if picking.note:
            comment += ' - ' + picking.note

        result['comment'] = comment
        result['fiscal_category_id'] = picking.fiscal_category_id and \
        picking.fiscal_category_id.id
        result['fiscal_position'] = picking.fiscal_position and \
        picking.fiscal_position.id
        return result


class stock_picking_in(stock_picking):
    _inherit = 'stock.picking.in'

    def _default_fiscal_category(self, cr, uid, context=None):
        user = self.pool.get('res.users').browse(
            cr, uid, uid, context=context)
        return user.company_id.stock_in_fiscal_category_id and \
        user.company_id.stock_in_fiscal_category_id.id or False

    _columns = {
        'fiscal_category_id': fields.many2one(
            'l10n_br_account.fiscal.category', 'Categoria Fiscal',
            domain="[('journal_type', 'in', ('sale_refund', 'purchase')), "
            "('fiscal_type', '=', 'product'), ('type', '=', 'input')]"),
        'fiscal_position': fields.many2one(
            'account.fiscal.position', u'Posição Fiscal',
            domain="[('fiscal_category_id','=',fiscal_category_id)]")
    }
    _defaults = {
        'invoice_state': 'none',
        'fiscal_category_id': _default_fiscal_category
    }


class stock_picking_out(stock_picking):
    _inherit = 'stock.picking.out'

    def _default_fiscal_category(self, cr, uid, context=None):
        user = self.pool.get('res.users').browse(
            cr, uid, uid, context=context)
        return user.company_id.stock_out_fiscal_category_id and \
        user.company_id.stock_out_fiscal_category_id.id or False

    _columns = {
        'fiscal_category_id': fields.many2one(
            'l10n_br_account.fiscal.category', 'Categoria Fiscal',
            domain="[('journal_type', 'in', ('purchase_refund', 'sale')), "
            "('fiscal_type', '=', 'product'), ('type', '=', 'output')]"),
        'fiscal_position': fields.many2one(
            'account.fiscal.position', u'Posição Fiscal',
            domain="[('fiscal_category_id','=',fiscal_category_id)]")
    }
    _defaults = {
        'invoice_state': 'none',
        'fiscal_category_id': _default_fiscal_category,
    }
