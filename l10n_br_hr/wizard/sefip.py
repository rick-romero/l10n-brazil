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
        num = (pattern % data)[:size]
        self.content += num
        return num

    def write_val(self, data, size):
        if not data:
            data = 0
        else:
            try:
                data = int(data)
            except:
                data = int(re.sub('[^0-9]', '', str(data)))

        pattern = '%0{}d'.format(size)
        val = (pattern % data)[:size]
        self.content += val
        return val

    def write_str(self, data, size):
        if not data:
            data = ''

        stripped_data = data[:size]
        stripped_data_len = len(stripped_data)

        if stripped_data_len < size:
            stripped_data += ' ' * (size - stripped_data_len)

        self.content += stripped_data
        return stripped_data

    def write_date(self, date_str):
        if date_str:
            date = datetime.datetime.strptime(date_str, '%Y-%m-%d')
            date_str = date.strftime('%d%m%Y')

        self.write_str(date_str, 8)
        return date_str


class sefip(osv.TransientModel):
    _name = 'l10n_br_hr.sefip'
    _description = 'Generate SEFIP File'
    _columns = {
        'state': fields.selection([('init', 'init'),
                                   ('done', 'done'),
                                   ], 'state', readonly=True),
        'last_sync_date': fields.datetime('Last Sync Date'),
        'message': fields.text(u'Mensagem'),
        'file': fields.binary(u'Arquivo', readonly=True),
        'file_name': fields.char(u'Nome do Arquivo', 128, readonly=True),
        'company': fields.many2one('res.company', u'Empresa',
                                      required=True),
        'responsavel': fields.many2one('res.partner', u'Responsável'),
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
        'modalidade': fields.selection([
                ('0', u'Recolhimento ao FGTS e Declaração à Previdência'),
                ('1', u'Declaração ao FGTS e à Previdência'),
                ('9', u'Confirmação/Retificação de informações anteriores ' + \
                 u'- Recolhimento ao FGTS e Declaração à Previdência/' + \
                 u'Declaração ao FGTS e à Previdência.'),
            ], u'Modalidade do Arquivo'
            ),
        'indicador_de_recolhimento_fgts': fields.selection([
                ('1', u'GRF no prazo'),
                ('2', u'GRF em atraso'),
                ('3', u'GRF em atraso - Ação Fiscal'),
                ('5', u'Individualização'),
                ('6', u'Individualização - Ação Fiscal'),
            ], u'Indicador de Recolhimento de FGTS'
            ),
        'data_de_recolhimento_fgts': fields.date(
            u'Data de Recolhimento do FGTS'
            ),
        'indicador_de_recolhimento_previdencia': fields.selection([
                ('1', u'No prazo'),
                ('2', u'Em atraso'),
                ('3', u'Não gera GPS'),
            ], u'Indicador de Recolhimento da Previdência Social'
            ),
        'data_de_recolhimento_previdencia': fields.date(
            u'Data de Recolhimento da Previdência Social'
            ),
        'indice_de_recolhimento_em_atras_previdencia': fields.integer(
            u'Índice de Recolhimento em Atraso da Previdência Social',
            size=7
            ),
        'fornecedor_folha_tipo_de_inscricao': fields.selection([
                ('1', 'CNPJ'),
                ('3', 'CPF'),
            ],
            u'Tipo de Inscrição',
            required=True
            ),
        'fornecedor_folha_cnpj': fields.char(u'CNPJ', size=18),
        'fornecedor_folha_cpf': fields.char(u'CPF', size=15),
        'aliquota_rat': fields.float(
            u'Alíquota RAT', size=3, digits=(1, 1), required=True
            ),
        'codigo_de_centralizacao': fields.selection([
                ('0', u'Não Centraliza'),
                ('1', u'Centralizadora'),
                ('2', u'Centralizada'),
            ],
            u'Código de Centralização',
            # FIXME: Campo deve ser obrigatório, mas dá erro de integridade
            #required=True
            ),
        'codigo_de_outras_entidades': fields.integer(
            u'Código de Outras Entidades',
            size=4,
            help=u'Informar o código de outras entidades e fundos para as ' +\
                u'quais a empresa está obrigada a contribuir.',
            ),
        'codigo_de_pagamento_gps': fields.integer(
            u'Código de Pagamento da GPS',
            size=4,
            help=u'Informar o código de pagamento da GPS, conforme tabela ' +\
                u'divulgada pelo INSS.',
            ),
        'percentual_de_isencao_de_filantropia': fields.float(
            u'Percentual de Isenção de Filantropia',
            size=6,
            digits=(3, 2),
            ),
        'deducao_13_salario_licenca_maternidade': fields.float(
            u'Dedução 13º Salário Licença Maternidade',
            size=16,
            digits=(13, 2),
            ),
        'receita_evento_desportivo': fields.float(
            u'Receita Evento Desportivo/Patrocínio',
            size=16,
            digits=(13, 2),
            help=u'Informar o valor total da receita bruta de espetáculos ' + \
                u'desportivos em qualquer modalidade, realizado com ' + \
                u'qualquer associação desportiva que mantenha equipe de ' + \
                u'futebol profissional ou valor total pago a título de ' + \
                u'patrocínio, licenciamento de marcas e símbolos, ' + \
                u'publicidade, propaganda e transmissão de espetáculos ' + \
                u'celebrados com essas associações desportivas.'
            ),
        'indicativo_origem_da_receita': fields.selection([
                ('E', u'Receita referente a arrecadação de eventos'),
                ('P', u'Receita referente a patrocínio'),
                ('A',
                 u'Receita referente à arrecadação de eventos e patrocínio'),
            ],
            u'Indicativo de Origem da Receita',
            required=True,
            help=u'Indicar a origem da receita de evento desportivo/patrocínio'
            ),
        'compensacao_valor_corrigido': fields.float(
            u'Compensação - Valor Corrigido',
            size=16,
            digits=(13, 2),
            ),
        'compensacao_periodo_inicio': fields.char(
            u'Compensação - Período de Início',
            size=7,
            help=u'Mês e ano (MM/AAAA) de início das competências ' + \
                u'recolhidas indevidamente ou a maior.'
            ),
        'compensacao_periodo_fim': fields.char(
            u'Compensação - Período de Fim',
            size=7,
            help=u'Mês e ano (MM/AAAA) de final das competências ' + \
                u'recolhidas indevidamente ou a maior.'
            ),
        'competencias_anteriores_inss_folha': fields.float(
            u'Valor do INSS sobre Folha de Pagamento',
            size=16,
            digits=(13, 2),
            ),
        'competencias_anteriores_outras_entidades_folha': fields.float(
            u'Outras Entidades sobre Folha de Pagamento',
            size=16,
            digits=(13, 2),
            ),
        'competencias_anteriores_inss_producao': fields.float(
            u'Comercialização de Produção - Valor do INSS',
            size=16,
            digits=(13, 2),
            ),
        'competencias_anteriores_outras_entidades_producao': fields.float(
            u'Comercialização de Produção - Outras Entidades',
            size=16,
            digits=(13, 2),
            ),
        'competencias_anteriores_inss_evento': fields.float(
            u'Receita de Evento Desportivo/Patrocínio - Valor do INSS',
            size=16,
            digits=(13, 2),
            ),
        }
    _defaults = {
        'state': 'init',
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

    def _validate_cpf(self, cpf):
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

    def _constraint_fornecedor_folha_cnpj(self, cr, uid, ids):
        sefip_data = self.browse(cr, uid, ids[0])
        if not sefip_data.fornecedor_folha_cnpj or \
            sefip_data.fornecedor_folha_tipo_de_inscricao != '1':
            return True
        return self._validate_cnpj(sefip_data.fornecedor_folha_cnpj)

    def _constraint_responsavel_cpf(self, cr, uid, ids):
        sefip_data = self.browse(cr, uid, ids[0])
        if not sefip_data.responsavel_cpf or \
            sefip_data.responsavel_tipo_de_inscricao != '3':
            return True
        return self._validate_cpf(sefip_data.responsavel_cpf)

    def _constraint_fornecedor_folha_cpf(self, cr, uid, ids):
        sefip_data = self.browse(cr, uid, ids[0])
        if not sefip_data.fornecedor_folha_cpf or \
            sefip_data.fornecedor_folha_tipo_de_inscricao != '3':
            return True
        return self._validate_cpf(sefip_data.fornecedor_folha_cpf)

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
            elif sefip_data.fpas == '868' and date_number < 200003:
                message = u'Competência deve ser maior ou igual a 03/2000 para empregador doméstico.'

        if message:
            raise osv.except_osv(u'Competência inválida.', message)

        return True

    _constraints = [
        (_constraint_responsavel_cnpj, u'CNPJ do responsável é inválido.',
         ['responsavel_cnpj']),
        (_constraint_responsavel_cpf, u'CPF do responsável é inválido.',
         ['responsavel_cpf']),
        (_validate_cep, u'CEP do responsável é inválido.',
         ['responsavel_cep']),
        (_validate_telefone, u'Telefone do responsável é inválido.',
         ['responsavel_teleone']),
        (_validate_competencia, u'Competência é inválida.', ['competencia']),
        (_constraint_fornecedor_folha_cnpj,
         u'CNPJ do fornecedor da folha de pagamento é inválido.',
         ['fornecedor_folha_cnpj']),
        (_constraint_fornecedor_folha_cpf,
         u'CPF do fornecedor da folha de pagamento é inválido.',
         ['fornecedor_folha_cpf']),
        ]

    def _mask_cnpj(self, cnpj, field_name='cnpj'):
        if not cnpj:
            return {}
        val = re.sub('[^0-9]', '', cnpj)

        if len(val) >= 14:
            cnpj = "%s.%s.%s/%s-%s" % (val[0:2], val[2:5], val[5:8], val[8:12], val[12:14])

        return {'value': {field_name: cnpj}}

    def _mask_cpf(self, cpf, field_name):
        if not cpf:
            return {}
        val = re.sub('[^0-9]', '', cpf)

        if len(val) >= 11:
            cpf = "%s.%s.%s-%s" % (val[0:3], val[3:6], val[6:9], val[9:11])

        return {'value': {field_name: cpf}}

    def _mask_cep(self, cep, field_name):
        if not cep:
            return {}
        val = re.sub('[^0-9]', '', cep)

        if len(val) >= 8:
            cep = "%s-%s" % (val[0:5], val[5:8])

        return {'value': {field_name: cep}}

    def onchange_responsavel(self, cr, uid, ids, partner_id):
        partner_data = {}
        partner_obj = self.pool.get('res.partner')
        partner = partner_obj.browse(cr, uid, partner_id)
        if partner:
            tipo_de_inscricao = partner.tipo_pessoa == 'J' and '1' or '3'
            partner_data = {
                'responsavel_razao_social': partner.legal_name,
                'responsavel_tipo_de_inscricao': tipo_de_inscricao,
                }

            if partner.tipo_pessoa == 'J':
                partner_data['responsavel_cnpj'] = partner.cnpj_cpf
            else:
                partner_data['responsavel_cpf'] = partner.cnpj_cpf

            partner_data['responsavel_contato'] = partner.name
            partner_data['responsavel_email'] = partner.email
            partner_data['responsavel_telefone'] = partner.phone
            partner_data['responsavel_endereco'] = partner.street
            partner_data['responsavel_bairro'] = partner.district
            partner_data['responsavel_cep'] = partner.zip
            partner_data['responsavel_pais'] = partner.country_id.id
            partner_data['responsavel_cidade'] = partner.l10n_br_city_id.id

        return {'value': partner_data}

    def onchange_responsavel_cnpj(self, cr, uid, ids, cnpj):
        return self._mask_cnpj(cnpj, 'responsavel_cnpj')

    def onchange_fornecedor_folha_cnpj(self, cr, uid, ids, cnpj):
        return self._mask_cnpj(cnpj, 'fornecedor_folha_cnpj')

    def onchange_responsavel_cpf(self, cr, uid, ids, cpf):
        return self._mask_cpf(cpf, 'responsavel_cpf')

    def onchange_fornecedor_folha_cpf(self, cr, uid, ids, cpf):
        return self._mask_cpf(cpf, 'fornecedor_folha_cpf')

    def onchange_responsavel_cep(self, cr, uid, ids, cep):
        return self._mask_cep(cep, 'responsavel_cep')

    def _mask_mmyyyy(self, date):
        val = re.sub('[^0-9]', '', date)

        if len(val) in (1, 2):
            current_year = int(datetime.datetime.today().strftime('%Y'))
            val = '%02d%d' % (int(val), current_year)

        if len(val) >= 6:
            date = "%s/%s" % (val[0:2], val[2:6])

        return date

    def onchange_competencia(self, cr, uid, ids, competencia):
        if not competencia:
            return {}
        return {'value': {'competencia': self._mask_mmyyyy(competencia)}}

    def onchange_compensacao_periodo_inicio(self, cr, uid, ids, date):
        if not date:
            return {}
        return {'value': {
            'compensacao_periodo_inicio': self._mask_mmyyyy(date)
            }}

    def onchange_compensacao_periodo_fim(self, cr, uid, ids, date):
        if not date:
            return {}
        return {'value': {
            'compensacao_periodo_fim': self._mask_mmyyyy(date)
            }}

    def onchange_aliquota_rat(self, cr, uid, ids, aliquota_rat):
        
        if not aliquota_rat:
            return {}

        val = round(aliquota_rat, 1)
        val = re.sub('[^0-9]', '', str(val))

        if len(val) > 1:
            aliquota_rat = float(val[0] + '.' + val[1])
        elif len(val) == 1:
            aliquota_rat = float(val[0])

        return {'value': {'aliquota_rat': aliquota_rat}}

    def onchange_percentual_de_isencao_de_filantropia(self, cr, uid, ids, p):
        if not p:
            return {}

        val = round(p, 2)
        val = re.sub('[^0-9]', '', str(val))

        if len(val) > 4:
            p = float(val[0:3] + '.' + val[3:5])

        return {'value': {'percentual_de_isencao_de_filantropia': p}}

    def onchange_mask_float_15(self, cr, uid, ids, field, value):
        if not value:
            return {}

        val = round(value, 2)
        val = '%.2f' % val

        if len(val) > 14:
            val = re.sub('[^0-9]', '', val)
            value = float(val[0:13] + '.' + val[13:15])

        return {'value': {field: value}}

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
        if not data:
            return ''

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
        mes_competencia = scope_month

        month, year = sefip_data.competencia.split('/')
        valor_competencia = int(year + month)

        if scope_month == 13:
            scope_month = 12

        scope_date = datetime.datetime.strptime(
            '%04d-%02d-%02d' % (scope_year, scope_month, 1),
            '%Y-%m-%d'
            )

        lines = []

        r = self.browse(cr, uid, ids[0])
        company = r.company

        partner_obj = self.pool.get('res.partner')
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

        # FIXME: check if this is being used
        categories = [
            'SFAMILIA', 'SMATERNIDADE', '13SALAD', '13SALFI',
            ]
        tomadores = []
        active_contracts = 0

        for category in categories:
            grouped_payslips[category] = {'value': 0}

        for employee in employees:
            for contract in employee.contract_ids:
                # check if contract was active in the base year and month
                date_end = None

                date_start = datetime.datetime.strptime(
                    contract.date_start, '%Y-%m-%d'
                    )
                start_year = int(date_start.strftime('%Y'))
                start_month = int(date_start.strftime('%m'))

                if contract.data_de_desligamento:
                    date_end = datetime.datetime.strptime(
                        contract.data_de_desligamento, '%Y-%m-%d'
                        )
                elif contract.date_end:
                    date_end = datetime.datetime.strptime(
                        contract.date_end, '%Y-%m-%d'
                        )

                if not date_end:
                    if (start_year == scope_year and start_month >
                        scope_month) or start_year > scope_year:
                        del employees[index]
                        continue

                else:
                    end_year = int(date_end.strftime('%Y'))
                    end_month = int(date_end.strftime('%m'))

                    if (end_year == scope_year and end_month < scope_month) or\
                        end_year < scope_year:
                        del employees[index]
                        continue

                active_contracts += 1

                payslip_ids = payslip_obj.search(cr, uid, [
                        ('state', '=', 'done'),
                        ('contract_id', '=', contract.id),
                    ],
                    context=context
                    )
                payslips = payslip_obj.browse(
                    cr, uid, payslip_ids, context=context
                    )

                if contract.tomador:
                    tomadores.append(contract.tomador.id)

                for m in range(1, 13):
                    grouped_payslips[m] = {'value': 0}

                for category in categories:
                    grouped_payslips[category] = {'value': 0}

                for payslip in payslips:

                    date_from = datetime.datetime.strptime(
                        payslip.date_from, '%Y-%m-%d'
                        )
                    month = int(date_from.strftime('%m'))

                    if month != scope_month:
                        continue

                    # Get the gross payslip line
                    p_line_ids = payslip_line_obj.search(cr, uid, [
                        ('slip_id', '=', payslip.id),
                        ('code', '=', 'GROSS'),
                        ], context=context)

                    if p_line_ids:
                        p_line = payslip_line_obj.browse(
                            cr, uid, p_line_ids[0], context=context
                            )
                        grouped_payslips[month]['value'] += p_line.total

                    # Other payslip data
                    p_line_ids = payslip_line_obj.search(cr, uid, [
                        ('slip_id', '=', payslip.id),
                        ('code', 'in', categories),
                        ], context=context)

                    if p_line_ids:
                        p_lines = payslip_line_obj.browse(
                            cr, uid, p_line_ids, context=context
                            )
                        for l in p_lines:

                            if l.code == 'SFAMILIA' and \
                                contract.type_id.code not in ['01', '04', '07',
                                                              '12', '19', '20',
                                                              '21', '26']:
                                continue

                            data = payslip_line_obj.perm_read(
                                cr, uid, [l.id], context=context
                                )[0]

                            create_date = datetime.datetime.strptime(
                                data['create_date'], '%Y-%m-%d %H:%M:%S.%f'
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

        if active_contracts == 0:
            message = u'Não há contratos ativos na competência informada.'
            raise osv.except_osv(u'Não foi possível gerar o arquivo.', message)

        if not company.cnpj:
            message = u'A empresa deve possuir CNPJ cadastrado'
            state = 'init'
            raise osv.except_osv(_('Error'), message)

        else:
            # check if changes were made during the month scope
            changed_stuff = {}
            changed_employees = []
            address_changed_employees = []
            contract_changed_employees = []
            partner_changed_employees = []
            tables = ['hr_employee', 'hr_contract', 'res_partner',
                      'res_company']

            for table in tables:
                changed_stuff[table] = {}

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
                        changed_stuff[change.table][change.register_id\
                                                       ].append(change)
                    except:
                        changed_stuff[change.table][change.register_id] = []
                        changed_stuff[change.table][change.register_id\
                                                       ].append(change)

            for employee in employees:
                if employee.id in changed_stuff['hr_employee']:
                    changed_employees.append(employee)
                if employee.address_home_id.id in changed_stuff\
                    ['res_partner']:
                    address_changed_employees.append(employee)

                for contract in employee.contract_ids:
                    if contract.id in changed_stuff['hr_contract']:
                        contract_changed_employees.append(contract)

                if not employee.address_home_id:
                    raise osv.except_osv(
                        u'Não foi possível gerar o arquivo.',
                        u'Faltam dados no endereço do colaborador {}.'.format(
                            employee.name
                            ),
                        )
                if employee.address_home_id.id in changed_stuff\
                    ['res_partner']:
                    partner_changed_employees.append(employee)

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
            r00.write_num(valor_competencia, 6)
            # 298 300  Código de Recolhimento
            r00.write_num(sefip_data.recolhimento.code, 3)
            # 301 301  Indicador de Recolhimento FGTS
            if not sefip_data.indicador_de_recolhimento_fgts and \
                sefip_data.recolhimento.code in ['115', '130', '135', '145',
                                                 '150', '155', '307', '317',
                                                 '327', '337', '345', '608',
                                                 '640', '650', '660']:
                raise osv.except_osv(
                    u'Não foi possível gerar o arquivo.',
                    u'O indicador de recolhimento de FGTS é obrigatório ' + \
                    u'para o código de recolhimento selecionado.',
                    )
            elif sefip_data.indicador_de_recolhimento_fgts == '1' and \
                sefip_data.recolhimento.code in ['145', '307', '317', '327',
                                                 '337', '345', '640']:
                raise osv.except_osv(
                    u'Não foi possível gerar o arquivo.',
                    u'O código de recolhimento selecionado não aceita o ' + \
                    u'indicador de recolhimento do FGTS "GRF no prazo".',
                    )
            if sefip_data.recolhimento.code == '211' or mes_competencia == 13:
                r00.write_str('', 1)
            else:
                r00.write_num(sefip_data.indicador_de_recolhimento_fgts, 1)

            # 302 302  Modalidade do Arquivo
            modalidade = sefip_data.modalidade
            if modalidade == '0':
                modalidade = None

            if (scope_year < 1998 or (scope_year == 1998 and
                mes_competencia < 10)) and modalidade == '9':
                raise osv.except_osv(
                    u'Não foi possível gerar o arquivo.',
                    u'Modalidade deve ser recolhimento ou declaração para ' + \
                    u'a competência informada.',
                    )
            elif modalidade and sefip_data.recolhimento.code in ['145', '307',
                                                                 '317', '327',
                                                                 '337', '345',
                                                                 '640']:
                raise osv.except_osv(
                    u'Não foi possível gerar o arquivo.',
                    u'Para o código de recolhimento selecionado, a ' + \
                    u'modalidade deve ser recolhimento.',
                    )
            elif sefip_data.recolhimento.code == '211' and modalidade is None:
                raise osv.except_osv(
                    u'Não foi possível gerar o arquivo.',
                    u'Para o código de recolhimento selecionado, a ' + \
                    u'modalidade deve ser recolhimento ou confirmação/' + \
                    u'retificação.',
                    )
            elif sefip_data.fpas == 868 and modalidade == '1':
                raise osv.except_osv(
                    u'Não foi possível gerar o arquivo.',
                    u'Para o FPAS selecionado, a modalidade deve ser ' + \
                    u'recolhimento ou confirmação/retificação.',
                    )
            elif mes_competencia == 13 and modalidade is None:
                raise osv.except_osv(
                    u'Não foi possível gerar o arquivo.',
                    u'Para a competência 13, a modalidade deve ser ' + \
                    u'declaração ou confirmação/retificação.',
                    )

            r00.write_num(modalidade, 1)

            # 303 310  Data de Recolhimento do FGTS
            if sefip_data.data_de_recolhimento_fgts and \
                sefip_data.indicador_de_recolhimento_fgts == '1':
                raise osv.except_osv(
                    u'Não foi possível gerar o arquivo.',
                    u'Data de recolhimento do FGTS não deve ser informada ' + \
                    u'quando o indicador de recolhimento do FGTS for "GRF ' + \
                    u'no prazo".',
                    )
            r00.write_date(sefip_data.data_de_recolhimento_fgts)

            # 311 311  Indicador de Recolhimento da Previdência Social
            if sefip_data.indicador_de_recolhimento_previdencia != '3' and (
                scope_year < 1998 or (scope_year == 1998 and
                mes_competencia < 10)):
                raise osv.except_osv(
                    u'Não foi possível gerar o arquivo.',
                    u'Para a competência informada, o indicador de ' + \
                    u'recolhimento da Previdência Social deve ser "Não ' + \
                    u'gera GPS".',
                    )
            elif sefip_data.indicador_de_recolhimento_previdencia != '3' and (
                 sefip_data.recolhimento.code in ['145', '307', '317', '327',
                                                  '337', '345', '640', '660']
                ):
                raise osv.except_osv(
                    u'Não foi possível gerar o arquivo.',
                    u'Para o código de recolhimento selecionado, o ' + \
                    u'indicador de recolhimento da Previdência Social ' + \
                    u'deve ser "Não gera GPS".',
                    )
            r00.write_num(sefip_data.indicador_de_recolhimento_previdencia, 1)

            # 312 319  Data de Recolhimento da Previdência Social
            if sefip_data.data_de_recolhimento_previdencia:

                date = datetime.datetime.strptime(
                    sefip_data.data_de_recolhimento_previdencia, '%Y-%m-%d'
                    )
                tmp_date = scope_date + datetime.timedelta(months=1)
                tmp_month, tmp_year = map(
                    int, tmp_date.strftime('%m/%Y').split('/')
                    )

                if sefip_data.recolhimento.code == '650':

                    alw_date = datetime.datetime.strptime(
                        '%04d-%02d-%02d' % (tmp_year, tmp_month, 2), '%Y-%m-%d'
                        )
                    if date <= alw_date:
                        raise osv.except_osv(
                            u'Não foi possível gerar o arquivo.',
                            u'Para o código de recolhimento selecionado, a ' + \
                            u'data de recolhimento da Previdência Social deve ' + \
                            u'ser posterior ao dia 2 do mês seguinte ao da ' + \
                            u'competência.',
                            )
                    else:
                        r00.write_str(date.strftime('%d%m%Y'), 8)
    
                elif mes_competencia == 13:
                    alw_date = datetime.datetime.strptime(
                        '%04d-%02d-%02d' % (scope_year, 12, 20), '%Y-%m-%d'
                        )

                    if date <= alw_date:
                        raise osv.except_osv(
                            u'Não foi possível gerar o arquivo.',
                            u'Para a competência 13, data de recolhimento ' + \
                            u'da Previdência Social deve ser posterior a ' + \
                            u'20/12/%d.' % scope_year,
                            )
                    else:
                        r00.write_str(date.strftime('%d%m%Y'), 8)

                else:
                    r00.write_date(sefip_data.data_de_recolhimento_previdencia)
            else:
                r00.write_str('', 8)

            # 320 326  Índice de Recolhimento de atraso da Previdência Social
            r00.write_num(
                sefip_data.indice_de_recolhimento_em_atras_previdencia, 7
                )
            
            tipo_de_inscricao = sefip_data.responsavel_tipo_de_inscricao

            if tipo_de_inscricao == '1':
                cpf_cnpj = sefip_data.responsavel_cnpj
            else:
                cpf_cnpj = sefip_data.responsavel_cpf
            
            # 327 327  Tipo de Inscrição - Fornecedor Folha de Pagamento
            if sefip_data.fornecedor_folha_tipo_de_inscricao and (
                sefip_data.fornecedor_folha_cnpj or
                sefip_data.fornecedor_folha_cpf
                ):
                tipo_de_inscricao = sefip_data.fornecedor_folha_tipo_de_inscricao

            r00.write_num(tipo_de_inscricao, 1)

            # 328 341  Inscrição do Fornecedor Folha de Pagamento
            if sefip_data.fornecedor_folha_tipo_de_inscricao:
                if sefip_data.fornecedor_folha_tipo_de_inscricao == '1' and \
                    sefip_data.fornecedor_folha_cnpj:
                    cpf_cnpj = sefip_data.fornecedor_folha_cnpj
                elif sefip_data.fornecedor_folha_tipo_de_inscricao == '3' and \
                    sefip_data.fornecedor_folha_cpf:
                    cpf_cnpj = sefip_data.fornecedor_folha_cpf

            r00.write_num(cpf_cnpj, 14)

            # 342 359  Brancos
            r00.write_str('', 18)
            # 360 360  Final de Linha
            r00.write_str('*', 1)

            lines.append({'line': r00, 'order': '00'})

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
            company_partner = sefip_data.company.partner_id

            address = ''

            if company_partner.street:
                address += company_partner.street + ' '
            if company_partner.number:
                address += company_partner.number + ' '
            if company_partner.street2:
                address += company_partner.street2

            r10.write_str(self._clear_alfanum(address), 50)
            # 144 163  Bairro
            r10.write_str(company_partner.district, 20)
            # 164 171  CEP
            r10.write_str(company_partner.zip, 8)
            # 172 191  Cidade
            r10.write_str(
                self._clear_alfanum(company_partner.l10n_br_city_id.name), 20
                )
            # 192 193  Unidade da Federação
            if company_partner.state_id:
                r10.write_str(company_partner.state_id.country_id.code, 2)
            else:
                raise osv.except_osv(
                    u'Não foi possível gerar o arquivo.',
                    u'Faltam dados no endereço da empresa.',
                    )
            # 194 205  Telefone
            r10.write_str(company_partner.phone, 12)
            # 206 206  Indicador de Alteração de Endereço
            if company_partner.id in changed_stuff['res_partner']:
                r10.write_str('s', 1)
            else:
                r10.write_str('n', 1)

            # 207 213  CNAE
            r10.write_num(company.cnae_main_id.code, 7)

            # 214 214  Indicador de Alteração CNAE
            cnae_changed = 'n'
            if company.id in changed_stuff['res_company']:
                for change in changed_stuff['res_company'][company.id]:
                    if change.field == 'cnae_main_id':
                        cnae_changed = 's'
                        break
            r10.write_str(cnae_changed, 1)

            # 215 216  Alíquota RAT
            if sefip_data.company.simples in ['2', '3', '6'] or \
                sefip_data.recolhimento.code in ['604', '647', '825', '833',
                                                 '868']:
                r10.write_val(0, 2)
            elif valor_competencia < 199810 or (sefip_data.fpas == '639' and
                valor_competencia < 199904
                ) or (sefip_data.fpas == '604' and
                sefip_data.recolhimento.code == '150' and 
                valor_competencia < 200110) or \
                sefip_data.recolhimento.code in ['145', '307', '317', '327',
                                                 '337', '345', '640', '660']:
                r10.write_str('', 2)
            else:
                r10.write_num(sefip_data.aliquota_rat, 2)

            # 217 217  Código de Centralização
            # FIXME: não implementado
            r10.write_num(0, 1)
            # 218 218  SIMPLES
            r10.write_num(company.simples, 1)

            # 219 221  FPAS
            # FIXME: Trocar campo aberto por tabela de códigos
            r10.write_num(sefip_data.fpas, 3)

            # 222 225  Código de Outras Entidades
            if not sefip_data.codigo_de_outras_entidades and \
                sefip_data.recolhimento.code in ['115', '130', '135', '150',
                                                 '155', '211', '608', '650']:
                raise osv.except_osv(
                    u'Não foi possível gerar o arquivo.',
                    u'Campo "Código de Outras Entidades" é obrigatório ' + \
                    u'para o recolhimento selecionado.',
                    )
            elif sefip_data.recolhimento.code in ['145', '307', '317', '327',
                                                  '337', '345', '640', '660']:
                r10.write_str('', 4)
            elif valor_competencia < 199810 or company.simples in ['2', '3',
                                                                   '6']:
                r10.write_str('', 4)
            elif sefip_data.fpas == '639' and valor_competencia < 199904:
                r10.write_str('', 4)
            elif sefip_data.fpas == '582' and valor_competencia >= 199810:
                r10.write_val(0, 4)
            elif sefip_data.fpas == '868':
                r10.write_val(0, 4)
            else:
                r10.write_num(sefip_data.codigo_de_outras_entidades, 4)

            # 226 229  Código de Pagamento GPS
            if not sefip_data.codigo_de_pagamento_gps and (scope_year > 1998 or
                (scope_year == 1998 and mes_competencia >= 10)):
                raise osv.except_osv(
                    u'Não foi possível gerar o arquivo.',
                    u'Campo "Código de Pagamento GPS" é obrigatório para ' + \
                    u'competência maior ou igual a 10/1998.',
                    )
            elif sefip_data.recolhimento.code in ['115', '150', '211', '650']:
                r10.write_num(sefip_data.codigo_de_pagamento_gps, 4)
            elif sefip_data.fpas == '868' and \
                sefip_data.codigo_de_pagamento_gps in [1600, 1651]:
                r10.write_num(sefip_data.codigo_de_pagamento_gps, 4)
            else:
                r10.write_str('', 4)

            # 230 234  Percentual de Isenção de Filantropia
            if sefip_data.fpas == '639':
                r10.write_num('{:06.02f}'.format(
                    sefip_data.percentual_de_isencao_de_filantropia
                    ), 5)
            else:
                r10.write_str('', 5)

            # 235 249  Salário-Família
            if mes_competencia == 13 or valor_competencia < 199810 or \
                sefip_data.fpas == '868' or \
                sefip_data.recolhimento.code in ['145', '307', '327', '345',
                                                 '640', '650', '660', '868']:
                sfamilia = 0
            else:
                sfamilia = grouped_payslips['SFAMILIA']['value']

            r10.write_val(sfamilia, 15)
            # 250 264  Salário-Maternidade
            if mes_competencia == 13 or valor_competencia < 199810 or \
                valor_competencia >= 200006 and valor_competencia <= 200308 or\
                sefip_data.fpas == '868' or \
                sefip_data.recolhimento.code in ['130', '135', '145', '211',
                                                 '307', '317', '327', '337',
                                                 '345', '640', '650', '660']:
                smaternidade = 0
            else:
                smaternidade = grouped_payslips['SMATERNIDADE']['value']

            r10.write_val(smaternidade, 15)

            # 265 279  Contrib. Desc. Empregado Referente à Competência 13
            r10.write_val(0, 15)
            # 280 280  Indicador de valor negativo ou positivo
            r10.write_val(0, 1)
            # 281 294  Valor Devido à Previdência Social Referente à Comp. 13
            r10.write_val(0, 14)


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
            lines.append({
                'line': r10,
                # Tipo do registro (10), tipo de inscrição (1) e CNPJ
                'order': '101{}'.format(sefip_data.company.cnpj),
                })

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

            # 54  68   Dedução 13º Salário Licença Maternidade
            if sefip_data.fpas == '868' or sefip_data.recolhimento.code in \
                ['130', '135', '145', '211', '307', '317', '327', '337',
                 '345', '640', '650', '660']:
                r12.write_val(0, 15)
            elif valor_competencia < 199810 or (valor_competencia > 200101 and
                                                valor_competencia < 200308):
                r12.write_val(0, 15)
            else:
                r12.write_val(
                    sefip_data.deducao_13_salario_licenca_maternidade, 15
                    )

            # 69  83   Receita Evento Desportivo/Patrocínio
            if mes_competencia == 13 or sefip_data.fpas == '868' or \
                sefip_data.recolhimento.code in ['130', '135', '145', '211',
                                                 '307', '317', '327', '337',
                                                 '345', '608', '640', '650',
                                                 '660']:
                r12.write_val(0, 15)
            else:
                r12.write_val(sefip_data.receita_evento_desportivo, 15)
            # 84  84   Indicativo Origem da Receita
            if mes_competencia == 13:
                r12.write_str('', 1)
            else:
                r12.write_str(sefip_data.indicativo_origem_da_receita, 1)
            # 85  99   Comercialização da Produção - Pessoa Física
            # FIXME: Não implementado
            r12.write_val(0, 15)
            # 100 114  Comercialização da Produção - Pessoa Jurídica
            # FIXME: Não implementado
            r12.write_val(0, 15)
            
            # FIXME: Recolhimentos 650, 660 não suportados
            # 115 125  Outras Informações Processo
            r12.write_str('', 11)
            # 126 129  Outras Informações Processo - Ano
            r12.write_str('', 4)
            # 130 134  Outras Informações Vara/JCJ
            r12.write_str('', 5)
            # 135 140  Outras Informações Período Início
            r12.write_str('', 6)
            # 141 146  Outras Informações Período Fim
            r12.write_str('', 6)

            if sefip_data.indicador_de_recolhimento_previdencia != '1' or \
                valor_competencia < 199810 or \
                sefip_data.compensacao_valor_corrigido == 0 or \
                sefip_data.recolhimento.code in ['145', '211', '307', '327',
                                                 '345', '640', '660']:
                r12.write_val(0, 15)
                r12.write_str('', 12)
            else:
                # 147 161  Compensação - Valor Corrigido
                r12.write_val(sefip_data.compensacao_valor_corrigido, 15)

                periodo_inicio = None
                if sefip_data.compensacao_periodo_inicio:
                    m, y = sefip_data.compensacao_periodo_inicio.split('/')
                    periodo_inicio = int('{}{}'.format(y, m))

                periodo_fim = None
                if sefip_data.compensacao_periodo_fim:
                    m, y = sefip_data.compensacao_periodo_fim.split('/')
                    periodo_fim = int('{}{}'.format(y, m))

                if periodo_inicio > valor_competencia:
                    raise osv.except_osv(
                        u'Não foi possível gerar o arquivo.',
                        u'Campo "Compensação - Período de Início" deve ser  ' + \
                        u'menor ou igual a 10/1998.',
                        )

                if periodo_inicio > valor_competencia:
                    raise osv.except_osv(
                        u'Não foi possível gerar o arquivo.',
                        u'Campo "Compensação - Período de Início" deve ser  ' + \
                        u'menor ou igual a 10/1998.',
                        )

                # 162 167  Compensação - Período Início
                r12.write_num(periodo_inicio, 6)
                # 168 173  Compensação - Período Fim
                r12.write_num(periodo_fim, 6)

            if sefip_data.indicador_de_recolhimento_previdencia not in ['1',
                '2'] or valor_competencia < 199810 or \
                sefip_data.recolhimento.code in ['145', '307', '327', '345',
                                                 '640', '660']:
                r12.write_val(0, 30)
            else:
                # 174 188  Recolhimento de Competências Anteriores - Valor do INSS sobre Folha de Pagamento
                r12.write_val(sefip_data.competencias_anteriores_inss_folha, 15)
                # 189 203  Recolhimento de Competências Anteriores - Outras Entidades sobre Folha de Pagamento
                r12.write_val(
                    sefip_data.competencias_anteriores_outras_entidades_folha, 15
                    )

            if sefip_data.indicador_de_recolhimento_previdencia not in ['1',
                '2'] or sefip_data.fpas == '868' or mes_competencia == 13 or \
                valor_competencia < 199810 or \
                sefip_data.recolhimento.code in ['130', '135', '145', '211',
                                                 '307', '317', '327', '337',
                                                 '345', '608', '640', '650',
                                                 '660']:
                r12.write_val(0, 45)
            else:
                # 204 218  Recolhimento de Competências Anteriores - Comercialização de Produção - Valor do INSS
                r12.write_val(
                    sefip_data.competencias_anteriores_inss_producao, 15
                    )
                # 219 233  Recolhimento de Competências Anteriores - Comercialização de Produção - Outras Entidades
                r12.write_val(
                    sefip_data.competencias_anteriores_outras_entidades_producao,
                    15
                    )
                # 234 248  Recolhimento de Competências Anteriores - Receita de Evento Desportivo/Patrocínio - Valor do INSS
                r12.write_val(
                    sefip_data.competencias_anteriores_inss_evento, 15
                    )

            # FIXME: Para implementação futura
            # 249 263  Parcelamento do FGTS - Somatório Remunerações das Categorias 1, 2, 3, 5 e 6
            r12.write_val(0, 15)
            # 264 278  Parcelamento do FGTS - Somatório Remunerações das Categorias 4 e 7
            r12.write_val(0, 15)
            # 279 293  Parcelamento do FGTS - Valor Recolhido
            r12.write_val(0, 15)

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
            lines.append({
                'line': r12,
                # Tipo do registro (10), tipo de inscrição (1) e CNPJ
                'order': '121{}'.format(sefip_data.company.cnpj),
            })

            '''
            Registro 13 - Alteração cadastral do trabalhador
            '''

            # hr_employee
            if changed_employees:
                for employee in changed_employees:
                    for change in changed_stuff['hr_employee'][employee.id]:

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
                        cnpj = r13.write_num(sefip_data.company.cnpj, 14)
                        # 18  53   Zeros
                        r13.write_val(0, 36)
                        # 54  64   PIS/PASEP
                        pis_pasep = r13.write_num(employee.pis_pasep, 11)

                        # 65  72   Data de Admissão
                        if contract.date_start:
                            date_start = datetime.datetime.strptime(
                                contract.date_start, '%Y-%m-%d'
                                )
                            d = r13.write_str(date_start.strftime('%d%m%Y'), 8)
                        else:
                            d = r13.write_val(0, 8)

                        # 73  74   Categoria Trabalhador
                        if not contract.type_id.code:
                            contract_type = '01'
                        else:
                            contract_type = contract.type_id.code

                        r13.write_val(contract_type, 2)

                        # 75  85   Matrícula do Trabalhador
                        if contract_type == '06' or not employee.matricula:
                            r13.write_str('', 11)
                        else:
                            r13.write_val(employee.matricula, 11)
                        # 86  92   Número CTPS
                        r13.write_num(employee.carteira_de_trabalho_numero, 7)
                        # 93  97   Série CTPS
                        r13.write_num(employee.carteira_de_trabalho_serie, 5)
                        # 98  167  Nome Trabalhador
                        r13.write_str(self._clear_alfanum(employee.name), 70)
                        # 168 181  Código Empresa CAIXA
                        r13.write_num(company.codigo_caixa, 14)
                        # 182 192  Código Trabalhador CAIXA
                        r13.write_num(employee.codigo_caixa, 11)

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

                        order = '131' + str(cnpj) + str(pis_pasep) + str(d) + \
                            contract_type

                        lines.append({'line': r13, 'order': order})

            # hr_contract
            if contract_changed_employees:
                for contract in contract_changed_employees:
                    for change in changed_stuff['hr_contract'][contract.id]:

                        r13 = line()
                        # 1   2    Tipo de Registro
                        r13.write_val(13, 2)
                        # 3   3    Tipo de Inscrição - Fixo: 1 - CNPJ
                        r13.write_val(1, 1)
                        # 4   17   Inscrição da Empresa
                        cnpj = r13.write_num(sefip_data.company.cnpj, 14)
                        # 18  53   Zeros
                        r13.write_val(0, 36)
                        # 54  64   PIS/PASEP
                        pis_pasep = r13.write_num(employee.pis_pasep, 11)

                        # 65  72   Data de Admissão
                        if contract.date_start:
                            date_start = datetime.datetime.strptime(
                                contract.date_start, '%Y-%m-%d'
                                )
                            d = r13.write_str(date_start.strftime('%d%m%Y'), 8)
                        else:
                            d = r13.write_val(0, 8)

                        # 73  74   Categoria Trabalhador
                        if not contract.type_id.code:
                            contract_type = '01'
                        else:
                            contract_type = contract.type_id.code

                        r13.write_val(contract_type, 2)

                        # 75  85   Matrícula do Trabalhador
                        if contract_type == '06' or not employee.matricula:
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
                        # 168 181  Código Empresa CAIXA
                        r13.write_num(company.codigo_caixa, 14)
                        # 182 192  Código Trabalhador CAIXA
                        r13.write_num(employee.codigo_caixa, 11)

                        # 193 195  Código Alteração Cadastral
                        change_code = None
                        new_value = change.new_value

                        if change.field == 'date_start':
                            change_code = 408
                        elif change.field == 'ocupacao_id':
                            if not contract.ocupacao_id:
                                raise osv.except_osv(
                                    u'Não foi possível gerar o arquivo.',
                                    u'É necessário informar a ocupação no ' + \
                                        u'contrato %s.' % contract.name,
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

                        order = '131' + str(cnpj) + str(pis_pasep) + str(d) + \
                            contract_type

                        lines.append({'line': r13, 'order': order})

            # res_partner
            if partner_changed_employees:
                for employee in partner_changed_employees:
                    for change in changed_stuff['res_partner'][employee.id]:
                        
                        if change.field != 'birthday':
                            continue

                        r13 = line()
                        # 1   2    Tipo de Registro
                        r13.write_val(13, 2)
                        # 3   3    Tipo de Inscrição - Fixo: 1 - CNPJ
                        r13.write_val(1, 1)
                        # 4   17   Inscrição da Empresa
                        cnpj = r13.write_num(sefip_data.company.cnpj, 14)
                        # 18  53   Zeros
                        r13.write_val(0, 36)
                        # 54  64   PIS/PASEP
                        pis_pasep = r13.write_num(employee.pis_pasep, 11)

                        # 65  72   Data de Admissão
                        if contract.date_start:
                            date_start = datetime.datetime.strptime(
                                contract.date_start, '%Y-%m-%d'
                                )
                            d = r13.write_str(date_start.strftime('%d%m%Y'), 8)
                        else:
                            d = r13.write_val(0, 8)

                        # 73  74   Categoria Trabalhador
                        if not contract.type_id.code:
                            contract_type = '01'
                        else:
                            contract_type = contract.type_id.code

                        r13.write_val(contract_type, 2)

                        # 75  85   Matrícula do Trabalhador
                        if contract_type == '06' or not employee.matricula:
                            r13.write_str('', 11)
                        else:
                            r13.write_val(employee.matricula, 11)
                        # 86  92   Número CTPS
                        r13.write_num(employee.carteira_de_trabalho_numero, 7)
                        # 93  97   Série CTPS
                        r13.write_num(employee.carteira_de_trabalho_serie, 5)
                        # 98  167  Nome Trabalhador
                        r13.write_str(self._clear_alfanum(employee.name), 70)
                        # 168 181  Código Empresa CAIXA
                        r13.write_num(company.codigo_caixa, 14)
                        # 182 192  Código Trabalhador CAIXA
                        r13.write_num(employee.codigo_caixa, 11)

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

                        order = '131' + str(cnpj) + str(pis_pasep) + str(d) + \
                            contract_type

                        lines.append({'line': r13, 'order': order})

            '''
            Registro 14 - Inclusão/alteração do endereço do trabalhador
            '''
            # res_partner
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
                    cnpj = r14.write_num(sefip_data.company.cnpj, 14)
                    # 18  53   Zeros
                    r14.write_val(0, 36)
                    # 54  64   PIS/PASEP/CI
                    pis_pasep = r14.write_val(employee.pis_pasep, 11)
                    # 65  72   Data Admissão
                    if contract.date_start:
                        date_start = datetime.datetime.strptime(
                            contract.date_start, '%Y-%m-%d'
                            )
                        d = r14.write_str(date_start.strftime('%d%m%Y'), 8)
                    else:
                        d = r14.write_val(0, 8)
                    # 73  74   Categoria Trabalhador
                    if not contract.type_id.code:
                        contract_type = '01'
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
                    address = ''

                    if employee.address_home_id.street:
                        address += employee.address_home_id.street + ' '
                    if employee.address_home_id.number:
                        address += employee.address_home_id.number + ' '
                    if employee.address_home_id.street2:
                        address += employee.address_home_id.street2

                    r14.write_str(self._clear_alfanum(address), 50)
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
                            u'Não foi possível gerar o arquivo.',
                            u'Faltam dados no endereço do colaborador.',
                            )

                    # 257 359  Brancos
                    r14.write_str('', 103)
                    # 360 360  Final da Linha
                    r14.write_str('*', 1)

                    order = '141' + str(cnpj) + str(pis_pasep) + str(d) + \
                            contract_type

                    lines.append({'line': r14, 'order': order})

            invoice_ids = invoice_obj.search(cr, uid, [
                    ('fiscal_type', '=', 'service'),
                    ('company_id', '=', company.id),
                    ('partner_id', 'in', tomadores),
                ], context=context
                )
            invoices = invoice_obj.browse(cr, uid, invoice_ids, context=context)

            invoice_partners = {}

            for invoice in invoices:
                if not invoice.contracts:
                    continue

                try:
                    invoice_partners[invoice.partner_id] += invoice.amount_total
                except:
                    invoice_partners[invoice.partner_id] = invoice.amount_total

            for partner in invoice_partners:
                address = partner.address[0]

                '''
                Registro 20 - Registro do tomador de serviço/obra
                '''
                r20 = line()
                # 1   2    Tipo de Registro
                r20.write_val(20, 2)
                # 3   3    Tipo de Inscrição - Fixo: 1 - CNPJ
                r20.write_val(1, 1)
                # 4   17   Inscrição da Empresa
                cnpj = r20.write_num(sefip_data.company.cnpj, 14)
                # 18  18   Tipo de Inscrição-Tomador/Obra Const. Civil
                # Fixo: 1 - CNPJ
                r20.write_num(1, 1)
                # 19  32   Inscrição Tomador/Obra Const. Civil
                partner_cnpj = r20.write_num(partner.cnpj_cpf, 14)
                # 33  53   Zeros
                r20.write_val(0, 21)
                # 54  93   Nome do Tomador/Obra de Const. Civil
                r20.write_str(self._clear_alfanum(partner.name), 40)
                # 94  143  Logradouro, rua, nº, apto
                street = ''

                if company_partner.street:
                    street += company_partner.street + ' '
                if company_partner.number:
                    street += company_partner.number + ' '
                if company_partner.street2:
                    street += company_partner.street2

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
                        u'Não foi possível gerar o arquivo.',
                        u'Faltam dados no endereço do colaborador %s.' % \
                            partner.name,
                        )
                # 194 197  Código de Pagamento GPS
                if partner.codigo_pagamento_gps:
                    r20.write_num(partner.codigo_pagamento_gps, 4)
                else:
                    r20.write_str('', 4)
                # 198 212  Salário Família
                if mes_competencia == 13 or valor_competencia < 199810 or \
                    sefip_data.fpas == '868' or \
                    sefip_data.recolhimento.code not in ['150', '155', '608']:
                    sfamilia = 0
                else:
                    sfamilia = grouped_payslips['SFAMILIA']['value']
                r20.write_val(sfamilia, 15)
                # 213 227  Contrib. Desc. Empregado Referente à Competência 13
                r20.write_val(0, 15)
                # 228 228  Indicador de Valor Negativo ou Positivo
                r20.write_val(0, 1)
                # 229 242  Valor Devido à Previdência Social Referente à Competência 13
                r20.write_val(0, 14)
                # 243 257  Valor de Retenção
                # FIXME: Não implementado
                r20.write_val(0, 15)
                # 258 272  Valor das Faturas Emitidas para o Tomador
                r20.write_val(invoice_partners[partner], 15)
                # 273 317  Zeros
                r20.write_val(0, 45)
                # 318 359  Brancos
                r20.write_str('', 42)
                # 360 360  Final da Linha
                r20.write_str('*', 1)

                order = '201' + str(cnpj) + '1' + str(partner_cnpj)

                lines.append({'line': r20, 'order': order})

                '''
                Registro 21 - Informações adicionais do tomador de serviço/obra
                '''
                r21 = line()
                # 1   2    Tipo de Registro
                r21.write_val(21, 2)
                # 3   3    Tipo de Inscrição - Fixo: 1 - CNPJ
                r21.write_val(1, 1)
                # 4   17   Inscrição da Empresa
                cnpj = r21.write_num(sefip_data.company.cnpj, 14)
                # 18  18   Tipo de Inscrição-Trabalhador/Obra Const. Civil
                # Fixo: 1 - CNPJ
                r21.write_val(1, 1)
                # 19  32   Inscrição Tomador/Obra Const. Civil
                partner_cnpj = r21.write_num(partner.cnpj_cpf, 14)
                # 33  53   Zeros
                r21.write_val(0, 21)
                
                
                if sefip_data.indicador_de_recolhimento_previdencia != '1' or \
                    valor_competencia < 199810 or mes_competencia == 13 or \
                    sefip_data.recolhimento.code in ['317', '337']:
                    r21.write_val(0, 15)
                    r21.write_str('', 12)
                else:
                    # 54  68   Compensação - Valor Corrigido
                    r21.write_val(sefip_data.compensacao_valor_corrigido, 15)

                    periodo_inicio = None
                    if sefip_data.compensacao_periodo_inicio:
                        m, y = sefip_data.compensacao_periodo_inicio.split('/')
                        periodo_inicio = int('{}{}'.format(y, m))

                    periodo_fim = None
                    if sefip_data.compensacao_periodo_fim:
                        m, y = sefip_data.compensacao_periodo_fim.split('/')
                        periodo_fim = int('{}{}'.format(y, m))

                    # 69  74   Compensação - Período Início
                    r21.write_num(periodo_inicio, 6)
                    # 75  80   Compensação - Período Fim
                    r21.write_num(periodo_fim, 6)

                if sefip_data.recolhimento.code in ['211', '317', '337'] or \
                    sefip_data.indicador_de_recolhimento_previdencia not in \
                    ['1', '2']:
                    r21.write_val(0, 30)
                else:
                    # 81  95   Recolhimento de Competências Anteriores - Valor do INSS sobre Folha de Pagamento
                    r21.write_val(
                        sefip_data.competencias_anteriores_inss_folha, 15
                        )
                    # 96  110  Recolhimento de Competências Anteriores - Outras Entidades sobre Folha de Pagamento
                    r21.write_val(
                        sefip_data.competencias_anteriores_outras_entidades_folha,
                        15
                        )

                # FIXME: Para implementação futura
                # 111 125  Parcelamento do FGTS - somatório das remunerações das categorias 1, 2, 3, 5 e 6
                # 126 140  Parcelamento do FGTS - somatório das remunerações das categorias 4 e 7
                # 141 155  Parcelamento do FGTS - valor recolhido
                r21.write_val(0, 45)

                # 156 359  Brancos
                r21.write_str('', 204)
                # 360 360  Final da Linha
                r21.write_str('*', 1)

                order = '211' + str(cnpj) + '1' + str(partner_cnpj)

                lines.append({'line': r21, 'order': '21'})

            for employee in employees:

                contract = employee_obj.get_active_contract(
                    cr, uid, employee.id, date=scope_date, context=context
                    )

                if not contract:
                    continue

                base_calculo_previdencia = 0
                contract_payslips = {}
                categories = [
                    'GROSS', 'SFAMILIA', 'SMATERNIDADE', '13SALAD', '13SALFI',
                    'CPREV', 'RECL', 'DISSIDIO', 'RECLAMATORIA',
                    'CPREVMATERNIDADE',
                    ]

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
                    contract_payslips[category] = {'value': 0}

                for payslip in payslips:

                    date_from = datetime.datetime.strptime(
                        payslip.date_from, '%Y-%m-%d'
                        )
                    month = int(date_from.strftime('%m'))

                    if month != scope_month:
                        continue

                    base_calculo_previdencia = payslip.base_calculo_previdencia

                    p_line_ids = payslip_line_obj.search(cr, uid, [
                        ('slip_id', '=', payslip.id),
                        ('code', 'in', categories),
                        ], context=context)

                    if p_line_ids:
                        p_lines = payslip_line_obj.browse(
                            cr, uid, p_line_ids, context=context
                            )

                        for l in p_lines:
                            data = payslip_line_obj.perm_read(
                                cr, uid, [l.id], context=context
                                )[0]

                            create_date = datetime.datetime.strptime(
                                data['create_date'], '%Y-%m-%d %H:%M:%S.%f'
                                )

                            try:
                                contract_payslips[l.code][
                                    'value'] += l.total
                                contract_payslips[l.code][
                                    'create_date'] = create_date
                            except:
                                contract_payslips[l.code] = {
                                    'value': l.total,
                                    'create_date': create_date,
                                    }

                '''
                Registro 30 - Registro do trabalhador
                '''
                r30 = line()
                # 1   2    Tipo de Registro
                r30.write_val(30, 2)
                # 3   3    Tipo de Inscrição - Fixo: 1 - CNPJ
                r30.write_val(1, 1)
                # 4   17   Inscrição da Empresa
                cnpj = r30.write_num(sefip_data.company.cnpj, 14)
                # 18  18   Tipo de Inscrição-Tomador/Obra Const. Civil
                # Fixo: 1 - CNPJ
                r30.write_val(1, 1)
                # 19  32   Inscrição Tomador/Obra Const. Civil
                r30.write_num(sefip_data.company.cnpj, 14)

                # 33  43   PIS/PASEP/CI
                pis_pasep = r30.write_num(employee.pis_pasep, 11)
                # 44  51   Data de Admissão
                if contract.date_start:
                    date_start = datetime.datetime.strptime(
                        contract.date_start, '%Y-%m-%d'
                        )
                    d = r30.write_str(date_start.strftime('%d%m%Y'), 8)
                else:
                    d = r30.write_val(0, 8)
                # 52  53   Categoria Trabalhador
                if not contract.type_id.code:
                    contract_type = '01'
                else:
                    contract_type = contract.type_id.code

                r30.write_val(contract_type, 2)

                # 54  123  Nome Trabalhador
                r30.write_str(self._clear_alfanum(employee.name), 70)
                # 124 134  Matrícula do Empregado
                if contract_type == '06' or not employee.matricula:
                    r30.write_str('', 11)
                else:
                    r30.write_val(employee.matricula, 11)
                # 135 141  Número CTPS
                r30.write_num(employee.carteira_de_trabalho_numero, 7)
                # 142 146  Série CTPS
                r30.write_num(employee.carteira_de_trabalho_serie, 5)
                # 147 154  Data de Opção
                date_start = datetime.datetime.strptime(
                    contract.date_start, '%Y-%m-%d'
                    )
                date_limit = datetime.datetime.strptime(
                    '1988-10-05', '%Y-%m-%d'
                    )
                if date_start < date_limit and contract.optante_fgts \
                    and contract.data_de_opcao:
                    r30.write_date(contract.data_de_opcao)
                else:
                    r30.write_str('', 8)
                # 155 162  Data de Nascimento
                r30.write_date(employee.address_home_id.birthday)
                # 163 167  CBO - Código Brasileiro de Ocupação
                '''
                SEFIP pede o código da família, que é composto pelos 4
                primeiros dígitos da ocupação
                '''
                if not contract.ocupacao_id:
                    raise osv.except_osv(
                        u'Não foi possível gerar o arquivo.',
                        u'É necessário informar a ocupação no contrato %s.' % \
                            contract.name,
                        )
                r30.write_val(contract.ocupacao_id.code[:4], 5)
                # 168 182  Remuneração sem 13º
                gross = contract_payslips['GROSS']['value']
                r30.write_val(re.sub('[^0-9]', '', '%.02f' % gross), 15)
                # 183 197  Remuneração 13º
                sal13 = contract_payslips['13SALAD']['value'] + \
                    contract_payslips['13SALFI']['value']
                r30.write_val(re.sub('[^0-9]', '', '%.02f' % sal13), 15)
                # 198 199  Classe de Contribuição
                # FIXME: Não implementado (Campo relativo à construção civil)
                r30.write_str('', 2)
                # 200 201  Ocorrência
                r30.write_str(contract.ocorrencia.code, 2)

                # 202 216  Valor Descontado do Segurado
                valor = 0

                # Múltiplos vínculos ou trabalhador avulso
                if (contract.ocorrencia and contract.ocorrencia.code in ['05',
                    '06', '07', '08']) or contract.type_id.code == '01' or \
                    contract_payslips['DISSIDIO']['value'] or \
                    contract_payslips['RECLAMATORIA']['value']:

                    valor = contract_payslips['CPREV']['value']

                elif contract_payslips['CPREVMATERNIDADE']['value']:
                    valor = contract_payslips['CPREVMATERNIDADE']['value']

                r30.write_val(valor, 15)

                # 217 231  Remuneração Base de Cálculo da Contribuição Previdenciária
                r30.write_val(base_calculo_previdencia, 15)

                '''
                TODO: 232 246  Base de Cálculo 13º Salário Previdência Social -
                Referente a Competência do Movimento
                '''
                base_calculo = 0
                if contract_type in (01, 02, 04 ,06 , 07, 12, 19, 20, 21, 26):
                    pass

                r30.write_val(base_calculo, 15)

                # 247 261  Base de Cálculo 13º Salário Previdência Social - Referente a GPS da Competência 13
                # FIXME: Não suportado
                r30.write_val(0, 15)

                # 262 359  Brancos
                r30.write_str('', 98)
                # 360 360  Final da Linha
                r30.write_str('*', 1)

                order = '301' + str(cnpj) + '1' + str(cnpj) + str(pis_pasep) +\
                    str(d) + contract_type

                lines.append({'line': r30, 'order': order})

                '''
                Registro 32 - Registro de movimentação do trabalhador
                '''
                r32 = line()
                # 1   2    Tipo de Registro
                r32.write_val(32, 2)
                # 3   3    Tipo de Inscrição - Fixo: 1 - CNPJ
                r32.write_val(1, 1)
                # 4   17   Inscrição da Empresa
                cnpj = r32.write_num(sefip_data.company.cnpj, 14)
                # 18  18   Tipo de Inscrição-Trabalhador/Obra Const. Civil
                # Fixo: 1 - CNPJ
                r32.write_val(1, 1)
                # 19  32   Inscrição Tomador/Obra Const. Civil
                r32.write_num(sefip_data.company.cnpj, 14)
                # 33  43   PIS/PASEP/CI
                pis_pasep = r32.write_num(employee.pis_pasep, 11)
                # 44  51   Data de Admissão
                if contract.date_start:
                    date_start = datetime.datetime.strptime(
                        contract.date_start, '%Y-%m-%d'
                        )
                    d = r32.write_str(date_start.strftime('%d%m%Y'), 8)
                else:
                    d = r32.write_val(0, 8)

                # 52  53   Categoria Trabalhador
                if not contract.type_id.code:
                    contract_type = '01'
                else:
                    contract_type = contract.type_id.code

                r32.write_val(contract_type, 2)

                # 54  123  Nome Trabalhador
                r32.write_str(self._clear_alfanum(employee.name), 70)

                if contract.movimentacao:
                    # 124 125  Código da Movimentação
                    r32.write_str(contract.movimentacao.code, 2)
                    # 126 133  Data de Movimentação
                    r32.write_date(contract.data_de_movimentacao)
                else:
                    r32.write_str('', 10)

                # TODO: 134 134  Indicativo de Recolhimento do FGTS
                # possible values: 'S', 'N', 'C', ' '
                indicativo_recolhimento = ' '

                # Required
                if contract.movimentacao.code in ('I1', 'I2', 'I3', 'I4', 'L'):
                    pass
                # Not required
                    pass

                if indicativo_recolhimento in ('S', 'N') and \
                    valor_competencia <= 199801:
                    indicativo_recolhimento = ' '
                elif indicativo_recolhimento == 'C' and \
                    valor_competencia < 199810:
                    indicativo_recolhimento = ' '

                r32.write_str(indicativo_recolhimento, 1)
                
                # 135 359  Brancos
                r32.write_str('', 225)
                # 360 360  Final da Linha
                r32.write_str('*', 1)

                order = '321' + str(cnpj) + '1' + str(cnpj) + str(pis_pasep) +\
                    str(d) + contract_type

                lines.append({'line': r32, 'order': order})

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
            lines.append({'line': r90, 'order': '90'})

            # Ordena linhas de acordo chave "order"
            lines = sorted(lines, key=lambda k: k['order'])

            file_content = '\n'.join([l['line'].content.upper() for l in lines])
            message = u'Arquivo gerado com sucesso'
            state = 'done'

            print file_content
            file_name = 'SEFIP.RE'

            encoded_data = file_content.encode("utf-8").encode("base64")
            self.write(cr, uid, ids, {
                'file': encoded_data,
                'file_name': file_name,
                #'state': state,
                'message': message,
                },
                context=context)

        ir_model_data = self.pool.get('ir.model.data')
        __, view_id = ir_model_data.get_object_reference(
            cr, uid, 'l10n_br_hr', 'view_l10n_br_hr_sefip_generate_form'
            )

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'l10n_br_hr.sefip',
            'res_id': ids[0],
            'view_type': 'form',
            'view_mode': 'form',
            'views': [(view_id, 'form')],
            'view_id': False,
            'target': 'new',
            'nodestroy': True,
            }


sefip()
