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
        vals = super(stock_return_picking,self)._prepare_create_returns(cr, uid, pick, context)
        
        fc_return_id = vals['fiscal_category_id']
        
        obj_company = self.pool.get('res.company').browse(cr, uid, [pick.company_id.id])[0]

        company_addr = self.pool.get('res.partner').address_get(cr, uid, [obj_company.partner_id.id], ['default'])
        company_addr_default = self.pool.get('res.partner.address').browse(cr, uid, [company_addr['default']])[0]

        from_country = company_addr_default.country_id.id
        from_state = company_addr_default.state_id.id

        to_invoice_country = pick.address_id.country_id.id
        to_invoice_state = pick.address_id.state_id.id

        obj_partner = self.pool.get('res.partner').browse(cr, uid, [pick.address_id.partner_id.id])[0]
        partner_fiscal_type = obj_partner.partner_fiscal_type_id.id

        fp_id = self.pool.get('account.fiscal.position.rule').search(
            cr, uid, ['&', ('company_id', '=', obj_company.id),
                      ('use_picking', '=', True),
                      ('fiscal_category_id', '=', fc_return_id),
                      '|', ('from_country', '=', from_country),
                      ('from_country', '=', False),
                      '|', ('to_invoice_country', '=', to_invoice_country),
                      ('to_invoice_country', '=', False),
                      '|', ('from_state', '=', from_state),
                      ('from_state', '=', False),
                      '|', ('to_invoice_state', '=', to_invoice_state),
                      ('to_invoice_state', '=', False),
                      '|', ('partner_fiscal_type_id', '=', False),
                      ('partner_fiscal_type_id', '=', partner_fiscal_type)])

        if fp_id:
            obj_fp_rule = self.pool.get('account.fiscal.position.rule').browse(cr, uid, fp_id)[0]
            vals['fiscal_position'] = obj_fp_rule.fiscal_position_id.id
        
        return vals