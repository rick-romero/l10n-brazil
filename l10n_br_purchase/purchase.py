# -*- encoding: utf-8 -*-
#################################################################################
#                                                                               #
# Copyright (C) 2009  Renato Lima - Akretion, Gabriel C. Stabel                 #
# Copyright (C) 2012  Raphaël Valyi - Akretion                                  #
#                                                                               #
#This program is free software: you can redistribute it and/or modify           #
#it under the terms of the GNU Affero General Public License as published by    #
#the Free Software Foundation, either version 3 of the License, or              #
#(at your option) any later version.                                            #
#                                                                               #
#This program is distributed in the hope that it will be useful,                #
#but WITHOUT ANY WARRANTY; without even the implied warranty of                 #
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the                  #
#GNU Affero General Public License for more details.                            #
#                                                                               #
#You should have received a copy of the GNU Affero General Public License       #
#along with this program.  If not, see <http://www.gnu.org/licenses/>.          #
#################################################################################

from osv import osv, fields
from tools.translate import _
import decimal_precision as dp


class purchase_order(osv.osv):
    _inherit = 'purchase.order'

    STATE_SELECTION = [
        ('draft', 'Request for Quotation'),
        ('to_invoice', u'Para Faturar'),
        ('wait', 'Waiting'),
        ('confirmed', 'Waiting Approval'),
        ('approved', 'Approved'),
        ('except_picking', 'Shipping Exception'),
        ('except_invoice', 'Invoice Exception'),
        ('done', 'Done'),
        ('cancel', 'Cancelled')
    ]

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
                for c_tax in self.pool.get('account.tax').compute_all(cr, uid, line.taxes_id, line.price_unit, line.product_qty, order.partner_address_id.id, line.product_id.id, order.partner_id)['taxes']:
                    tax_brw = self.pool.get('account.tax').browse(cr, uid, c_tax['id'])
                    if tax_brw.tax_add:
                        val += c_tax.get('amount', 0.0)
            res[order.id]['amount_tax'] = cur_obj.round(cr, uid, cur, val)
            res[order.id]['amount_untaxed'] = cur_obj.round(cr, uid, cur, val1)
            res[order.id]['amount_total'] = res[order.id]['amount_untaxed'] + res[order.id]['amount_tax']
        return res

    def _get_order(self, cr, uid, ids, context=None):
        result = {}
        for line in self.pool.get('purchase.order.line').browse(cr, uid, ids, context=context):
            result[line.order_id.id] = True
        return result.keys()

    _columns = {
        'fiscal_operation_category_id': fields.many2one(
            'l10n_br_account.fiscal.operation.category',
            u'Categoria',
            domain="[('type','=','input'),('use_purchase','=',True)]"
            ),
        'fiscal_operation_id': fields.many2one(
            'l10n_br_account.fiscal.operation',
            u'Operação Fiscal',
            domain="[('fiscal_operation_category_id','=',fiscal_operation_category_id),(type,'=','input'),('use_purchase','=',True)]"
            ),
        'amount_untaxed': fields.function(
            _amount_all,
            method=True,
            digits_compute=dp.get_precision('Purchase Price'),
            string='Untaxed Amount',
            store={'purchase.order.line': (_get_order, None, 10), },
            multi="sums",
            help="The amount without tax"
            ),
        'amount_tax': fields.function(
            _amount_all,
            method=True,
            digits_compute=dp.get_precision('Purchase Price'),
            string='Taxes',
            store={'purchase.order.line': (_get_order, None, 10), },
            multi="sums",
            help="The tax amount"
            ),
        'amount_total': fields.function(
            _amount_all,
            method=True,
            digits_compute=dp.get_precision('Purchase Price'),
            string='Total',
            store={'purchase.order.line': (_get_order, None, 10), },
            multi="sums",
            help="The total amount"
            ),
        'state': fields.selection(
            STATE_SELECTION,
            'State',
            readonly=True,
            help="The state of the purchase order or the quotation request. A quotation is a purchase order in a 'Draft' state. Then the order has to be confirmed by the user, the state switch to 'Confirmed'. Then the supplier must confirm the order to change the state to 'Approved'. When the purchase order is paid and received, the state becomes 'Done'. If a cancel action occurs in the invoice or in the reception of goods, the state becomes in exception.",
            select=True
            ),
        'partner_ref': fields.char(
            'Supplier Reference',
            states={
                'to_invoice': [('readonly', True)],
                'confirmed': [('readonly', True)],
                'approved': [('readonly', True)],
                'done': [('readonly', True)]
                },
            size=64
            ),
        'date_order':fields.date(
            'Order Date',
            required=True,
            states={
                'to_invoice': [('readonly', True)],
                'confirmed': [('readonly', True)],
                'approved': [('readonly', True)]
                },
            select=True,
            help="Date on which this document has been created."
            ),
        'partner_id':fields.many2one(
            'res.partner',
            'Supplier',
            required=True,
            states={
                'to_invoice': [('readonly', True)],
                'confirmed': [('readonly', True)],
                'approved': [('readonly', True)],
                'done': [('readonly', True)]
                },
            change_default=True
            ),
        'partner_address_id': fields.many2one(
            'res.partner.address',
            'Address',
            required=True,
            states={
                'to_invoice': [('readonly', True)],
                'confirmed': [('readonly', True)],
                'approved': [('readonly', True)],
                'done': [('readonly', True)]
                },
            domain="[('partner_id', '=', partner_id)]"
            ),
        'dest_address_id': fields.many2one(
            'res.partner.address',
            'Destination Address',
            domain="[('partner_id', '!=', False)]",
            states={
                'to_invoice': [('readonly', True)],
                'confirmed': [('readonly', True)],
                'approved': [('readonly', True)],
                'done': [('readonly', True)]
                },
            help="Put an address if you want to deliver directly from the supplier to the customer." \
                "In this case, it will remove the warehouse link and set the customer location."
        ),
        'warehouse_id': fields.many2one(
            'stock.warehouse',
            'Warehouse',
            states={
                'to_invoice': [('readonly', True)],
                'confirmed': [('readonly', True)],
                'approved': [('readonly', True)],
                'done': [('readonly', True)]}
            ),
        'pricelist_id':fields.many2one(
            'product.pricelist',
            'Pricelist',
            required=True,
            states={
                'to_invoice': [('readonly', True)],
                'confirmed': [('readonly', True)],
                'approved': [('readonly', True)],
                'done': [('readonly', True)]
                },
            help="The pricelist sets the currency used for this purchase order. It also computes the supplier price for the selected products/quantities."
            ),
        'order_line': fields.one2many(
            'purchase.order.line',
            'order_id',
            'Order Lines',
            states={
                'approved':[('readonly', True)],
                'done':[('readonly', True)]
                }
            ),
        }

    def _default_fiscal_operation_category(self, cr, uid, context=None):
        user = self.pool.get('res.users').browse(cr, uid, uid, context=context)
        return user.company_id and user.company_id.purchase_fiscal_category_operation_id and user.company_id.purchase_fiscal_category_operation_id.id or False

    _defaults = {
                'fiscal_operation_category_id': _default_fiscal_operation_category,
                }

    def _fiscal_position_map(self, cr, uid, ids, partner_id, partner_invoice_id, company_id, fiscal_operation_category_id):
        obj_fiscal_position_rule = self.pool.get('account.fiscal.position.rule')

        result = obj_fiscal_position_rule.fiscal_position_map(cr, uid, partner_id, partner_invoice_id, company_id,
                                                              fiscal_operation_category_id,
                                                              context={'use_domain': ('use_purchase', '=', True)})
        return result

    def onchange_partner_id(self, cr, uid, ids, partner_id=False, partner_address_id=False,
                            company_id=False, fiscal_operation_category_id=False):
        result = super(purchase_order, self).onchange_partner_id(cr, uid, ids, partner_id, company_id)
        if result['value']['partner_address_id']:
            partner_address_id = result['value']['partner_address_id']
        fiscal_data = self._fiscal_position_map(cr, uid, ids, partner_id, partner_address_id, company_id, fiscal_operation_category_id)
        result['value'].update(fiscal_data)
        return result

    def onchange_partner_address_id(self, cr, uid, ids, partner_id=False, partner_address_id=False,
                                    company_id=False, fiscal_operation_category_id=False):
        result = super(purchase_order, self).onchange_partner_address_id(cr, uid, ids, partner_address_id, company_id)
        fiscal_data = self._fiscal_position_map(cr, uid, ids, partner_id, partner_address_id, company_id, fiscal_operation_category_id)
        result['value'].update(fiscal_data)
        return result

    def onchange_fiscal_operation_category_id(self, cr, uid, ids, partner_id=False, partner_address_id=False,
                                              company_id=False, fiscal_operation_category_id=False):
        result = {'value': {}}
        fiscal_data = self._fiscal_position_map(cr, uid, ids, partner_id, partner_address_id, company_id, fiscal_operation_category_id)
        result['value'].update(fiscal_data)
        return result

    def _prepare_inv_line(self, cr, uid, account_id, order_line, context=None):
        result = super(purchase_order, self)._prepare_inv_line(cr, uid, account_id, order_line, context)
        order = order_line.order_id
        result['fiscal_operation_category_id'] = order_line.fiscal_operation_category_id and order_line.fiscal_operation_category_id.id \
                                              or order.fiscal_operation_category_id and order.fiscal_operation_category_id.id
        result['fiscal_operation_id'] = order_line.fiscal_operation_id and order_line.fiscal_operation_id.id \
                                     or order.fiscal_operation_id and order.fiscal_operation_id.id
        result['cfop_id'] = (order_line.cfop_id and order_line.cfop_id.id) or\
            (order.fiscal_operation_id and
             order.fiscal_operation_id.cfop_id and
             order.fiscal_operation_id.cfop_id.id) or False
        return result

    def action_invoice_create(self, cr, uid, ids, *args):  # TODO ask OpenERP SA for a _prepare_invoice method!
        inv_id = super(purchase_order, self).action_invoice_create(cr, uid, ids, *args)
        for order in self.browse(cr, uid, ids):
            if inv_id:  # REMARK: super method is ugly as it assumes only one invoice for possibly several purchase orders.
                company_id = order.company_id
                if not company_id.document_serie_product_ids:
                    raise osv.except_osv(_('No fiscal document serie found !'), _("No fiscal document serie found for selected company %s and fiscal operation: '%s'") % (order.company_id.name, order.fiscal_operation_id.code))
                comment = order.fiscal_operation_id.note or ''
                if order.notes:
                    comment += ' - ' + order.notes
                self.pool.get('account.invoice').write(cr, uid, inv_id, {\
                     'fiscal_operation_category_id': order.fiscal_operation_id and order.fiscal_operation_category_id.id,
                     'fiscal_operation_id': order.fiscal_operation_id and order.fiscal_operation_id.id,
                     'fiscal_document_id': order.fiscal_operation_id and order.fiscal_operation_id.fiscal_document_id and order.fiscal_operation_id.fiscal_document_id.id,
                     'fiscal_position': order.fiscal_position and order.fiscal_position.id,
                     'document_serie_id': company_id.document_serie_product_ids and company_id.document_serie_product_ids[0].id,  # TODO pick 1st active! See l10n_br_sale + refactor logic into res_company
                     'own_invoice': False,
                     'comment': comment})
        return inv_id

    def action_picking_create(self, cr, uid, ids, *args):
        picking_id = False
        for order in self.browse(cr, uid, ids):
            picking_id = super(purchase_order, self).action_picking_create(cr, uid, ids, *args)
            self.pool.get('stock.picking').write(cr, uid, picking_id, {'fiscal_operation_category_id': order.fiscal_operation_category_id.id, 'fiscal_operation_id': order.fiscal_operation_id.id, 'fiscal_position': order.fiscal_position.id})
        return picking_id

    def wkf_confirm_order(self, cr, uid, ids, context=None):
        todo = []
        for po in self.browse(cr, uid, ids, context=context):
            if not po.order_line:
                raise osv.except_osv(
                    _('Error !'),
                    _('You cannot confirm a purchase order without any lines.')
                    )
            for line in po.order_line:
                if line.state == 'to_invoice':
                    todo.append(line.id)
            message = _("Purchase order '%s' is confirmed.") % (po.name,)
            self.log(cr, uid, po.id, message)

        self.pool.get('purchase.order.line').action_confirm(cr, uid, todo,
                                                            context)
        for id in ids:
            self.write(cr, uid, [id], {'state': 'confirmed',
                                       'validator': uid})
        return True

    def to_invoice(self, cr, uid, ids, context=None):
        todo = []
        for po in self.browse(cr, uid, ids, context=context):
            if not po.order_line:
                raise osv.except_osv(
                    _('Error !'),
                    _('You cannot confirm a purchase order without any lines.')
                    )
            for line in po.order_line:
                if line.state == 'draft':
                    todo.append(line.id)
            message = _("Purchase order '%s' is confirmed.") % (po.name,)
            self.log(cr, uid, po.id, message)

        self.pool.get('purchase.order.line').write(
            cr, uid, todo, {'state': 'to_invoice'}, context=context
            )

        for id in ids:
            self.write(cr, uid, [id], {'state': 'to_invoice',
                                       'validator': uid})
        return True


purchase_order()


class purchase_order_line(osv.osv):
    _inherit = 'purchase.order.line'

    _columns = {
        'fiscal_operation_category_id': fields.many2one(
            'l10n_br_account.fiscal.operation.category',
            u'Categoria',
            domain="[('type','=','input'),('use_purchase','=',True)]"
            ),
        'fiscal_operation_id': fields.many2one(
            'l10n_br_account.fiscal.operation',
            u'Operação Fiscal',
            domain="[('fiscal_operation_category_id','=',fiscal_operation_category_id),('type','=','input'),('use_purchase','=',True)]"
            ),
        'fiscal_position': fields.many2one(
            'account.fiscal.position',
            'Fiscal Position',
            readonly=True,
            domain="[('fiscal_operation_id','=',fiscal_operation_id)]",
            states={
                'draft': [('readonly', False)],
                }
            ),
        'state': fields.selection(
            [('draft', 'Draft'),
             ('to_invoice', u'Para Faturar'),
             ('confirmed', 'Confirmed'),
             ('done', 'Done'),
             ('cancel', 'Cancelled')],
            'State',
            required=True,
            readonly=True,
            help=' * The \'Draft\' state is set automatically when purchase order in draft state. \
                \n* The \'Confirmed\' state is set automatically as confirm when purchase order in confirm state. \
                \n* The \'Done\' state is set automatically when purchase order is set as done. \
                \n* The \'Cancelled\' state is set automatically when user cancel purchase order.'
            ),

        'name': fields.char(
            'Description',
            size=256,
            required=True,
            states={'to_invoice': [('readonly', True)]},
            ),
        'product_qty': fields.float(
            'Quantity',
            digits_compute=dp.get_precision('Product UoM'),
            required=True,
            states={'to_invoice': [('readonly', True)]},
            ),
        'date_planned': fields.date(
            'Scheduled Date', required=True, select=True,
            states={'to_invoice': [('readonly', True)]},
            ),
        'product_uom': fields.many2one(
            'product.uom', 'Product UOM', required=True,
            states={'to_invoice': [('readonly', True)]},
            ),
        'product_id': fields.many2one(
            'product.product',
            'Product',
            domain=[('purchase_ok','=',True)],
            change_default=True,
            states={'to_invoice': [('readonly', True)]},
            ),
        'move_dest_id': fields.many2one(
            'stock.move',
            'Reservation Destination',
            ondelete='set null',
            states={'to_invoice': [('readonly', True)]},
            ),
        'price_unit': fields.float(
            'Unit Price',
            required=True,
            digits_compute=dp.get_precision('Purchase Price'),
            states={'to_invoice': [('readonly', True)]},
            ),
        'notes': fields.text(
            'Notes', states={'to_invoice': [('readonly', True)]},
            ),
        'order_id': fields.many2one(
            'purchase.order',
            'Order Reference',
            select=True,
            required=True,
            ondelete='cascade',
            states={'to_invoice': [('readonly', True)]},
            ),
        'cfop_id': fields.many2one(
            'l10n_br_account.cfop',
            u'Código Fiscal',
            domain="[('type','=','output'),('internal_type','=','normal')]"
            ),
        }

    def product_id_change(self, cr, uid, ids, pricelist, product, qty, uom,
                          partner_id, date_order=False, fiscal_position=False, date_planned=False,
                          name=False, price_unit=False, notes=False, context={}, fiscal_operation_category_id=False,
                          fiscal_operation_id=False):
        result = super(purchase_order_line, self).product_id_change(cr, uid, ids, pricelist, product, qty, uom,
                                                                    partner_id, date_order, fiscal_position,
                                                                    date_planned, name, price_unit, notes)
        if fiscal_operation_category_id:
            result['value']['fiscal_operation_category_id'] = fiscal_operation_category_id
        if fiscal_operation_id:
            result['value']['fiscal_operation_id'] = fiscal_operation_id
        if fiscal_position:
            result['value']['fiscal_position'] = fiscal_position
        return result

    def fiscal_operation_id_change(self, cr, uid, ids, fop_id):
        result = {'value': {}}
        obj_fop = self.pool.get('l10n_br_account.fiscal.operation').browse(
            cr, uid, fop_id
            )
        if obj_fop.cfop_id:
            result['value']['cfop_id'] = obj_fop.cfop_id.id

        return result


purchase_order_line()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
