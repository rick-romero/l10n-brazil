# -*- encoding: utf-8 -*-
###############################################################################
#                                                                             #
# Copyright (C) 2013  Renato Lima - Akretion                                  #
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

FISCAL_POSITION_COLUMNS = {
    'cfop_id': fields.many2one('l10n_br_account_product.cfop', 'CFOP'),
}


class AccountFiscalPositionTemplate(orm.Model):
    _inherit = 'account.fiscal.position.template'
    _columns = FISCAL_POSITION_COLUMNS


class AccountFiscalPositionTaxTemplate(orm.Model):
    _inherit = 'account.fiscal.position.tax.template'
    _columns = {
        'ncm_id': fields.many2one(
            'account.product.fiscal.classification.template', 'NCM'),
    }


class AccountFiscalPosition(orm.Model):
    _inherit = 'account.fiscal.position'
    _columns = FISCAL_POSITION_COLUMNS

    #TODO - Refatorar para trocar os impostos
    def map_tax_code(self, cr, uid, product_id, fiscal_position,
                     company_id=False, tax_ids=False, context=None):

        if not context:
            context = {}

        result = {}
        if tax_ids:

            product = self.pool.get('product.product').browse(
                cr, uid, product_id, context=context)

            fclassificaion = product.ncm_id

            if context.get('type_tax_use') == 'sale':

                if fclassificaion:
                    tax_sale_ids = fclassificaion.sale_tax_definition_line
                    for tax_def in tax_sale_ids:
                        if tax_def.tax_id.id in tax_ids and tax_def.tax_code_id:
                            result.update({tax_def.tax_id.domain:
                                           tax_def.tax_code_id.id})

                if company_id:
                    company = self.pool.get('res.company').browse(
                        cr, uid, company_id, context=context)

                    company_tax_def = company.product_tax_definition_line

                    for tax_def in company_tax_def:
                        if tax_def.tax_id.id in tax_ids and tax_def.tax_code_id:
                                result.update({tax_def.tax_id.domain:
                                               tax_def.tax_code_id.id})

            if context.get('type_tax_use') == 'purchase':

                if fclassificaion:
                    tax_purchase_ids = fclassificaion.purchase_tax_definition_line
                    for tax_def in tax_purchase_ids:
                        if tax_def.tax_id.id in tax_ids and tax_def.tax_code_id:
                            result.update({tax_def.tax_id.domain:
                                           tax_def.tax_code_id.id})

            if fiscal_position:

                #TODO Criar um método para varrer as regras de mapeamento
                mapping_taxes = [tax_map for tax_map in fiscal_position.tax_ids
                if not tax_map.ncm_id]

                for fp_tax in mapping_taxes:
                    if fp_tax.tax_dest_id:
                        if fp_tax.tax_dest_id.id in tax_ids and fp_tax.tax_code_dest_id:
                            result.update({fp_tax.tax_dest_id.domain:
                                           fp_tax.tax_code_dest_id.id})
                    if not fp_tax.tax_dest_id and fp_tax.tax_code_src_id and \
                    fp_tax.tax_code_dest_id:
                        result.update({fp_tax.tax_code_src_id.domain:
                                       fp_tax.tax_code_dest_id.id})

                mapping_ncm_taxes = [tax_map for tax_map in fiscal_position.tax_ids
                if tax_map.ncm_id.id == product.ncm_id.id]

                for fp_tax in mapping_ncm_taxes:
                    if fp_tax.tax_dest_id:
                        if fp_tax.tax_dest_id.id in tax_ids and fp_tax.tax_code_dest_id:
                            result.update({fp_tax.tax_dest_id.domain:
                                           fp_tax.tax_code_dest_id.id})
                    if not fp_tax.tax_dest_id and fp_tax.tax_code_src_id and \
                    fp_tax.tax_code_dest_id:
                        result.update({fp_tax.tax_code_src_id.domain:
                                       fp_tax.tax_code_dest_id.id})

        return result

    def map_tax(self, cr, uid, fposition_id, taxes, context=None):
        result = []
        if not context:
            context = {}
        if fposition_id and fposition_id.company_id and \
        context.get('type_tax_use') in ('sale', 'all'):
            company_tax_ids = self.pool.get('res.company').read(
                cr, uid, fposition_id.company_id.id, ['product_tax_ids'],
                context=context)['product_tax_ids']

            company_taxes = self.pool.get('account.tax').browse(
                    cr, uid, company_tax_ids, context=context)
            if taxes:
                all_taxes = taxes + company_taxes
            else:
                all_taxes = company_taxes
            taxes = all_taxes

        if not fposition_id and not taxes:
            return map(lambda x: x.id, taxes)
        product_ncm = False
        if context.get('product_id'):
            product_ncm = self.pool.get('product.product').read(
                cr, uid, context.get('product_id'), ['ncm_id'],
                context=context)['ncm_id'][0]

        taxes_mapped = {}
        for tax in taxes:
            taxes_mapped[tax.domain] = tax.id

            #TODO Criar um método para varrer as regras de mapeamento
            mapping_taxes = [tax_map for tax_map in fposition_id.tax_ids
            if not tax_map.ncm_id]

            for tax_mapping in mapping_taxes:
                tax_src = tax_mapping.tax_src_id and \
                tax_mapping.tax_src_id.id == tax.id

                tax_code_src = tax_mapping.tax_code_src_id and \
                tax_mapping.tax_code_src_id.id == tax.tax_code_id.id

                domain = tax.domain
                if tax_src or tax_code_src:
                    if tax_mapping.tax_dest_id:
                        taxes_mapped[domain] = tax_mapping.tax_dest_id.id
                    else:
                        taxes_mapped[domain] = False

            mapping_ncm_taxes = [tax_map for tax_map in fposition_id.tax_ids
            if tax_map.ncm_id.id == product_ncm]

            for tax_mapping in mapping_ncm_taxes:
                domain = tax.domain
                tax_src = tax_mapping.tax_src_id and \
                tax_mapping.tax_src_id.id == tax.id

                tax_code_src = tax_mapping.tax_code_src_id and \
                tax_mapping.tax_code_src_id.id == tax.tax_code_id.id

                if tax_src or tax_code_src:
                    if tax_mapping.tax_dest_id:
                        taxes_mapped[domain] = tax_mapping.tax_dest_id.id
                    else:
                        taxes_mapped[domain] = False

            for tax_id in taxes_mapped.values():
                if tax_id:
                    result.append(tax_id)
        return list(set(result))


class AccountFiscalPositionTax(orm.Model):
    _inherit = 'account.fiscal.position.tax'
    _columns = {
        'ncm_id': fields.many2one(
            'account.product.fiscal.classification', 'NCM'),
    }