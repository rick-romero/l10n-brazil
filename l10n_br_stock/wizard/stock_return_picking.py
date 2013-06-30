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

from openerp.osv import orm
from openerp.tools.translate import _


class stock_return_picking(orm.TransientModel):
    _inherit = 'stock.return.picking'

    def _prepare_create_returns(self, cr, uid, pick, context=None): 
        vals = {
                'fiscal_category_id': False,
                'fiscal_position': False}

        fc_return_id = pick.fiscal_category_id.refund_fiscal_category_id \
        and pick.fiscal_category_id.refund_fiscal_category_id.id

        if not fc_return_id:
            raise orm.except_orm(
                _('Error!'),
                _("This Fiscal Operation does not has Fiscal Operation \
                for Returns!"))

        vals['fiscal_category_id'] = fc_return_id
        
        return vals
                
        
    def create_returns(self, cr, uid, ids, context=None):
        """
         Creates return picking.
         @param self: The object pointer.
         @param cr: A database cursor
         @param uid: ID of the user currently logged in
         @param ids: List of ids selected
         @param context: A standard dictionary
         @return: A dictionary which of fields with values.
        """
        result = super(stock_return_picking, self).create_returns(
            cr, uid, ids, context)

        data = self.read(cr, uid, ids[0])

        if data['invoice_state'] == 'none':
            return result

        pick_obj = self.pool.get('stock.picking')
        result_domain = eval(result['domain'])
        record_ids = result_domain and result_domain[0] and result_domain[0][2]
        picks = pick_obj.browse(cr, uid, record_ids, context=context)

        for pick in picks:
            vals = self._prepare_create_returns(cr, uid, pick, context)
            pick_obj.write(cr, uid, pick.id, vals)

        return result
