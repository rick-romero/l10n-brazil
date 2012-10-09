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


class hr_employee(osv.osv):
    _inherit = 'hr.employee'
    _columns = {
        'pis_pasep': fields.char(u'PIS/PASEP', size=15),
        'nationality_id': fields.many2one(
            'l10n_br_hr.nationality', u'Nacionalidade'
            ),
        'etnia_id': fields.many2one('l10n_br_hr.etnia', _(u'Etnia')),
        'deficiencia': fields.selection((
            ('0', u'Não Possui'),
            ('1', u'Física'),
            ('2', u'Auditiva'),
            ('3', u'Visual'),
            ('4', u'Intelectual (Mental)'),
            ('5', u'Múltipla'),
            ('6', u'Reabilitado'),
            ), u'Deficiência'),
        'grau_de_instrucao_id': fields.many2one(
            'l10n_br_hr.grau_de_instrucao', u'Grau de Instrução'
            ),
        'ano_de_chegada': fields.integer(u'Ano de Chegada no Brasil'),
        'carteira_de_trabalho_numero': fields.integer(
            u'Número da Carteira de Trabalho', size=8
            ),
        'carteira_de_trabalho_serie': fields.integer(
            u'Número de Série da Carteira de Trabalho', size=5
            ),
        'cpf': fields.char(u'CPF', size=14),
        }

    def _validate_pis_pasep(self, cr, uid, ids):
        employee = self.browse(cr, uid, ids[0])

        if not employee.pis_pasep:
            return True

        digits = []
        for c in employee.pis_pasep:
            if c == '.' or c == ' ' or c == '\t':
                continue

            if c == '-':
                if len(digits) != 10:
                    return False
                continue

            if c.isdigit():
                digits.append(int(c))
                continue

            return False
        if len(digits) != 11:
            return False

        height = [int(x) for x in "3298765432"]

        total = 0

        for i in range(10):
            total += digits[i] * height[i]

        rest = total % 11
        if rest != 0:
            rest = 11 - rest
        return (rest == digits[10])

    def _validate_cpf(self, cr, uid, ids):
        employee = self.browse(cr, uid, ids[0])
        if not employee.cpf:
            return True

        cpf = employee.cpf

        if not cpf.isdigit():
            cpf = re.sub('[^0-9]', '', cpf)

        if len(cpf) != 11:
            return False

        cpf = map(int, cpf)
        novo = cpf[:9]

        while len(novo) < 11:
            r = sum([(len(novo) + 1 - i) * v for i, v in enumerate(novo)]) % 11

            if r > 1:
                f = 11 - r
            else:
                f = 0
            novo.append(f)

        if novo == cpf:
            return True

        return False

    _constraints = [
        (_validate_pis_pasep, u'Número PIS/PASEP é inválido.', ['pis_pasep']),
        (_validate_cpf, u'CPF inválido.', ['cpf']),
        ]

    def onchange_mask_cpf(self, cr, uid, ids, cpf):
        if not cpf:
            return {}
        val = re.sub('[^0-9]', '', cpf)

        if len(val) >= 11:
            cpf = "%s.%s.%s-%s" % (val[0:3], val[3:6], val[6:9], val[9:11])

        return {'value': {'cpf': cpf}}

    def onchange_mask_pis_pasep(self, cr, uid, ids, pis_pasep):
        if not pis_pasep:
            return {}
        val = re.sub('[^0-9]', '', pis_pasep)

        if len(val) >= 11:
            pis_pasep = "%s.%s.%s-%s" % (val[0:3], val[3:8], val[8:10], val[10])

        return {'value': {'pis_pasep': pis_pasep}}

hr_employee()


class hr_contract(osv.osv):
    _inherit = 'hr.contract'
    _columns = {
        'informacao_da_admissao': fields.selection((
            ('a', 'Admissão/Provimento'),
            ('t', 'Transferência/Movimentação'),
            ), u'Ação'),
        'tipo_de_admissao_id': fields.many2one(
            'l10n_br_hr.tipo_de_admissao', u'Tipo de Admissão'
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
        }

    def _get_default_company_address(self, cr, uid, context):
        company_obj = self.pool.get('res.company')
        company_id = company_obj._company_default_get(cr, uid, context=context)
        company = company_obj.browse(cr, uid, company_id, context=context)
        part_obj = self.pool.get('res.partner')
        address_obj = self.pool.get('res.partner.address')
        address_data = part_obj.address_get(cr, uid, [company.partner_id.id],
                                            adr_pref=['default'])
        if address_data['default']:
            address = address_obj.browse(cr, uid, address_data['default'],
                                         context=context)
            return address
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

hr_contract()
