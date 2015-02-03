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
    
class L10n_brAccountServiceType(orm.Model):
    _name = 'l10n_br_account_service.service.type'
    _description = u'Cadastro de Operações Fiscais de Serviço'
    _columns = {
        'code': fields.char(u'Código', size=16, required=True),
        'name': fields.char(u'Descrição', size=256, required=True),
        'parent_id': fields.many2one('l10n_br_account_service.service.type', 'Tipo de Serviço Pai'),
        'child_ids': fields.one2many('l10n_br_account_service.service.type', 'parent_id', u'Tipo de Serviço Filhos'),
        'internal_type': fields.selection([('view', u'Visualização'), ('normal', 'Normal')], 'Tipo Interno', required=True),
    }
    _defaults = {
        'internal_type': 'normal'
    }

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
    
class L10n_brAccountDocumentSerie(orm.Model):
    _name = 'l10n_br_account.document.serie'
    _inherit = 'l10n_br_account.document.serie'
    
class L10n_brAccountFiscalCategory(orm.Model):
    _name = 'l10n_br_account.fiscal.category'
    _inherit = 'l10n_br_account.fiscal.category'
