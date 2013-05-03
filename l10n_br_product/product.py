# -*- encoding: utf-8 -*-
#################################################################################
#                                                                               #
# Copyright (C) 2010                                                            #
# @author Raphaël Valyi, Renato Lima						#
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

from osv import fields, osv


class product_template(osv.osv):
    _inherit = "product.template"
    _columns = {
        'origin': fields.selection(
            (('0', 'Nacional'),
             ('1', 'Estrangeira - Importação direta'),
             ('2', 'Estrangeira - Adquirida no mercado interno'),
             ('3', 'Nacional, mercadoria ou bem com conteúdo de importação superior a 40%'),
             ('4', 'Nacional, cuja produção tenha sido feita em conformidade com os processos produtivos básicos de que tratam as legislações citadas nos ajustes'),
             ('5', 'Nacional, mercadoria ou bem com conteúdo de importação inferior ou igual a 40%'),
             ('6', 'Estrangeira - Importação direta, sem similar nacional, constante em lista da CAMEX'),
             ('7', 'Estrangeira - Adquirida no mercado interno, sem similar nacional, constante em lista da CAMEX')
            ),
            u'Origem'
            ),
        'company_id':fields.many2one('res.company','Company', required=True),
        }
    _defaults = {
        'origin': '0',
        'company_id': lambda self, cr, uid, c: \
            self.pool.get('res.users').browse(
                cr, uid, uid, context=c
                ).company_id.id,
        }


product_template()


class product_product(osv.osv):
    _inherit = "product.product"

    def name_search(self, cr, user, name='', args=None, operator='ilike',
                    context=None, limit=100):
        if not args:
            args = []
        company = self.pool.get('res.users').browse(
            cr, user, user, context=context
            ).company_id
        args.append(('company_id', '=', company.id))
        return super(product_product, self).name_search(
            cr, user, name, args, operator, context, limit
            )

    def search(self, cr, user, args, offset=0, limit=None, order=None,
               context=None, count=False):
        if not args:
            args = []
        company = self.pool.get('res.users').browse(
            cr, user, user, context=context
            ).company_id
        args.append(('company_id', '=', company.id))
        return super(product_product, self).search(
            cr, user, args, offset=offset, limit=limit, order=order,
            context=context, count=count
            )


product_product()
