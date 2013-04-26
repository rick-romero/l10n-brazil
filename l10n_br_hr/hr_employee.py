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


class hr_employee(osv.osv):
    _inherit = 'hr.employee'

    def _get_address_data(self, cr, uid, ids, field_names, arg, context=None):
        """ Read the 'address' functional fields. """
        result = {}
        address_obj = self.pool.get('res.partner')
        for employee in self.browse(cr, uid, ids, context=context):
            result[employee.id] = {}.fromkeys(field_names, False)
            if employee.address_id:
                address = address_obj.read(cr, uid,
                                           employee.address_id.id,
                                           field_names, context=context)
                for field in field_names:
                    result[employee.id][field] = address[field] or False
        return result

    def _set_address_data(self, cr, uid, employee_id, name, value, arg,
                          context=None):
        """ Write the 'address' functional fields. """
        employee = self.browse(cr, uid, employee_id, context=context)
        address_obj = self.pool.get('res.partner')

        if employee.address_id:
            address_obj.write(cr, uid, [employee.address_id.id], {
                'name': employee.name + u' - Endereço Comercial',
                name: value or False,
                })
        else:
            address_id = address_obj.create(cr, uid, {
                'name': employee.name + u' - Endereço Comercial',
                name: value or False,
                }, context=context)
            self.write(cr, uid, [employee_id], {'address_id': address_id},
                       context=context)
        return True

    def _get_home_address_data(self, cr, uid, ids, field_names, arg,
                               context=None):
        """ Read the 'address' functional fields. """

        crossed_names = []
        a_fields = []
        e_fields = field_names

        for field in field_names:
            if field.startswith('home_'):
                fixed_name = field[len('home_'):]
                a_fields.append(fixed_name)
                crossed_names.append((field, fixed_name))

        result = {}
        address_obj = self.pool.get('res.partner')
        for employee in self.browse(cr, uid, ids, context=context):
            result[employee.id] = {}.fromkeys(e_fields, False)
            if employee.address_home_id:
                address = address_obj.read(cr, uid,
                                           employee.address_home_id.id,
                                           a_fields, context=context)
                for efield, afield in crossed_names:
                    result[employee.id][efield] = address[afield] or False
        return result

    def _set_home_address_data(self, cr, uid, employee_id, name, value, arg,
                               context=None):
        """ Write the 'address' functional fields. """
        name = name[len('home_'):]
        employee = self.browse(cr, uid, employee_id, context=context)
        address_obj = self.pool.get('res.partner')

        if employee.address_home_id:
            address_obj.write(cr, uid, [employee.address_home_id.id], {
                'name': employee.name + u' - Endereço Residencial',
                name: value or False,
                })
        else:
            address_id = address_obj.create(cr, uid, {
                'name': employee.name + u' - Endereço Residencial',
                name: value or False,
                }, context=context)
            self.write(cr, uid, [employee_id], {'address_home_id': address_id},
                       context=context)
        return True

    def _set_name_address(self, cr, uid, employee_id, name, value, arg,
                          context=None):
        """ Write the 'address' name. """
        employee = self.browse(cr, uid, employee_id, context=context)
        address_obj = self.pool.get('res.partner')

        if employee.address_id:
            address_obj.write(cr, uid, [employee.address_id.id], {
                'name': value + u' - Endereço Comercial',
                })

        if employee.address_home_id:
            address_obj.write(cr, uid, [employee.address_home_id.id], {
                'name': value + u' - Endereço Residencial',
                })

        return True

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
        'possui_alvara_judicial': fields.selection([
                ('1', 'Sim'),
                ('2', 'Não'),
            ],
            u'Possui Alvará Judicial',
            help=u'O menor de 16 que não é aprendiz deve possuir alvará ' + \
                u'judicial, autorizando o seu trabalho, para poder ser ' + \
                u'declarado na RAIS.'
            ),
        'matricula': fields.integer(u'Matrícula', size=11),
        'codigo_caixa': fields.char(u'Código Trabalhador CAIXA', size=11),

        'home_street': fields.function(
            _get_home_address_data, fnct_inv=_set_home_address_data,
            size=128, type='char', string=u'Rua',
            multi='home_address'
            ),
        'home_number': fields.function(
            _get_home_address_data, fnct_inv=_set_home_address_data,
            size=10, type='char', string=u'Número',
            multi='home_address'
            ),
        'home_street2': fields.function(
            _get_home_address_data, fnct_inv=_set_home_address_data,
            size=128, type='char', string=u'Complemento',
            multi='home_address'
            ),
        'home_zip': fields.function(
            _get_home_address_data, fnct_inv=_set_home_address_data,
            size=24, type='char', string=u'CEP',
            multi='home_address'
            ),
        'home_district': fields.function(
            _get_home_address_data, fnct_inv=_set_home_address_data,
            size=32, type='char', string=u'Bairro',
            multi='home_address'
            ),
        'home_l10n_br_city_id': fields.function(
            _get_home_address_data, fnct_inv=_set_home_address_data,
            type='many2one', domain="[('state_id','=',state_id)]",
            relation='l10n_br_base.city', string=u'Cidade',
            multi='home_address'
            ),
        'home_state_id': fields.function(
            _get_home_address_data, fnct_inv=_set_home_address_data,
            type='many2one', domain="[('country_id', '=', country_id)]",
            relation='res.country.state', string=u'Estado',
            multi='home_address'
            ),
        'home_country_id': fields.function(
            _get_home_address_data, fnct_inv=_set_home_address_data,
            type='many2one', relation='res.country', string=u'País',
            multi='home_address'
            ),
        'home_email': fields.function(
            _get_home_address_data, fnct_inv=_set_home_address_data,
            size=64, type='char', string=u'E-mail',
            multi='home_address'
            ),
        'home_phone': fields.function(
            _get_home_address_data, fnct_inv=_set_home_address_data,
            size=64, type='char', string=u'Telefone',
            multi='home_address'
            ),
        'home_mobile': fields.function(
            _get_home_address_data, fnct_inv=_set_home_address_data,
            size=64, type='char', string=u'Celular',
            multi='home_address'
            ),
        'home_fax': fields.function(
            _get_home_address_data, fnct_inv=_set_home_address_data,
            size=64, type='char', string=u'Fax',
            multi='home_address'
            ),

        'street': fields.function(
            _get_address_data, fnct_inv=_set_address_data,
            size=128, type='char', string=u'Rua',
            multi='address'
            ),
        'number': fields.function(
            _get_address_data, fnct_inv=_set_address_data,
            size=10, type='char', string=u'Número',
            multi='address'
            ),
        'street2': fields.function(
            _get_address_data, fnct_inv=_set_address_data,
            size=128, type='char', string=u'Complemento',
            multi='address'
            ),
        'zip': fields.function(
            _get_address_data, fnct_inv=_set_address_data,
            size=24, type='char', string=u'CEP',
            multi='address'
            ),
        'district': fields.function(
            _get_home_address_data, fnct_inv=_set_home_address_data,
            size=32, type='char', string=u'Bairro',
            multi='address'
            ),
        'l10n_br_city_id': fields.function(
            _get_address_data, fnct_inv=_set_address_data,
            type='many2one', domain="[('state_id','=',state_id)]",
            relation='l10n_br_base.city', string=u'Cidade',
            multi='address'
            ),
        'state_id': fields.function(
            _get_address_data, fnct_inv=_set_address_data,
            type='many2one', domain="[('country_id', '=', country_id)]",
            relation='res.country.state', string=u'Estado',
            multi='address'
            ),
        'country_id': fields.function(
            _get_address_data, fnct_inv=_set_address_data,
            type='many2one', relation='res.country', string=u'País',
            multi='address'
            ),
        'email': fields.function(
            _get_address_data, fnct_inv=_set_address_data,
            size=64, type='char', string=u'E-mail',
            multi='address'
            ),
        'phone': fields.function(
            _get_address_data, fnct_inv=_set_address_data,
            size=64, type='char', string=u'Telefone',
            multi='address'
            ),
        'mobile': fields.function(
            _get_address_data, fnct_inv=_set_address_data,
            size=64, type='char', string=u'Celular',
            multi='address'
            ),
        'fax': fields.function(
            _get_address_data, fnct_inv=_set_address_data,
            size=64, type='char', string=u'Fax',
            multi='address'
            ),
        }
    _defaults = {
        'matricula': lambda self, cr, uid, context: int(
            self.pool.get('ir.sequence').get(cr, uid, 'hr.employee.matricula')
            ),
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

    def write(self, cr, uid, ids, vals, context=None):
        result = super(hr_employee, self).write(cr, uid, ids, vals, context)
        changes_obj = self.pool.get('l10n_br_hr.changes')
        changes_obj.register_changes(cr, uid, ids, 'hr_employee', vals)

        # Write the 'address' name.
        for id in ids:
            employee = self.browse(cr, uid, id, context=context)
            address_obj = self.pool.get('res.partner')

            if employee.address_id:
                address_obj.write(cr, uid, [employee.address_id.id], {
                    'name': employee.name + u' - Endereço Comercial',
                    })

            if employee.address_home_id:
                address_obj.write(cr, uid, [employee.address_home_id.id], {
                    'name': employee.name + u' - Endereço Residencial',
                    })

        return result

    def get_active_contract(self, cr, uid, eid, date=None, context=None):
        """Get the active contract in the current month"""
        employee = self.browse(cr, uid, eid, context=context)
        contract = None

        if not date:
            date = datetime.datetime.today()

        current_year = int(date.strftime('%Y'))
        current_month = int(date.strftime('%m'))

        for c in employee.contract_ids:
            end_date = None

            date_start = datetime.datetime.strptime(
                c.date_start, '%Y-%m-%d'
                )
            start_year = int(date_start.strftime('%Y'))
            start_month = int(date_start.strftime('%m'))

            if c.data_de_desligamento:
                end_date = datetime.datetime.strptime(
                    c.data_de_desligamento, '%Y-%m-%d'
                    )
            elif c.date_end:
                end_date = datetime.datetime.strptime(c.date_end, '%Y-%m-%d')

            if not end_date:
                if (start_year == current_year and 
                    start_month <= current_month) or start_year < current_year:
                    contract = c
                    break
            else:
                end_year = int(end_date.strftime('%Y'))
                end_month = int(end_date.strftime('%m'))

                start_year_condition = ((start_year == current_year and
                    start_month <= current_month) or start_year < current_year)

                if start_year_condition and ((end_year == current_year and
                    end_month >= current_month) or end_year > current_year):

                    contract = c
                    break

        return contract

    def onchange_codigo_caixa(self, cr, uid, ids, codigo_caixa):
        if not codigo_caixa:
            return {}
        return {'value': {'codigo_caixa': re.sub('[^0-9]', '', codigo_caixa)}}

    def onchange_mask_zip(self, cr, uid, ids, field, zip):
        result = {'value': {field: False}}
        if not zip:
            return result
        val = re.sub('[^0-9]', '', zip)
        if len(val) >= 8:
            zip = "%s-%s" % (val[0:5], val[5:8])
            result['value'][field] = zip
        return result


hr_employee()
