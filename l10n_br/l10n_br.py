# -*- encoding: utf-8 -*-
#################################################################################
#                                                                               #
# Copyright (C) 2009  Renato Lima - Akretion                                    #
#                                                                               #
#This program is free software: you can redistribute it and/or modify           #
#it under the terms of the GNU Affero General Public License as published by    #
#the Free Software Foundation, either version 3 of the License, or              #
#(at your option) any later version.                                            #
#                                                                               #
#This program is distributed in the hope that it will be useful,                #
#but WITHOUT ANY WARRANTY; without even the implied warranty of                 #
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the                  #
#GNU General Public License for more details.                                   #
#                                                                               #
#You should have received a copy of the GNU General Public License              #
#along with this program.  If not, see <http://www.gnu.org/licenses/>.          #
#################################################################################

from osv import fields, osv

class l10n_br_account_cst_template(osv.osv):
    _name = 'l10n_br_account.cst.template'
    _description = 'Tax Situation Code Template' 
    _columns = {
                'code': fields.char('Code', size=8,required=True),
                'name': fields.char('Description', size=64),
                'tax_code_template_id': fields.many2one('account.tax.code.template', 'Tax Code Template',required=True),
                }
    
    def name_search(self, cr, user, name, args=None, operator='ilike', context=None, limit=80):
        if not args:
            args = []
        if context is None:
            context = {}
        ids = self.search(cr, user, ['|',('name',operator,name),('code',operator,name)] + args, limit=limit, context=context)
        return self.name_get(cr, user, ids, context)
    
    def name_get(self, cr, uid, ids, context=None):
        if not ids:
            return []
        reads = self.read(cr, uid, ids, ['name', 'code'], context=context)
        res = []
        for record in reads:
            name = record['name']
            if record['code']:
                name = record['code'] + ' - '+name
            res.append((record['id'], name))
        return res
    
l10n_br_account_cst_template()

class l10n_br_account_cst(osv.osv):
    _name = 'l10n_br_account.cst'
    _description = 'Tax Situation Code'
    _columns = {
                'code': fields.char('Code', size=8,required=True),
                'name': fields.char('Description', size=64),
                'tax_code_id': fields.many2one('account.tax.code', 'Tax Code',required=True),
                }
    
    def name_search(self, cr, user, name, args=None, operator='ilike', context=None, limit=80):
        if not args:
            args = []
        if context is None:
            context = {}
        ids = self.search(cr, user, ['|',('name',operator,name),('code',operator,name)] + args, limit=limit, context=context)
        return self.name_get(cr, user, ids, context)
    
    def name_get(self, cr, uid, ids, context=None):
        if not ids:
            return []
        reads = self.read(cr, uid, ids, ['name', 'code'], context=context)
        res = []
        for record in reads:
            name = record['name']
            if record['code']:
                name = record['code'] + ' - '+name
            res.append((record['id'], name))
        return res
    
l10n_br_account_cst()


class l10n_br_natureza_juridica(osv.osv):
    _name = 'l10n_br.natureza_juridica'
    _description = u'Natureza Jurídica'
    _columns = {
        'code': fields.char(u'Código', size=5, required=True),
        'name': fields.char(u'Descrição', size=100),
        }

    def name_search(self, cr, user, name, args=None, operator='ilike',
                    context=None, limit=80):
        if not args:
            args = []
        if context is None:
            context = {}
        ids = self.search(cr, user, [
            '|', ('name', operator, name), ('code', operator, name)
            ] + args, limit=limit, context=context)

        return self.name_get(cr, user, ids, context)

    def name_get(self, cr, uid, ids, context=None):
        if not ids:
            return []
        reads = self.read(cr, uid, ids, ['name', 'code'], context=context)
        res = []
        for record in reads:
            name = record['name']
            if record['code']:
                name = record['code'] + ' - ' + name
            res.append((record['id'], name))
        return res

l10n_br_natureza_juridica()


class l10n_br_porte(osv.osv):
    _name = 'l10n_br.porte'
    _description = u'Porte'
    _columns = {
        'name': fields.char(u'Porte', size=60, required=True),
        'description': fields.char(u'Descrição', size=500),
        }

l10n_br_porte()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
