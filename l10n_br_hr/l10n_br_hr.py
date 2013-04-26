# -*- coding: utf-8 -*-

##############################################################################
#                                                                            #
#  Copyright (C) 2012 Proge Informática Ltda (<http://www.proge.com.br>).    #
#                                                                            #
#  Author Daniel Hartmann <daniel@proge.com.br>                              #
#                                                                            #
#  This program is free software: you can redistribute it and/or modify      #
#  it under the terms of the GNU Affero General Public License as            #
#  published by the Free Software Foundation, either version 3 of the        #
#  License, or (at your option) any later version.                           #
#                                                                            #
#  This program is distributed in the hope that it will be useful,           #
#  but WITHOUT ANY WARRANTY; without even the implied warranty of            #
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the             #
#  GNU Affero General Public License for more details.                       #
#                                                                            #
#  You should have received a copy of the GNU Affero General Public License  #
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.     #
#                                                                            #
##############################################################################

from osv import osv, fields
from tools.translate import _
import re
import datetime


class l10n_br_hr_nationality(osv.osv):
    _name = 'l10n_br_hr.nationality'
    _description = u'Nacionalidade'
    _columns = {
        'code': fields.char(u'Código', size=2, required=True),
        'name': fields.char(u'Nacionalidade', size=60, required=True),
        }

l10n_br_hr_nationality()


class l10n_br_hr_etnia(osv.osv):
    _name = 'l10n_br_hr.etnia'
    _description = u'Etnia'
    _columns = {
        'code': fields.char(u'Código', size=2, required=True),
        'name': fields.char(u'Descrição', size=60, required=True),
        }

l10n_br_hr_etnia()


class l10n_br_hr_grau_de_instrucao(osv.osv):
    _name = 'l10n_br_hr.grau_de_instrucao'
    _description = u'Grau de Instrução'
    _columns = {
        'code': fields.char(u'Código', size=2, required=True),
        'name': fields.char(u'Descrição', size=150, required=True),
        }

l10n_br_hr_grau_de_instrucao()


class l10n_br_hr_tipo_de_admissao(osv.osv):
    _name = 'l10n_br_hr.tipo_de_admissao'
    _description = u'Tipo de Admissão'
    _columns = {
        'code': fields.char(u'Código', size=2, required=True),
        'name': fields.char(u'Descrição', size=150, required=True),
        }

l10n_br_hr_tipo_de_admissao()


class l10n_br_hr_ocupacao(osv.osv):
    _name = 'l10n_br_hr.ocupacao'
    _description = u'Ocupação'
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

l10n_br_hr_ocupacao()


class l10n_br_hr_vinculo(osv.osv):
    _name = 'l10n_br_hr.vinculo'
    _description = u'Vínculo Empregatício'
    _columns = {
        'code': fields.char(u'Código', size=2, required=True),
        'name': fields.char(u'Descrição', size=150, required=True),
        }

l10n_br_hr_vinculo()


class l10n_br_hr_motivo_de_desligamento(osv.osv):
    _name = 'l10n_br_hr.motivo_de_desligamento'
    _description = u'Motivo de Desligamento'
    _columns = {
        'code': fields.char(u'Código', size=2, required=True),
        'name': fields.char(u'Descrição', size=170, required=True),
        }

l10n_br_hr_motivo_de_desligamento()


class l10n_br_hr_movimentacao(osv.osv):
    _name = 'l10n_br_hr.movimentacao'
    _description = u'Movimentação'
    _columns = {
        'code': fields.char(u'Código', size=2, required=True),
        'name': fields.char(u'Descrição', size=170, required=True),
        }

l10n_br_hr_movimentacao()


class l10n_br_hr_changes(osv.osv):
    _name = 'l10n_br_hr.changes'
    _description = u'Registra alterações para envio via SEFIP'
    _columns = {
        'table': fields.char(u'Tabela em que ocorreu a alteração', size=128),
        'field': fields.char(u'Campo em que ocorreu a alteração', size=128),
        'new_value': fields.text(u'Novo valor do campo'),
        'register_id': fields.integer(u'Id do registro alterado'),
        }
    # FIXME: registrar somente os campos necessarios
    def register_changes(self, cr, uid, ids, table, vals):
        for register_id in ids:
            for field in vals:
                self.create(cr, uid, {
                    'table': table,
                    'field': field,
                    'new_value': vals[field],
                    'register_id': register_id,
                    })

l10n_br_hr_changes()


class l10n_br_hr_ocorrencia(osv.osv):
    _name = 'l10n_br_hr.ocorrencia'
    _description = u'Ocorrência'
    _columns = {
        'code': fields.char(u'Código', size=2, required=True),
        'name': fields.char(u'Descrição', size=150, required=True),
        }

l10n_br_hr_ocorrencia()


class hr_contract(osv.osv):
    _inherit = 'hr.contract'
    _columns = {
        'informacao_da_admissao': fields.selection((
            ('a', 'Admissão/Provimento'),
            ('t', 'Transferência/Movimentação'),
            ), u'Ação', required=True),
        'tipo_de_admissao_id': fields.many2one(
            'l10n_br_hr.tipo_de_admissao', u'Tipo de Admissão', required=True
            ),
        'tipo_de_salario_contratual': fields.selection((
            ('1', u'Mensal'),
            ('2', u'Quinzenal'),
            ('3', u'Semanal'),
            ('4', u'Diário'),
            ('5', u'Horário'),
            ('6', u'Tarefa'),
            ('7', u'Outros'),
            ), u'Tipo de Salário Contratual'),
        'ocupacao_id': fields.many2one(
            'l10n_br_hr.ocupacao', u'Ocupação'
            ),
        'vinculo_id': fields.many2one(
            'l10n_br_hr.vinculo', u'Vínculo Empregatício'
            ),
        'local_de_trabalho_estado': fields.many2one(
            'res.country.state', u'Estado'
            ),
        'local_de_trabalho_cidade': fields.many2one(
            'l10n_br_base.city', u'Cidade',
            domain="[('state_id','=',local_de_trabalho_estado)]",
            ),
        'informacao_de_desligamento': fields.selection((
            ('d', 'Desligamento/Vacância'),
            ('t', 'Transferência/Movimentação'),
            ), u'Ação de Desligamento'),
        'data_de_desligamento': fields.date(u'Data de Desligamento'),
        'motivo_de_desligamento_id': fields.many2one(
            'l10n_br_hr.motivo_de_desligamento', u'Motivo de Desligamento'
            ),
        'filiado_a_sindicato': fields.boolean(
            u'Empregado Filiado a Sindicato'
            ),
        'sindicato_cassoc1': fields.many2one(
            'res.partner',
            u'Contribuição Associativa (1ª Ocorrência)',
            ),
        'sindicato_cassoc2': fields.many2one(
            'res.partner',
            u'Contribuição Associativa (2ª Ocorrência)',
            ),
        'sindicato_cassist': fields.many2one(
            'res.partner', u'Contribuição Assistencial'
            ),
        'sindicato_csind': fields.many2one(
            'res.partner', u'Contribuição Sindical'
            ),
        'sindicato_cconf': fields.many2one(
            'res.partner', u'Contribuição Confederativa'
            ),
        'ocorrencia': fields.many2one(
            'l10n_br_hr.ocorrencia', u'Ocorrência', required=True,
            ),
        'tomador': fields.many2one(
            'res.partner',
            u'Tomador de Serviços',
            domain=[('tipo_pessoa', '=', 'J')],
            ),
        'optante_fgts': fields.boolean(u'Optante pelo FGTS'),
        'data_de_opcao': fields.date(u'Data de Opção pelo FGTS'),
        'movimentacao': fields.many2one(
            'l10n_br_hr.movimentacao', u'Movimentação'
            ),
        'data_de_movimentacao': fields.date(u'Data de Movimentação'),
        }

    def _get_default_company_address(self, cr, uid, context):
        company_obj = self.pool.get('res.company')
        company_id = company_obj._company_default_get(cr, uid, context=context)
        company = company_obj.browse(cr, uid, company_id, context=context)

        if company.state_id and company.l10n_br_city_id:
            return company
        return None

    def _get_default_company_state_id(self, cr, uid, context):
        address = self._get_default_company_address(cr, uid, context)
        if address:
            return address.state_id.id
        return None

    def _get_default_company_city_id(self, cr, uid, context):
        address = self._get_default_company_address(cr, uid, context)
        if address:
            return address.l10n_br_city_id.id
        return None

    _defaults = {
        'local_de_trabalho_estado': _get_default_company_state_id,
        'local_de_trabalho_cidade': _get_default_company_city_id,
        }

    def write(self, cr, uid, ids, vals, context=None):
        changes_obj = self.pool.get('l10n_br_hr.changes')
        changes_obj.register_changes(cr, uid, ids, 'hr_contract', vals)
        return super(hr_contract, self).write(cr, uid, ids, vals, context)

hr_contract()


class hr_contract_type(osv.osv):
    _inherit = 'hr.contract.type'
    _columns = {
        'name': fields.char('Contract Type', size=256, required=True),
        'code': fields.char(u'Código', size=2, required=True),
        }

hr_contract_type()


class hr_holidays_status(osv.osv):
    _inherit = 'hr.holidays.status'
    _columns = {
        'name': fields.char(u'Motivo de Afastamento', size=128, required=True),
        'code': fields.char(u'Código', size=2),
        }

    def name_search(self, cr, user, name, args=None, operator='ilike',
                    context=None, limit=80):
        if not args:
            args = []
        if context is None:
            context = {}
        ids = self.search(cr, user, [('code', '!=', '')] + args, limit=limit,
                          context=context)

        return self.name_get(cr, user, ids, context)

hr_holidays_status()
