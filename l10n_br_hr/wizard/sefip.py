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

from osv import fields, osv
from tools.translate import _
import datetime
import re
import unicodedata
import string


class l10n_br_hr_recolhimento(osv.osv):
    _name = 'l10n_br_hr.recolhimento'
    _description = u'Recolhimento'
    _columns = {
        'code': fields.char(u'Código', size=3, required=True),
        'name': fields.char(u'Recolhimento', size=290, required=True),
        }

class line:
    def __init__(self):
        self.content = ''

    def write_num(self, data, size):
        if not data:
            data = ''
        else:
            try:
                data = str(int(data))
            except:
                data = str(re.sub('[^0-9]', '', str(data)))

        pattern = '% {}s'.format(size)
        self.content += pattern % data

    def write_val(self, data, size):
        if not data:
            data = 0
        else:
            try:
                data = int(data)
            except:
                data = int(re.sub('[^0-9]', '', str(data)))

        pattern = '%0{}d'.format(size)
        self.content += pattern % data

    def write_str(self, data, size=None):
        if not data:
            data = ''

        if size is not None:
            stripped_data = data[:size]
            stripped_data_len = len(stripped_data)

            if stripped_data_len < size:
                stripped_data += ' ' * (size - stripped_data_len)

            self.content += stripped_data

        else:
            self.content += data


class sefip(osv.osv_memory):
    _name = 'l10n_br_hr.sefip'
    _description = 'Generate SEFIP File'
    _inherit = "ir.wizard.screen"
    _columns = {
        'state': fields.selection([('init', 'init'),
                                   ('done', 'done'),
                                   ], 'state', readonly=True),
        'last_sync_date': fields.datetime('Last Sync Date'),
        'message': fields.text('Message'),
        'file': fields.binary(u'Arquivo', readonly=True),
        'company': fields.many2one('res.company', u'Empresa',
                                      required=True),
        'ano_da_declaracao': fields.integer(u'Ano da Declaração', size=4),
        'responsavel_tipo_de_inscricao': fields.selection([
            ('1', 'CNPJ'),
            ('3', 'CPF'),
            ], u'Tipo de Inscrição', required=True
            ),
        'responsavel_cnpj': fields.char(u'CNPJ', size=18),
        'responsavel_cpf': fields.char(u'CPF', size=15),
        'responsavel_razao_social': fields.char(u'Razão Social', size=128, required=True),
        'responsavel_contato': fields.char(u'Nome do Contato', size=128, required=True),
        'responsavel_email': fields.char(u'E-mail', size=128),
        'responsavel_telefone': fields.char(u'Telefone', size=14, required=True),
        'responsavel_endereco': fields.char(u'Endereço', size=40, required=True),
        'responsavel_bairro': fields.char(u'Bairro', size=19, required=True),
        'responsavel_cep': fields.char(u'CEP', 9, required=True),
        'responsavel_cidade': fields.many2one('l10n_br_base.city', u'Cidade',
                                              required=True),
        'responsavel_pais': fields.many2one('res.country', u'País',
                                            required=True),
        'recolhimento': fields.many2one(
            'l10n_br_hr.recolhimento', u'Código de Recolhimento', required=True
            ),
        'competencia': fields.char(
            u'Competência', size=7, required=True,
            help=u'Data no formato MM/AAAA'
            ),
        'valores_pagos_a_cooperativas': fields.float(
            u'Valores pagos a Cooperativas de Trabalho'
            ),
        'fpas': fields.integer(u'FPAS', size=3, required=True),
        
        }
    _defaults = {
        'state': 'init',
        'ano_da_declaracao': lambda self, cr, uid, ids, c = {}: \
            int(datetime.datetime.today().strftime('%Y')) - 1,
        }

    def _validate_cnpj(self, cnpj):
        if not cnpj.isdigit():
            cnpj = re.sub('[^0-9]', '', cnpj)

        if len(cnpj) != 14:
            return False

        cnpj = map(int, cnpj)
        novo = cnpj[:12]

        prod = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
        while len(novo) < 14:
            r = sum([x * y for (x, y) in zip(novo, prod)]) % 11
            if r > 1:
                f = 11 - r
            else:
                f = 0
            novo.append(f)
            prod.insert(0, 6)

        if novo == cnpj:
            return True

        return False

    def _validate_cpf(self, cr, uid, ids):
        sefip_data = self.browse(cr, uid, ids[0])
        if not sefip_data.responsavel_cpf or \
            sefip_data.responsavel_tipo_de_inscricao != '3':
            return True

        cpf = sefip_data.responsavel_cpf

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

    def _validate_cep(self, cr, uid, ids):
        sefip_data = self.browse(cr, uid, ids[0])
        if not sefip_data.responsavel_cep:
            return False

        cep = sefip_data.responsavel_cep

        if not cep.isdigit():
            cep = re.sub('[^0-9]', '', cep)

        if len(cep) != 8:
            return False

        if cep in ['20000000', '30000000', '70000000', '80000000']:
            return False

        return True

    def _validate_telefone(self, cr, uid, ids):
        sefip_data = self.browse(cr, uid, ids[0])
        if not sefip_data.responsavel_telefone:
            return False

        telefone = sefip_data.responsavel_telefone

        if not telefone.isdigit():
            telefone = re.sub('[^0-9]', '', telefone)

        if len(telefone) < 9:
            return False

        return True

    def _constraint_responsavel_cnpj(self, cr, uid, ids):
        sefip_data = self.browse(cr, uid, ids[0])
        if not sefip_data.responsavel_cnpj or \
            sefip_data.responsavel_tipo_de_inscricao != '1':
            return True
        return self._validate_cnpj(sefip_data.responsavel_cnpj)

    def _validate_competencia(self, cr, uid, ids):
        sefip_data = self.browse(cr, uid, ids[0])
        month, year = sefip_data.competencia.split('/')
        code = sefip_data.recolhimento.code

        message = ''

        try:
            date_number = int(year + month)
            month = int(month)
            year = int(year)
        except:
            message = u'Data é inválida.'

        if message == '':
            if month < 1 or month > 13:
                message = u'O mês informado deve ser de 1 a 13.'
            elif year < 1967:
                message = u'O ano informado deve ser maior ou igual a 1967.'
            elif month == 13 and year < 1999:
                message = u'O mês 13 é válido apenas em ano maior ou igual a 1999'
            elif month == 13 and code in ['130', '135', '145', '211', '307',
                                          '317', '327', '337', '345', '640',
                                          '650', '660']:
                message = u'O mês 13 não é válido para o code informado.'
            elif code == '211' and date_number < 200003:
                message = u'Competência deve ser maior ou igual a 03/2000 para o code informado.'
            elif code == '640' and date_number >= 198810:
                message = u'Competência deve ser menor que 10/1988 para o code informado.'
            # TODO: Verificar como saber se é empregador doméstico
            #elif date_number < 200003:
            #    message = u'Competência deve ser maior ou igual a 03/2000 para empregador doméstico.'

        if message:
            raise osv.except_osv(u'Competência inválida.', message)

        return True

    _constraints = [
        (_constraint_responsavel_cnpj, u'CNPJ do responsável é inválido.',
         ['responsavel_cnpj']),
        (_validate_cpf, u'CPF do responsável é inválido.',
         ['responsavel_cpf']),
        (_validate_cep, u'CEP do responsável é inválido.',
         ['responsavel_cep']),
        (_validate_telefone, u'Telefone do responsável é inválido.',
         ['responsavel_teleone']),
        (_validate_competencia, u'Competência é inválida.', ['competencia']),
        ]

    def _mask_cnpj(self, cnpj, field_name='cnpj'):
        if not cnpj:
            return {}
        val = re.sub('[^0-9]', '', cnpj)

        if len(val) >= 14:
            cnpj = "%s.%s.%s/%s-%s" % (val[0:2], val[2:5], val[5:8], val[8:12], val[12:14])

        return {'value': {field_name: cnpj}}

    def _mask_cep(self, cep, field_name):
        if not cep:
            return {}
        val = re.sub('[^0-9]', '', cep)

        if len(val) >= 8:
            cep = "%s-%s" % (val[0:5], val[5:8])

        return {'value': {field_name: cep}}

    def onchange_responsavel_cnpj(self, cr, uid, ids, cnpj):
        return self._mask_cnpj(cnpj, 'responsavel_cnpj')

    def onchange_responsavel_cep(self, cr, uid, ids, cep):
        return self._mask_cep(cep, 'responsavel_cep')

    def onchange_responsavel_cpf(self, cr, uid, ids, cpf):
        if not cpf:
            return {}
        val = re.sub('[^0-9]', '', cpf)

        if len(val) >= 11:
            cpf = "%s.%s.%s-%s" % (val[0:3], val[3:6], val[6:9], val[9:11])

        return {'value': {'responsavel_cpf': cpf}}

    def onchange_competencia(self, cr, uid, ids, competencia):
        if not competencia:
            return {}
        val = re.sub('[^0-9]', '', competencia)

        if len(val) in (1, 2):
            current_year = int(datetime.datetime.today().strftime('%Y'))
            val = '%02d%d' % (int(val), current_year)

        if len(val) >= 6:
            competencia = "%s/%s" % (val[0:2], val[2:6])

        return {'value': {'competencia': competencia}}

    def _remove_accents(self, data):
        return ''.join(x for x in unicodedata.normalize('NFKD', unicode(data))\
            if x in string.ascii_letters + ' ').lower()

    def _clear_mixed(self, data):
        data = unicode(data)
        # Remove accents
        data = self._remove_accents(data)
        # More then one space between words is not allowed
        data = re.sub(r' {2,}', ' ', data)
        # Three or more chars cannot be repeated consecutively
        data = re.sub(r'(.)\1+', r'\1\1', data)
        # First position cannot be blank
        data = data.strip()
        return data

    def _clear_alfanum(self, data):
        data = self._clear_mixed(data)
        # Must contain olny A-Z chars and 0-9 numbers
        return str(re.sub('[^0-9a-zA-Z ]', '', str(data)))

    def _clear_alfa(self, data):
        data = self._clear_mixed(data)
        # Must contain olny A-Z chars
        return str(re.sub('[^a-zA-Z ]', '', str(data)))

    def generate_file(self, cr, uid, ids, context=None):

        sefip_data = self.browse(cr, uid, ids[0])
        recolhimento = sefip_data.recolhimento.code
        scope_month, scope_year = map(int, sefip_data.competencia.split('/'))
        scope_date = datetime.datetime.strptime(
            '%04d-%02d-%02d' % (scope_year, scope_month, 1),
            '%Y-%m-%d'
            )

        lines = []

        r = self.browse(cr, uid, ids[0])
        company = r.company

        partner_obj = self.pool.get('res.partner')
        partner_address_obj = self.pool.get('res.partner.address')
        changes_obj = self.pool.get('l10n_br_hr.changes')
        bank_obj = self.pool.get('res.partner.bank')
        holidays_obj = self.pool.get('hr.holidays')
        invoice_obj = self.pool.get('account.invoice')
        payslip_obj = self.pool.get('hr.payslip')
        payslip_line_obj = self.pool.get('hr.payslip.line')
        employee_obj = self.pool.get('hr.employee')
        employee_ids = employee_obj.search(cr, uid,
                                           [('company_id', '=', company.id)],
                                           context=context)
        employees = employee_obj.browse(cr, uid, employee_ids, context=context)
        index = 0

        grouped_payslips = {}
        categories = [
            'SFAMILIA', 'SMATERNIDADE',
            ]

        for employee in employees:
            for contract in employee.contract_ids:
                # check if contract was active in the base year and month
                date_end = None

                if contract.data_de_desligamento:
                    date_end = datetime.datetime.strptime(
                        contract.data_de_desligamento, '%Y-%m-%d'
                        )
                elif contract.date_end:
                    date_end = datetime.datetime.strptime(
                        contract.date_end, '%Y-%m-%d'
                        )

                if date_end:
                    end_year = int(date_end.strftime('%Y'))
                    end_month = int(date_end.strftime('%m'))

                    if (end_year == scope_year and end_month < scope_month) or\
                        end_year < scope_year:
                        del employees[index]
                        continue

                payslip_ids = payslip_obj.search(cr, uid, [
                        ('state', '=', 'done'),
                        ('contract_id', '=', contract.id),
                    ],
                    context=context
                    )
                payslips = payslip_obj.browse(
                    cr, uid, payslip_ids, context=context
                    )

                for category in categories:
                    grouped_payslips[category] = {'value': 0}

                for payslip in payslips:

                    date_from = datetime.datetime.strptime(
                        payslip.date_from, '%Y-%m-%d'
                        )
                    month = int(date_from.strftime('%m'))

                    p_line_ids = payslip_line_obj.search(cr, uid, [
                        ('slip_id', '=', payslip.id),
                        ('code', 'in', categories),
                        ], context=context)

                    if p_line_ids:
                        p_lines = payslip_line_obj.browse(
                            cr, uid, p_line_ids, context=context
                            )
                        for l in p_lines:

                            create_date = datetime.datetime.strptime(
                                l.create_date, '%Y-%m-%d %H:%M:%S'
                                )

                            try:
                                grouped_payslips[l.code][
                                    'value'] += l.total
                                grouped_payslips[l.code][
                                    'create_date'] = create_date
                            except:
                                grouped_payslips[l.code] = {
                                    'value': l.total,
                                    'create_date': create_date,
                                    }

            index += 1

        seq = 1

        if not company.cnpj:
            message = u'A empresa deve possuir CNPJ cadastrado'
            state = 'init'
            raise osv.except_osv(_('Error'), message)

        else:
            '''
            Registro 00 - Header - Informações do responsável
            '''
            r00 = line()

            # 1   2    Tipo de Registro
            r00.write_val(0, 2)
            # 3   53   Brancos
            r00.write_str('', 51)
            # 54  54   Tipo de Remessa
            r00.write_num(1, 1)
            # 55  55   Tipo de Inscrição - Responsável
            r00.write_num(sefip_data.responsavel_tipo_de_inscricao, 1)
            # 56  69   Inscrição do Responsável
            if sefip_data.responsavel_tipo_de_inscricao == '3':
                cpf_cnpj = sefip_data.responsavel_cpf
            else:
                cpf_cnpj = sefip_data.responsavel_cnpj

            r00.write_num(cpf_cnpj, 14)

            # 70  99   Nome Responsável (Razão Social)
            r00.write_str(
                self._clear_alfanum(sefip_data.responsavel_razao_social), 30
                )
            # 100 119  Nome Pessoa Contato
            r00.write_str(
                self._clear_alfa(sefip_data.responsavel_contato), 20
                )
            # 120 169  Logradouro, rua, nº, andar, apto
            r00.write_str(
                self._clear_alfanum(sefip_data.responsavel_endereco), 50
                )
            # 170 189  Bairro
            r00.write_str(
                self._clear_alfanum(sefip_data.responsavel_bairro), 20
                )
            # 190 197  CEP
            r00.write_num(sefip_data.responsavel_cep, 8)
            # 198 217  Cidade
            r00.write_str(
                self._clear_alfanum(sefip_data.responsavel_cidade.name), 20
                )
            # 218 219  Unidade da Federação
            r00.write_str(sefip_data.responsavel_pais.code, 2)
            # 220 231  Telefone Contato
            r00.write_num(sefip_data.responsavel_telefone, 12)
            # 232 291  Endereço Internet Contato
            r00.write_str(sefip_data.responsavel_email, 60)

            # 292 297  Competência
            month, year = sefip_data.competencia.split('/')
            mes_competencia = int(month)
            valor_competencia = int(year + month)
            r00.write_num(valor_competencia, 6)
            # 298 300  Código de Recolhimento
            r00.write_num(sefip_data.recolhimento.code, 3)

            # TODO: 301 301  Indicador de Recolhimento FGTS
            # TODO: 302 302  Modalidade do Arquivo
            # TODO: 303 310  Data de Recolhimento do FGTS
            # TODO: 311 311  Indicador de Recolhimento da Previdência Social
            # TODO: 312 319  Data de Recolhimento da Previdência Social
            # TODO: 320 326  Índice de Recolhimento de atraso da Previdência Social
            # TODO: 327 327  Tipo de Inscrição - Fornecedor Folha de Pagamento
            # TODO: 328 341  Inscrição do Fornecedor Folha de Pagamento

            # 342 359  Brancos
            r00.write_str('', 18)
            # 360 360  Final de Linha
            r00.write_str('*', 18)

            lines.append(r00)

            '''
            Registro 10 - Informações da empresa
            '''
            r10 = line()
            # 1   2    Tipo de Registro
            r10.write_val(10, 2)
            # 3   3    Tipo de Inscrição - Empresa - Fixo: 1 - CNPJ
            r10.write_val(1, 1)
            # 4   17   Inscrição da Empresa
            r10.write_num(sefip_data.company.cnpj, 14)
            # 18  53   Zeros
            r10.write_val(0, 36)
            # 54  93   Nome Empresa/Razão Social
            r10.write_str(sefip_data.company.legal_name, 40)
            # 94  143  Endereço
            default_address = partner_obj.address_get(
                cr, uid, [sefip_data.company.partner_id.id], ['default']
                )
            company_address = partner_address_obj.browse(
                cr, uid, default_address['default'], context=context
                )
            address = '{street} {number} {street2}'.format(
                street=company_address.street,
                number=company_address.number,
                street2=company_address.street2,
                )
            r10.write_str(self._clear_alfanum(address), 50)
            # 144 163  Bairro
            r10.write_str(company_address.district, 20)
            # 164 171  CEP
            r10.write_str(company_address.zip, 8)
            # 172 191  Cidade
            r10.write_str(
                self._clear_alfanum(company_address.l10n_br_city_id.name), 20
                )
            # 192 193  Unidade da Federação
            if company_address.state_id:
                r10.write_str(company_address.state_id.country_id.code, 2)
            else:
                raise osv.except_osv(
                    u'Falha na geração do arquivo.',
                    u'Faltam dados no endereço da empresa.',
                    )
            # 194 205  Telefone
            r10.write_str(company_address.phone, 12)
            # TODO: 206 206  Indicador de Alteração de Endereço
            # 207 213  CNAE
            r10.write_num(company.cnae_main_id.code, 7)
            # TODO: 214 214  Indicador de Alteração CNAE
            # TODO: 215 216  Alíquota RAT
            # TODO: 217 217  Código de Centralização
            # TODO: 218 218  SIMPLES

            # 219 221  FPAS
            # FIXME: Trocar campo aberto por tabela de códigos
            r10.write_num(sefip_data.fpas, 3)

            # TODO: 222 225  Código de Outras Entidades
            # TODO: 226 229  Código de Pagamento GPS
            # TODO: 230 234  Percentual de Isenção de Filantropia

            # 235 249  Salário-Família
            if mes_competencia == 13 or valor_competencia < 199810 or \
                sefip_data.recolhimento.code in ['145', '307', '327', '345',
                                                 '640', '650', '660', '868']:
                sfamilia = 0
            else:
                sfamilia = grouped_payslips['SFAMILIA']['value']

            r10.write_val(sfamilia, 15)
            # 250 264  Salário-Maternidade
            if mes_competencia == 13 or valor_competencia < 199810 or \
                valor_competencia >= 200006 and valor_competencia <= 200308 or\
                sefip_data.recolhimento.code in ['130', '135', '145', '211',
                                                 '307', '317', '327', '337',
                                                 '345', '640', '650', '660']:
                smaternidade = 0
            else:
                smaternidade = grouped_payslips['SMATERNIDADE']['value']

            r10.write_val(smaternidade, 15)

            # TODO: 265 279  Contrib. Desc. Empregado Referente à Competência 13
            # TODO: 280 280  Indicador de valor negativo ou positivo
            # TODO: 281 294  Valor Devido à Previdência Social Referente à Comp. 13


            bank_ids = bank_obj.search(cr, uid, [('company_id', '=', company.id)])
            if bank_ids:
                bank = bank_obj.browse(cr, uid, bank_ids[0], context=context)

                # 295 297  Banco
                r10.write_num(bank.bank, 3)
                # 298 301  Agência
                r10.write_num(bank.bra_number, 4)
                # 302 310  Conta Corrente
                r10.write_str(bank.acc_number, 9)
            else:
                r10.write_str('', 16)

            # 311 355  Zeros
            r10.write_val(0, 45)
            # 356 359  Brancos
            r10.write_str('', 4)
            # 360 360  Final de Linha
            r10.write_str('*', 1)
            lines.append(r10)

            '''
            Registro 12 - Informações adicionais do recolhimento da empresa
            '''
            r12 = line()
            # 1   2    Tipo de Registro
            r12.write_val(12, 2)
            # 3   3    Tipo de Inscrição - Empresa - Fixo: 1 - CNPJ
            r12.write_val(1, 1)
            # 4   17   Inscrição da Empresa
            r12.write_num(sefip_data.company.cnpj, 14)
            # 18  53   Zeros
            r12.write_val(0, 36)
            # TODO: 54  68   Dedução 13º Salário Licença Maternidade
            # TODO: 69  83   Receita Evento Desportivo/Patrocínio
            # TODO: 84  84   Indicativo Origem da Receita
            # TODO: 85  99   Comercialização da Produção - Pessoa Física
            # TODO: 100 114  Comercialização da Produção - Pessoa Jurídica
            # TODO: 115 125  Outras Informações Processo
            # TODO: 126 129  Outras Informações Processo - Ano
            # TODO: 130 134  Outras Informações Vara/JCJ
            # TODO: 135 140  Outras Informações Período Início
            # TODO: 141 146  Outras Informações Período Fim
            # TODO: 147 161  Compensação - Valor Corrigido
            # TODO: 162 167  Compensação - Período Início
            # TODO: 168 173  Compensação - Período Fim
            # TODO: 174 188  Recolhimento de Competências Anteriores - Valor do INSS sobre Folha de Pagamento
            # TODO: 189 203  Recolhimento de Competências Anteriores - Outras Entidades sobre Folha de Pagamento
            # TODO: 204 218  Recolhimento de Competências Anteriores - Comercialização de Produção - Valor do INSS
            # TODO: 219 233  Recolhimento de Competências Anteriores - Comercialização de Produção - Outras Entidades
            # TODO: 234 248  Recolhimento de Competências Anteriores - Receita de Evento Desportivo/Patrocínio - Valor do INSS
            # TODO: 249 263  Parcelamento do FGTS - Somatório Remunerações das Categorias 1, 2, 3, 5 e 6
            # TODO: 264 278  Parcelamento do FGTS - Somatório Remunerações das Categorias 4 e 7
            # TODO: 279 293  Parcelamento do FGTS - Valor Recolhido

            # 294 308  Valores pagos a Cooperativas de Trabalho - Serviços Prestados
            fpas_int = int(sefip_data.fpas)
            if mes_competencia == 13 or valor_competencia < 200003 or \
                (valor_competencia > 200110 and recolhimento == '150' and \
                 fpas_int == 604) or fpas_int == 868 or \
                recolhimento in ['130', '135', '145', '211', '307', '317',
                                 '327', '337', '345', '608', '640', '650',
                                 '660']:
                valores_pagos = 0
            else:
                valores_pagos = sefip_data.valores_pagos_a_cooperativas
            r12.write_val(valores_pagos, 15)

            # 309 353  Implementação Futura
            r12.write_val(0, 45)
            # 354 359  Brancos
            r12.write_str('', 6)
            # 360 360  Final da Linha
            r12.write_str('*', 1)
            lines.append(r12)

            '''
            Registro 13 - Alteração cadastral do trabalhador
            '''
            # check if changes were made during the month scope
            employee_changes = {}
            changed_employees = []
            address_changed_employees = []
            contract_changed_employees = []
            partner_changed_employees = []
            tables = ['hr_employee', 'hr_contract', 'res_partner',
                      'res_partner_address']

            for table in tables:
                employee_changes[table] = {}

            changes_ids = changes_obj.search(cr, uid, [
                ('table', 'in', tables),
                ], context=context)
            changes = changes_obj.browse(cr, uid, changes_ids, context=context)

            for change in changes:

                data = changes_obj.perm_read(cr, uid, [change.id], context=context)[0]
                create_date = datetime.datetime.strptime(
                    data['create_date'], '%Y-%m-%d %H:%M:%S.%f'
                    )
                create_month = int(create_date.strftime('%m'))
                create_year = int(create_date.strftime('%Y'))
                if create_month == scope_month and create_year == scope_year:
                    try:
                        employee_changes[change.table][change.register_id\
                                                       ].append(change)
                    except:
                        employee_changes[change.table][change.register_id] = []
                        employee_changes[change.table][change.register_id\
                                                       ].append(change)

            for employee in employees:
                if employee.id in employee_changes['hr_employee']:
                    changed_employees.append(employee)
                if employee.address_home_id.id in employee_changes\
                    ['res_partner_address']:
                    address_changed_employees.append(employee)
                
                for contract in employee.contract_ids:
                    if contract.id in employee_changes['hr_contract']:
                        contract_changed_employees.append(contract)

                if not employee.address_home_id.partner_id:
                    raise osv.except_osv(
                        u'Falha na geração do arquivo.',
                        u'Faltam dados no endereço do colaborador {}.'.format(
                            employee.name
                            ),
                        )
                if employee.address_home_id.partner_id.id in employee_changes\
                    ['res_partner']:
                    partner_changed_employees.append(employee)

            # hr_employee
            if changed_employees:
                for employee in changed_employees:
                    for change in employee_changes['hr_employee'][employee.id]:

                        contract = employee_obj.get_active_contract(
                            cr, uid, employee.id, date=scope_date,
                            context=context
                            )

                        if not contract:
                            continue

                        r13 = line()
                        # 1   2    Tipo de Registro
                        r13.write_val(13, 2)
                        # 3   3    Tipo de Inscrição - Fixo: 1 - CNPJ
                        r13.write_val(1, 1)
                        # 4   17   Inscrição da Empresa
                        r13.write_num(sefip_data.company.cnpj, 14)
                        # 18  53   Zeros
                        r13.write_val(0, 36)
                        # 54  64   PIS/PASEP
                        r13.write_num(employee.pis_pasep, 11)

                        # 65  72   Data de Admissão
                        if contract.date_start:
                            date_start = datetime.datetime.strptime(
                                contract.date_start, '%Y-%m-%d'
                                )
                            r13.write_str(date_start.strftime('%d%m%Y'), 8)
                        else:
                            r13.write_val(0, 8)

                        # 73  74   Categoria Trabalhador
                        if not contract.type_id.code:
                            contract_type = 1
                        else:
                            contract_type = contract.type_id.code

                        r13.write_val(contract_type, 2)

                        # 75  85   Matrícula do Trabalhador
                        if contract_type == 6 or not employee.matricula:
                            r13.write_str('', 11)
                        else:
                            r13.write_val(employee.matricula, 11)
                        # 86  92   Número CTPS
                        r13.write_num(employee.carteira_de_trabalho_numero, 7)
                        # 93  97   Série CTPS
                        r13.write_num(employee.carteira_de_trabalho_serie, 5)
                        # 98  167  Nome Trabalhador
                        r13.write_str(self._clear_alfanum(employee.name), 70)
                        # TODO: 168 181  Código Empresa CAIXA
                        # TODO: 182 192  Código Trabalhador CAIXA

                        # 193 195  Código Alteração Cadastral
                        change_code = None
                        if change.field in ('carteira_de_trabalho_serie',
                                            'carteira_de_trabalho_numero'):
                            change_code = 403
                        elif change.field == 'name':
                            change_code = 404
                        elif change.field == 'pis_pasep':
                            change_code = 405
                        elif change.field == 'matricula':
                            change_code = 406
                        else:
                            continue

                        r13.write_num(change_code, 3)
                        # 196 265  Novo Conteúdo do Campo
                        r13.write_str(change.new_value, 70)

                        # 266 359  Brancos
                        r13.write_str('', 94)
                        # 360 360  Final da Linha
                        r13.write_str('*', 1)
                        lines.append(r13)

            # hr_contract
            if contract_changed_employees:
                for contract in contract_changed_employees:
                    for change in employee_changes['hr_contract'][contract.id]:

                        r13 = line()
                        # 1   2    Tipo de Registro
                        r13.write_val(13, 2)
                        # 3   3    Tipo de Inscrição - Fixo: 1 - CNPJ
                        r13.write_val(1, 1)
                        # 4   17   Inscrição da Empresa
                        r13.write_num(sefip_data.company.cnpj, 14)
                        # 18  53   Zeros
                        r13.write_val(0, 36)
                        # 54  64   PIS/PASEP
                        r13.write_num(employee.pis_pasep, 11)

                        # 65  72   Data de Admissão
                        if contract.date_start:
                            date_start = datetime.datetime.strptime(
                                contract.date_start, '%Y-%m-%d'
                                )
                            r13.write_str(date_start.strftime('%d%m%Y'), 8)
                        else:
                            r13.write_val(0, 8)

                        # 73  74   Categoria Trabalhador
                        if not contract.type_id.code:
                            contract_type = 1
                        else:
                            contract_type = contract.type_id.code

                        r13.write_val(contract_type, 2)

                        # 75  85   Matrícula do Trabalhador
                        if contract_type == 6 or not employee.matricula:
                            r13.write_str('', 11)
                        else:
                            r13.write_val(employee.matricula, 11)
                        # 86  92   Número CTPS
                        r13.write_num(
                            contract.employee_id.carteira_de_trabalho_numero,
                            7
                            )
                        # 93  97   Série CTPS
                        r13.write_num(
                            contract.employee_id.carteira_de_trabalho_serie, 5
                            )
                        # 98  167  Nome Trabalhador
                        r13.write_str(
                            self._clear_alfanum(contract.employee_id.name), 70
                            )
                        # TODO: 168 181  Código Empresa CAIXA
                        # TODO: 182 192  Código Trabalhador CAIXA

                        # 193 195  Código Alteração Cadastral
                        change_code = None
                        new_value = change.new_value

                        if change.field == 'date_start':
                            change_code = 408
                        elif change.field == 'ocupacao_id':
                            if not contract.ocupacao_id:
                                raise osv.except_osv(
                                    u'Falha na geração do arquivo.',
                                    u'É necessário informar a ocupação no contrato %s.' % \
                                        contract.name,
                                    )
                            change_code = 427
                            new_value = '0' + contract.ocupacao_id.code[:4]
                        else:
                            continue

                        r13.write_num(change_code, 3)
                        # 196 265  Novo Conteúdo do Campo
                        r13.write_str(new_value, 70)

                        # 266 359  Brancos
                        r13.write_str('', 94)
                        # 360 360  Final da Linha
                        r13.write_str('*', 1)
                        lines.append(r13)

            # res_partner
            if partner_changed_employees:
                for employee in partner_changed_employees:
                    for change in employee_changes['res_partner'][employee.id]:
                        
                        if change.field != 'birthday':
                            continue

                        r13 = line()
                        # 1   2    Tipo de Registro
                        r13.write_val(13, 2)
                        # 3   3    Tipo de Inscrição - Fixo: 1 - CNPJ
                        r13.write_val(1, 1)
                        # 4   17   Inscrição da Empresa
                        r13.write_num(sefip_data.company.cnpj, 14)
                        # 18  53   Zeros
                        r13.write_val(0, 36)
                        # 54  64   PIS/PASEP
                        r13.write_num(employee.pis_pasep, 11)

                        # 65  72   Data de Admissão
                        if contract.date_start:
                            date_start = datetime.datetime.strptime(
                                contract.date_start, '%Y-%m-%d'
                                )
                            r13.write_str(date_start.strftime('%d%m%Y'), 8)
                        else:
                            r13.write_val(0, 8)

                        # 73  74   Categoria Trabalhador
                        if not contract.type_id.code:
                            contract_type = 1
                        else:
                            contract_type = contract.type_id.code

                        r13.write_val(contract_type, 2)

                        # 75  85   Matrícula do Trabalhador
                        if contract_type == 6 or not employee.matricula:
                            r13.write_str('', 11)
                        else:
                            r13.write_val(employee.matricula, 11)
                        # 86  92   Número CTPS
                        r13.write_num(employee.carteira_de_trabalho_numero, 7)
                        # 93  97   Série CTPS
                        r13.write_num(employee.carteira_de_trabalho_serie, 5)
                        # 98  167  Nome Trabalhador
                        r13.write_str(self._clear_alfanum(employee.name), 70)
                        # TODO: 168 181  Código Empresa CAIXA
                        # TODO: 182 192  Código Trabalhador CAIXA

                        # 193 195  Código Alteração Cadastral
                        # Alteração de data de nascimento
                        change_code = 428

                        r13.write_num(change_code, 3)
                        # 196 265  Novo Conteúdo do Campo
                        r13.write_str(change.new_value, 70)

                        # 266 359  Brancos
                        r13.write_str('', 94)
                        # 360 360  Final da Linha
                        r13.write_str('*', 1)
                        lines.append(r13)

            '''
            Registro 14 - Inclusão/alteração do endereço do trabalhador
            '''
            # res_partner_address
            if address_changed_employees:
                for employee in address_changed_employees:

                    contract = employee_obj.get_active_contract(
                        cr, uid, employee.id, date=scope_date, context=context
                        )
    
                    if not contract:
                        continue

                    r14 = line()
                    # 1   2    Tipo de Registro
                    r14.write_val(14, 2)
                    # 3   3    Tipo de Inscrição - Fixo: 1 - CNPJ
                    r14.write_val(1, 1) 
                    # 4   17   Inscrição da Empresa
                    r14.write_num(sefip_data.company.cnpj, 14)
                    # 18  53   Zeros
                    r14.write_val(0, 36)
                    # 54  64   PIS/PASEP/CI
                    r14.write_val(employee.pis_pasep, 11)
                    # 65  72   Data Admissão
                    if contract.date_start:
                        date_start = datetime.datetime.strptime(
                            contract.date_start, '%Y-%m-%d'
                            )
                        r14.write_str(date_start.strftime('%d%m%Y'), 8)
                    else:
                        r14.write_val(0, 8)
                    # 73  74   Categoria Trabalhador
                    if not contract.type_id.code:
                        contract_type = 1
                    else:
                        contract_type = contract.type_id.code

                    r14.write_val(contract_type, 2)

                    # 75  144  Nome Trabalhador
                    r14.write_str(self._clear_alfanum(employee.name), 70)
                    # 145 151  Número CTPS
                    r14.write_num(employee.carteira_de_trabalho_numero, 7)
                    # 152 156  Série CTPS
                    r14.write_num(employee.carteira_de_trabalho_serie, 5)
                    # 157 206  Logradouro, rua, nº, apto
                    r14.write_str(self._clear_alfanum(
                            employee.address_home_id.street
                        ), 50)
                    # 207 226  Bairro
                    r14.write_str(self._clear_alfanum(
                            employee.address_home_id.district
                        ), 20)
                    # 227 234  CEP
                    r14.write_str(employee.address_home_id.zip, 8)
                    # 235 254  Cidade
                    r14.write_str(self._clear_alfanum(
                            employee.address_home_id.l10n_br_city_id.name
                        ), 20)
                    # 255 256  Unidade da Federação
                    employee_state = employee.address_home_id.state_id

                    if employee_state:
                        r14.write_str(employee_state.country_id.code, 2)
                    else:
                        raise osv.except_osv(
                            u'Falha na geração do arquivo.',
                            u'Faltam dados no endereço do colaborador.',
                            )

                    # 257 359  Brancos
                    r14.write_str('', 103)
                    # 360 360  Final da Linha
                    r14.write_str('*', 1)
                    lines.append(r14)

            invoice_ids = invoice_obj.search(cr, uid, [
                    ('fiscal_type', '=', 'service'),
                    ('company_id', '=', company.id)
                ], context=context
                )
            invoices = invoice_obj.browse(cr, uid, invoice_ids, context=context)

            for invoice in invoices:

                address = invoice.partner_id.address[0]

                '''
                Registro 20 - Registro do tomador de serviço/obra
                '''
                r20 = line()
                # 1   2    Tipo de Registro
                r20.write_val(20, 2)
                # 3   3    Tipo de Inscrição - Fixo: 1 - CNPJ
                r20.write_val(1, 1)
                # 4   17   Inscrição da Empresa
                r20.write_num(sefip_data.company.cnpj, 14)
                # 18  18   Tipo de Inscrição-Tomador/Obra Const. Civil
                # Fixo: 1 - CNPJ
                r20.write_num(1, 1)
                # 19  32   Inscrição Tomador/Obra Const. Civil
                r20.write_num(invoice.partner_id.cnpj_cpf, 14)
                # 33  53   Zeros
                r20.write_val(0, 21)
                # 54  93   Nome do Tomador/Obra de Const. Civil
                r20.write_str(self._clear_alfanum(invoice.partner_id.name), 40)
                # 94  143  Logradouro, rua, nº, apto
                street = '{street} {number} {street2}'.format(
                    street=address.street,
                    number=address.number,
                    street2=address.street2,
                    )
                r20.write_str(self._clear_alfanum(street), 50)
                # 144 163  Bairro
                r20.write_str(self._clear_alfanum(address.district), 20)
                # 164 171  CEP
                r20.write_num(address.zip, 8)
                # 172 191  Cidade
                r20.write_str(self._clear_alfanum(
                        address.l10n_br_city_id.name
                    ), 20)
                # 192 193  Unidade da Federação
                if address.state_id:
                    r20.write_str(address.state_id.country_id.code, 2)
                else:
                    raise osv.except_osv(
                        u'Falha na geração do arquivo.',
                        u'Faltam dados no endereço do colaborador %s.' % \
                            invoice.partner_id.name,
                        )
                # TODO: 194 197  Código de Pagamento GPS
                # TODO: 198 212  Salário Família
                # TODO: 213 227  Contrib. Desc. Empregado Referente à Competência 13
                # TODO: 228 228  Indicador de Valor Negativo ou Positivo
                # TODO: 229 242  Valor Devido à Previdência Social Referente à Competência 13
                # TODO: 243 257  Valor de Retenção
                # TODO: 258 272  Valor das Faturas Emitidas para o Tomador

                # 273 317  Zeros
                r20.write_val(0, 45)
                # 318 359  Brancos
                r20.write_str('', 42)
                # 360 360  Final da Linha
                r20.write_str('*', 1)
                lines.append(r20)

                '''
                Registro 21 - Informações adicionais do tomador de serviço/obra
                '''
                r21 = line()
                # 1   2    Tipo de Registro
                r21.write_val(21, 2)
                # 3   3    Tipo de Inscrição - Fixo: 1 - CNPJ
                r21.write_val(1, 1)
                # 4   17   Inscrição da Empresa
                r21.write_num(sefip_data.company.cnpj, 14)
                # 18  18   Tipo de Inscrição-Trabalhador/Obra Const. Civil
                # Fixo: 1 - CNPJ
                r21.write_val(1, 1)
                # 19  32   Inscrição Tomador/Obra Const. Civil
                r21.write_num(invoice.partner_id.cnpj_cpf, 14)
                # 33  53   Zeros
                r21.write_val(0, 21)
                # TODO: 54  68   Compensação - Valor Corrigido
                # TODO: 69  74   Compensação - Período Início
                # TODO: 75  80   Compensação - Período Fim
                # TODO: 81  95   Recolhimento de Competências Anteriores - Valor do INSS sobre Folha de Pagamento
                # TODO: 96  110  Recolhimento de Competências Anteriores - Outras Entidades sobre Folha de Pagamento
                # TODO: 111 125  Parcelamento do FGTS - somatório das remunerações das categorias 1, 2, 3, 5 e 6
                # TODO: 126 140  Parcelamento do FGTS - somatório das remunerações das categorias 4 e 7
                # TODO: 141 155  Parcelamento do FGTS - valor recolhido
                # 156 359  Brancos
                r21.write_str('', 204)
                # 360 360  Final da Linha
                r21.write_str('*', 1)
                lines.append(r21)

            for employee in employees:
                print
                print 'employee.name', employee.name

                contract = employee_obj.get_active_contract(
                    cr, uid, employee.id, date=scope_date, context=context
                    )

                if not contract:
                    continue

                print 'contract.id', contract.id

                '''
                Registro 30 - Registro do trabalhador
                '''
                r30 = line()
                # 1   2    Tipo de Registro
                r30.write_val(30, 2)
                # 3   3    Tipo de Inscrição - Fixo: 1 - CNPJ
                r30.write_val(1, 1)
                # 4   17   Inscrição da Empresa
                r30.write_num(sefip_data.company.cnpj, 14)
                # TODO: 18  18   Tipo de Inscrição-Tomador/Obra Const. Civil
                # TODO: 19  32   Inscrição Tomador/Obra Const. Civil
                # 33  43   PIS/PASEP/CI
                r30.write_num(employee.pis_pasep, 11)
                # 44  51   Data de Admissão
                if contract.date_start:
                    date_start = datetime.datetime.strptime(
                        contract.date_start, '%Y-%m-%d'
                        )
                    r30.write_str(date_start.strftime('%d%m%Y'), 8)
                else:
                    r30.write_val(0, 8)
                # 52  53   Categoria Trabalhador
                if not contract.type_id.code:
                    contract_type = 1
                else:
                    contract_type = contract.type_id.code

                r30.write_val(contract_type, 2)

                # 54  123  Nome Trabalhador
                r30.write_str(self._clear_alfanum(employee.name), 70)
                # 124 134  Matrícula do Empregado
                if contract_type == 6 or not employee.matricula:
                    r30.write_str('', 11)
                else:
                    r30.write_val(employee.matricula, 11)
                # 135 141  Número CTPS
                r30.write_num(employee.carteira_de_trabalho_numero, 7)
                # 142 146  Série CTPS
                r30.write_num(employee.carteira_de_trabalho_serie, 5)
                # TODO: 147 154  Data de Opção
                # 155 162  Data de Nascimento
                r30.write_num(employee.address_home_id.partner_id.birthday, 5)
                # 163 167  CBO - Código Brasileiro de Ocupação
                '''
                SEFIP pede o código da família, que é composto pelos 4
                primeiros dígitos da ocupação
                '''
                if not contract.ocupacao_id:
                    raise osv.except_osv(
                        u'Falha na geração do arquivo.',
                        u'É necessário informar a ocupação no contrato %s.' % \
                            contract.name,
                        )
                r30.write_val(contract.ocupacao_id.code[:4], 5)
                # TODO: 168 182  Remuneração sem 13º
                # TODO: 183 197  Remuneração 13º
                # TODO: 198 199  Classe de Contribuição
                # 200 201  Ocorrência
                r30.write_str(contract.ocorrencia.code, 2)
                # TODO: 202 216  Valor Descontado do Segurado
                # TODO: 217 231  Remuneração Base de Cálculo da Contribuição Previdenciária
                # TODO: 232 246  Base de Cálculo 13º Salário Previdência Social - Referente a Competência do Movimento
                # TODO: 247 261  Base de Cálculo 13º Salário Previdência Social - Referente a GPS da Competência 13
                # 262 359  Brancos
                r30.write_str('', 98)
                # 360 360  Final da Linha
                r30.write_str('*', 1)
                lines.append(r30)
    
                '''
                Registro 32 - Registro de movimentação do trabalhador
                '''
                r32 = line()
                # 1   2    Tipo de Registro
                r32.write_val(32, 2)
                # 3   3    Tipo de Inscrição - Fixo: 1 - CNPJ
                r32.write_val(1, 1)
                # 4   17   Inscrição da Empresa
                r32.write_num(sefip_data.company.cnpj, 14)
                # TODO: 18  18   Tipo de Inscrição-Trabalhador/Obra Const. Civil
                # TODO: 19  32   Inscrição Tomador/Obra Const. Civil
                # 33  43   PIS/PASEP/CI
                r32.write_num(employee.pis_pasep, 11)
                # 44  51   Data de Admissão
                if contract.date_start:
                    date_start = datetime.datetime.strptime(
                        contract.date_start, '%Y-%m-%d'
                        )
                    r32.write_str(date_start.strftime('%d%m%Y'), 8)
                else:
                    r32.write_val(0, 8)

                # 52  53   Categoria Trabalhador
                if not contract.type_id.code:
                    contract_type = 1
                else:
                    contract_type = contract.type_id.code

                r32.write_val(contract_type, 2)

                # 54  123  Nome Trabalhador
                r32.write_str(self._clear_alfanum(employee.name), 70)
                # TODO: 124 125  Código da Movimentação
                # TODO: 126 133  Data de Movimentação
                # TODO: 134 134  Indicativo de Recolhimento do FGTS
                # 135 359  Brancos
                r32.write_str('', 225)
                # 360 360  Final da Linha
                r32.write_str('*', 1)
                lines.append(r32)

            '''
            Registro 50 - Registro de empresa - documento específico de
            recolhimento do FGTS (sua utilização exige autorização da CAIXA)
            '''
            r50 = line()
            # 1   2    Tipo de Registro
            r50.write_val(50, 2)
            # 3   3    Tipo de Inscrição - Fixo: 1 - CNPJ
            r50.write_val(1, 1)
            # 4   17   Inscrição da Empresa
            r50.write_num(sefip_data.company.cnpj, 14)
            # 18  53   Zeros
            r50.write_val(0, 36)
            # 54  93   Nome Empresa/Razão Social
            r50.write_str(sefip_data.company.legal_name, 40)
            # TODO: 94  94   Tipo de Inscrição - Tomador
            # TODO: 95  108  Inscrição Tomador
            # TODO: 109 148  Nome do Tomador de Serviço/Obra de Const. Civil
            # 149 198  Logradouro, rua, nº, apto
            default_address = partner_obj.address_get(
                cr, uid, [sefip_data.company.partner_id.id], ['default']
                )
            company_address = partner_address_obj.browse(
                cr, uid, default_address['default'], context=context
                )
            address = '{street} {number} {street2}'.format(
                street=company_address.street,
                number=company_address.number,
                street2=company_address.street2,
                )
            r50.write_str(self._clear_alfanum(address), 50)
            # 199 218  Bairro
            r50.write_str(company_address.district, 20)
            # 219 226  CEP
            r50.write_str(company_address.zip, 8)
            # 227 246  Cidade
            r50.write_str(
                self._clear_alfanum(company_address.l10n_br_city_id.name), 20
                )
            # 247 248  Unidade da Federação
            if company_address.state_id:
                r50.write_str(company_address.state_id.country_id.code, 2)
            else:
                raise osv.except_osv(
                    u'Falha na geração do arquivo.',
                    u'Faltam dados no endereço da empresa.',
                    )
            # 249 260  Telefone
            r50.write_str(company_address.phone, 12)
            # 261 267  CNAE
            r50.write_num(company.cnae_main_id.code, 7)
            # TODO: 268 268  Código de Centralização
            # TODO: 269 283  Valor da Multa - Informar o valor total da multa a ser recolhida
            # 284 359  Brancos
            r50.write_str('', 76)
            # 360 360  Final da Linha
            r50.write_str('*', 1)
            lines.append(r50)

            # TODO: verificar como obter se empresa está autorizada
            '''
            Registro 51 - Registro de individualização de valores recolhidos -
            documento específico de recolhimento do FGTS (sua utilização exige
            autorização da CAIXA)
            '''
            for employee in employees:

                contract = employee_obj.get_active_contract(
                    cr, uid, employee.id, date=scope_date, context=context
                    )

                if not contract:
                    continue

                r51 = line()
                # 1   2    Tipo de Registro30
                r51.write_val(51, 2)
                # 3   3    Tipo de Inscrição - Fixo: 1 - CNPJ
                r51.write_val(1, 1)
                # 4   17   Inscrição da Empresa
                r51.write_num(sefip_data.company.cnpj, 14)
                # TODO: 18  18   Tipo de Inscrição - Tomador
                # TODO: 19  32   Inscrição Tomador
                # 33  43   PIS/PASEP
                r51.write_num(employee.pis_pasep, 11)
                # 44  51   Data de Admissão
                if contract.date_start:
                    date_start = datetime.datetime.strptime(
                        contract.date_start, '%Y-%m-%d'
                        )
                    r51.write_str(date_start.strftime('%d%m%Y'), 8)
                else:
                    r51.write_val(0, 8)

                # 52  53   Categoria Trabalhador
                if not contract.type_id.code:
                    contract_type = 1
                else:
                    contract_type = contract.type_id.code

                r51.write_val(contract_type, 2)

                # 54  123  Nome Trabalhador
                r51.write_str(self._clear_alfanum(employee.name), 70)
                # 124 134  Matrícula do Empregado
                if contract_type == 6 or not employee.matricula:
                    r51.write_str('', 11)
                else:
                    r51.write_val(employee.matricula, 11)
                # 135 141  Número CTPS
                r51.write_num(employee.carteira_de_trabalho_numero, 7)
                # 142 146  Série CTPS
                r51.write_num(employee.carteira_de_trabalho_serie, 5)
                # TODO: 147 154  Data de Opção
                # 155 162  Data de Nascimento
                r51.write_num(employee.address_home_id.partner_id.birthday, 5)
                # 163 167  CBO - Código Brasileiro de Ocupação
                '''
                SEFIP pede o código da família, que é composto pelos 4
                primeiros dígitos da ocupação
                '''
                if not contract.ocupacao_id:
                    raise osv.except_osv(
                        u'Falha na geração do arquivo.',
                        u'É necessário informar a ocupação no contrato %s.' % \
                            contract.name,
                        )
                r51.write_val(contract.ocupacao_id.code[:4], 5)
                # TODO: 168 182  Valor do Depósito - sem 13º Salário
                # TODO: 183 197  Valor do Depósito - sobre 13º Salário
                # TODO: 198 212  Valor do JAM
                # 213 359  Brancos
                r51.write_str('', 147)
                # 360 360  Final da Linha
                r51.write_str('*', 1)
                lines.append(r51)

            '''
            Registro 90 - Totalizador de arquivo
            '''
            r90 = line()
            # 1   2    Tipo de Registro
            r90.write_val(90, 2)
            # 3   53   Marca de Final de Registro
            r90.write_str('9' * 51, 51)
            # 54  359  Brancos
            r90.write_str('', 306)
            # 360 360  Final da Linha
            r90.write_str('*', 1)
            lines.append(r90)

            file_content = '\n'.join([l.content.upper() for l in lines])
            message = u'Arquivo gerado com sucesso'
            state = 'done'

            print file_content

            encoded_data = file_content.encode("utf-8").encode("base64")
            self.write(cr, uid, ids, {
                'file': encoded_data,
                #'state': state,
                'message': message,
                },
                context=context)

            return True

        self.write(cr, uid, ids, {
            'state': state,
            'message': message,
            })

        return False

sefip()
