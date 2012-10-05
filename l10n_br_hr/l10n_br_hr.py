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

        # FIXME: check if it is valid a PIS with 12 digits
        #elif len(val) > 11:
        #    pis_pasep = "%s.%s.%s-%s" % (val[0:4], val[4:9], val[9:11], val[11])

        return {'value': {'pis_pasep': pis_pasep}}

hr_employee()
