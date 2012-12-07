# -*- encoding: utf-8 -*-
#################################################################################
#                                                                               #
# Copyright (C) 2009  Renato Lima - Akretion, Gabriel C. Stabel                 #
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


class res_partner(osv.osv):
    _inherit = 'res.partner'

    _columns = {
                'partner_fiscal_type_id': fields.many2one('l10n_br_account.partner.fiscal.type',
                                                          'Tipo Fiscal do Parceiro', domain="[('tipo_pessoa','=',tipo_pessoa)]"),
    }

res_partner()


class account_fiscal_position_template(osv.osv):
    _inherit = 'account.fiscal.position.template'
    
    _columns = {
                'fiscal_operation_id': fields.many2one('l10n_br_account.fiscal.operation', 'Operação Fiscal'),
                }
        
account_fiscal_position_template()


class account_fiscal_position(osv.osv):
    _inherit = 'account.fiscal.position'

    _columns = {
                'fiscal_operation_id': fields.many2one('l10n_br_account.fiscal.operation', 'Operação Fiscal'),
                }

    def map_tax(self, cr, uid, fposition_id, taxes, context=None):
        tax_obj = self.pool.get('account.tax')
        if not taxes:
            return []
        if not fposition_id:
            return map(lambda x: x.id, taxes)
        result = []
        for t in taxes:
            ok = False
            for fp_tax in fposition_id.tax_ids:
                # change behavior to search by the tax code
                tax = tax_obj.browse(cr, uid, fp_tax.tax_src_id.id)
                if tax.tax_code_id and tax.tax_code_id.id == t.tax_code_id.id:
                    if fp_tax.tax_dest_id:
                        result.append(fp_tax.tax_dest_id.id)
                    ok=True
            if not ok:
                result.append(t.id)
        return result
        
account_fiscal_position()


class account_fiscal_position_tax(osv.osv):
    _inherit = 'account.fiscal.position.tax'
 
    _columns = {
                'imposto_credito': fields.boolean(u'Gera Crédito'),
                }
    
    _defaults = {
        'imposto_credito': False,
    }
        
account_fiscal_position_tax()
