# -*- encoding: utf-8 -*-
###############################################################################
#                                                                             #
# Copyright (C) 2009  Renato Lima - Akretion, Gabriel C. Stabel               #
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
from openerp import api

PRODUCT_FISCAL_TYPE = [
    ('product', u'Produto'),
    ('service', u'Serviço'),
]

PRODUCT_FISCAL_TYPE_DEFAULT = PRODUCT_FISCAL_TYPE[0][0]

class ProductTemplate(orm.Model):
    _inherit = 'product.product'
    _columns = {
        'fiscal_category_default_ids': fields.one2many(
            'l10n_br_account.product.category', 'product_tmpl_id',
            u'Categoria de Operação Fiscal Padrões'),
        'fiscal_type': fields.selection(
            PRODUCT_FISCAL_TYPE, 'Tipo Fiscal', required=True),
    }
    _defaults = {
        'fiscal_type': PRODUCT_FISCAL_TYPE_DEFAULT
    }
    
class ProductTemplate(orm.Model):
    _inherit = 'product.template'
    _columns = {
        'fiscal_category_default_ids': fields.one2many(
            'l10n_br_account.product.category', 'product_tmpl_id',
            u'Categoria de Operação Fiscal Padrões'),
        'fiscal_type': fields.selection(
            PRODUCT_FISCAL_TYPE, 'Tipo Fiscal', required=True),
    }
    _defaults = {
        'fiscal_type': PRODUCT_FISCAL_TYPE_DEFAULT
    }
    
    @api.onchange('type')
    def _onchange_type(self):
        if self.type == 'consu' or self.type == 'product':
            self.fiscal_type = 'product'
        elif self.type == 'service':
            self.fiscal_type = 'service'
    

class L10n_brAccountProductFiscalCategory(orm.Model):
    _name = 'l10n_br_account.product.category'
    _columns = {
        'fiscal_category_source_id': fields.many2one(
            'l10n_br_account.fiscal.category', 'Categoria de Origem'),
        'fiscal_category_destination_id': fields.many2one(
            'l10n_br_account.fiscal.category', 'Categoria de Destino'),
        'product_tmpl_id': fields.many2one(
            'product.template', 'Produto', ondelete='cascade')
    }
