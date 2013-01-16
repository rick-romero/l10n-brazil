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
import re
import datetime


class line:
    def __init__(self):
        self.content = ''

    def write_num(self, data, size):
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


class rais(osv.osv_memory):
    _name = 'l10n_br_hr.rais'
    _description = 'Generate RAIS File'
    _inherit = "ir.wizard.screen"
    _columns = {
        'state': fields.selection([('init', 'init'),
                                   ('done', 'done'),
                                   ], 'state', readonly=True),
        'last_sync_date': fields.datetime('Last Sync Date'),
        'message': fields.text('Message'),
        'file': fields.binary(u'Arquivo', readonly=True),
        'file_name': fields.char(u'Nome do Arquivo', 128, readonly=True),
        'company_id': fields.many2one('res.company', u'Empresa',
                                      required=True),
        'participa_pat': fields.boolean(u'Participa do PAT'),
        'cnpj': fields.char(u'CNPJ', size=18),
        'ano_da_declaracao': fields.integer(u'Ano da Declaração', size=4),
        'responsavel': fields.many2one('res.partner', u'Responsável'),
        'responsavel_tipo_de_inscricao': fields.selection([
            ('1', 'CNPJ'),
            ('4', 'CPF'),
            ], u'Tipo de Inscrição', required=True
            ),
        'responsavel_cnpj': fields.char(u'CNPJ', size=18),
        'responsavel_cpf': fields.char(u'CPF', size=15),
        'responsavel_legal_name': fields.char(u'Razão Social', size=128, required=True),
        'responsavel_name': fields.char(u'Nome do Responsável', size=128, required=True),
        'responsavel_email': fields.char(u'E-mail', size=128),
        'responsavel_birthday': fields.date(u'Data de Nascimento'),
        'responsavel_phone_ddd': fields.integer(u'DDD', size=2),
        'responsavel_phone': fields.integer(u'Telefone', size=8),
        'responsavel_street': fields.char(u'Logradouro', size=40),
        'responsavel_number': fields.char(u'Número', size=6),
        'responsavel_street2': fields.char(u'Complemento', size=21),
        'responsavel_district': fields.char(u'Bairro', size=19),
        'responsavel_zip': fields.integer(u'CEP', size=8),
        'responsavel_l10n_br_city_id': fields.many2one('l10n_br_base.city', u'Cidade',
                                           required=True),

        'indicador_retificacao': fields.selection([
                ('2', u'Primeira Entrega'),
                ('1', u'Retificação'),
            ], u'Indicador de Retificação'),
        'crea_retificacao': fields.integer(u'CREA a ser Retificado', size=12),
        'numero_proprietarios': fields.integer(
            u'Número de Proprietários em Atividade',
            size=2
            ),
        'data_base': fields.selection([
            ('01', u'Janeiro'),
            ('02', u'Fevereiro'),
            ('03', u'Março'),
            ('04', u'Abril'),
            ('05', u'Maio'),
            ('06', u'Junho'),
            ('07', u'Julho'),
            ('08', u'Agosto'),
            ('09', u'Setembro'),
            ('10', u'Outubro'),
            ('11', u'Novembro'),
            ('12', u'Dezembro'),
            ],
            u'Data-Base',
            help=u'Data-base da categoria (mês do reajuste salarial) com ' + \
                u'maior número de empregados no(a) estabelecimento/entidade.',
            ),
        'para_uso_da_empresa': fields.char(u'Para Uso da Empresa', size=12),
        'pat_trabalhadores_baixa_renda': fields.integer(
            u'Número de Trabalhadores que Recebem até 5 Salários Mínimos',
            size=6
            ),
        'pat_trabalhadores_alta_renda': fields.integer(
            u'Número de Trabalhadores que Recebem Acima de 5 Salários Mínimos',
            size=6
            ),
        'porcentagem_servico_proprio': fields.integer(
            u'Porcentagem de Serviço Próprio',
            size=3
            ),
        'porcentagem_admin_cozinhas': fields.integer(
            u'Porcentagem de Administração de Cozinhas',
            size=3
            ),
        'porcentagem_refeicao_convenio': fields.integer(
            u'Porcentagem de Refeição-Convênio',
            size=3
            ),
        'porcentagem_refeicoes_transportadas': fields.integer(
            u'Porcentagem de Refeições Transportadas',
            size=3
            ),
        'porcentagem_cesta_alimento': fields.integer(
            u'Porcentagem de Cesta Alimento',
            size=3
            ),
        'porcentagem_alimentacao_convenio': fields.integer(
            u'Porcentagem de Alimentação-Convênio',
            size=3
            ),
        'indicador_encerramento': fields.selection([
            ('1', u'Encerrou suas atividades'),
            ('2', u'Não encerrou suas atividades'),
            ],
            u'Indicador de Encerramento das Atividades'
            ),
        'data_de_encerramento': fields.date(
            u'Data de Encerramento das Atividades'
            ),
        'em_atividade_no_ano_base': fields.boolean(
            u'Esteve em Atividade no Ano-Base', required=True
            ),
        'indicador_centralizacao_contribuicao': fields.boolean(
            u'Indicador de Centralização de Contribuição Sindical',
            required=True
            ),
        'cnpj_centralizador_contribuicao': fields.char(
            u'CNPJ do Estabelecimento Centralizador da Contribuição Sindical',
            size=18
            ),
        'filiada_a_sindicato': fields.boolean(
            u'Empresa Filiada a Sindicato',
            required=True
            ),
        'sindicato_contribuicao_associativa': fields.many2one(
            'res.partner',
            u'Sindicato - Contribuição Associativa (Patronal)',
            ),
        'valor_contribuicao_associativa': fields.float(
            u'Valor - Contribuição Associativa (Patronal)',
            size=9
            ),
        'sindicato_contribuicao_sindical': fields.many2one(
            'res.partner',
            u'Sindicato - Contribuição (Tributo) Sindical (Patronal)',
            ),
        'valor_contribuicao_sindical': fields.float(
            u'Valor - Contribuição (Tributo) Sindical (Patronal)',
            size=9
            ),
        'sindicato_contribuicao_assistencial': fields.many2one(
            'res.partner',
            u'Sindicato - Contribuição Assistencial (Patronal)',
            ),
        'valor_contribuicao_assistencial': fields.float(
            u'Valor - Contribuição Assistencial (Patronal)',
            size=9
            ),
        'sindicato_contribuicao_confederativa': fields.many2one(
            'res.partner',
            u'Sindicato - Contribuição Confederativa (Patronal)',
            ),
        'valor_contribuicao_confederativa': fields.float(
            u'Valor - Contribuição Confederativa (Patronal)',
            size=9
            ),
        }
    _defaults = {
        'state': 'init',
        'indicador_retificacao': '2',
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

    def _constraint_cnpj(self, cr, uid, ids):
        rais_data = self.browse(cr, uid, ids[0])
        if not rais_data.cnpj:
            return True
        return self._validate_cnpj(rais_data.cnpj)

    def _constraint_responsavel_cnpj(self, cr, uid, ids):
        rais_data = self.browse(cr, uid, ids[0])
        if not rais_data.responsavel_cnpj or \
            rais_data.responsavel_tipo_de_inscricao != '1':
            return True
        return self._validate_cnpj(rais_data.responsavel_cnpj)

    def _constraint_cnpj_centralizador_contribuicao(self, cr, uid, ids):
        rais_data = self.browse(cr, uid, ids[0])
        if not rais_data.cnpj_centralizador_contribuicao:
            return True
        return self._validate_cnpj(rais_data.cnpj_centralizador_contribuicao)

    def _validate_cpf(self, cr, uid, ids):
        rais_data = self.browse(cr, uid, ids[0])
        if not rais_data.responsavel_cpf or \
            rais_data.responsavel_tipo_de_inscricao != '4':
            return True

        cpf = rais_data.responsavel_cpf

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
        (_constraint_cnpj, u'CNPJ inválido.', ['cnpj']),
        (_constraint_responsavel_cnpj, u'CNPJ do responsável é inválido.',
         ['responsavel_cnpj']),
        (_constraint_cnpj_centralizador_contribuicao,
         u'CNPJ do estabelecimento centralizador da contribuição sindical é inválido.',
         ['cnpj_centralizador_contribuicao']),
        (_validate_cpf, u'CPF inválido.', ['responsavel_cpf']),
        ]

    def _mask_cnpj(self, cnpj, field_name='cnpj'):
        if not cnpj:
            return {}
        val = re.sub('[^0-9]', '', cnpj)

        if len(val) >= 14:
            cnpj = "%s.%s.%s/%s-%s" % (val[0:2], val[2:5], val[5:8], val[8:12], val[12:14])

        return {'value': {field_name: cnpj}}

    def onchange_cnpj(self, cr, uid, ids, cnpj):
        return self._mask_cnpj(cnpj)

    def onchange_responsavel_cnpj(self, cr, uid, ids, cnpj):
        return self._mask_cnpj(cnpj, 'responsavel_cnpj')

    def onchange_responsavel_cpf(self, cr, uid, ids, cpf):
        if not cpf:
            return {}
        val = re.sub('[^0-9]', '', cpf)

        if len(val) >= 11:
            cpf = "%s.%s.%s-%s" % (val[0:3], val[3:6], val[6:9], val[9:11])

        return {'value': {'responsavel_cpf': cpf}}

    def onchange_cnpj_centralizador_contribuicao(self, cr, uid, ids, cnpj):
        return self._mask_cnpj(cnpj, 'cnpj_centralizador_contribuicao')

    def onchange_company_id(self, cr, uid, ids, company_id):
        result = {'value': {}}
        company_obj = self.pool.get('res.company')

        company = company_obj.browse(cr, uid, company_id)

        result['value']['participa_pat'] = company.participa_pat

        if company.cnpj:
            result['value']['cnpj'] = company.cnpj

        return result

    def onchange_responsavel(self, cr, uid, ids, partner_id):
        partner_data = {}
        partner_obj = self.pool.get('res.partner')
        partner_address_obj = self.pool.get('res.partner.address')
        partner = partner_obj.browse(cr, uid, partner_id)
        if partner:
            tipo_de_inscricao = partner.tipo_pessoa == 'J' and '1' or '4'
            partner_data = {
                'responsavel_legal_name': partner.legal_name,
                'responsavel_tipo_de_inscricao': tipo_de_inscricao,
                'responsavel_birthday': partner.birthday,
                }

            if partner.tipo_pessoa == 'J':
                partner_data['responsavel_cnpj'] = partner.cnpj_cpf
            else:
                partner_data['responsavel_cpf'] = partner.cnpj_cpf

            default_address = partner_obj.address_get(
                cr, uid, [partner_id], ['default']
                )

            if default_address['default']:
                partner_addr = partner_address_obj.browse(
                    cr, uid, default_address['default']
                    )
                partner_data['responsavel_name'] = partner_addr.name
                partner_data['responsavel_email'] = partner_addr.email
                if partner_addr.phone:
                    phone_str = re.sub(
                        '[^0-9]', '', str(partner_addr.phone)
                        )
                    partner_data['responsavel_phone_ddd'] = int(phone_str[:2])
                    partner_data['responsavel_phone'] = int(phone_str[2:])

                partner_data['responsavel_street'] = partner_addr.street
                partner_data['responsavel_number'] = partner_addr.number
                partner_data['responsavel_street2'] = partner_addr.street2
                partner_data['responsavel_district'] = partner_addr.district
                if partner_addr.zip:
                    partner_data['responsavel_zip'] = int(re.sub(
                        '[^0-9]', '', str(partner_addr.zip)
                        ))
                partner_data['responsavel_l10n_br_city_id'] = \
                    partner_addr.l10n_br_city_id.id

        return {'value': partner_data}

    def generate_file(self, cr, uid, ids, context=None):

        rais_data = self.browse(cr, uid, ids[0])

        lines = []

        r = self.browse(cr, uid, ids[0])
        company = r.company_id

        holidays_obj = self.pool.get('hr.holidays')
        payslip_obj = self.pool.get('hr.payslip')
        payslip_line_obj = self.pool.get('hr.payslip.line')
        employee_obj = self.pool.get('hr.employee')
        employee_ids = employee_obj.search(cr, uid,
                                           [('company_id', '=', company.id)],
                                           context=context)
        employees = employee_obj.browse(cr, uid, employee_ids, context=context)

        seq = 1

        if not company.cnpj:
            message = u'A empresa deve possuir CNPJ cadastrado'
            state = 'init'
            raise osv.except_osv(_('Error'), message)

        else:
            '''
            TYPE-0 - Header
            '''
            type0 = line()

            # 001 a 006  06  Número   Sequencial do registro no arquivo
            type0.write_num(seq, 6)
            # 007 a 020  14  Número   Inscrição CNPJ/CEI do 1º estabelecimento do arquivo
            type0.write_num(re.sub('[^0-9]', '', company.cnpj), 14)
            # 021 a 022  02  Alfanum  Prefixo do 1º estabelecimento do arquivo
            type0.write_str('00', 2)
            # 023 a 023  01  Número   Tipo do registro = 0
            type0.write_num(0, 1)
            # 024 a 024  01  Número   Constante = 1
            type0.write_num(1, 1)
            # 025 a 038  14  Número   CNPJ/CEI/CPF do responsável
            if rais_data.responsavel_tipo_de_inscricao == '1':
                if not rais_data.cnpj:
                    raise osv.except_osv(_('Error'), u'Favor informar o CNPJ.')

                cnpj_cpf = rais_data.responsavel_cnpj

            else:
                if not rais_data.responsavel_cpf:
                    raise osv.except_osv(_('Error'), u'Favor informar o CPF.')

                cnpj_cpf = rais_data.responsavel_cpf

            type0.write_num(re.sub('[^0-9]', '', cnpj_cpf), 14)
            # 039 a 039  01  Número   Tipo de Inscrição do responsável
            type0.write_num(rais_data.responsavel_tipo_de_inscricao, 1)

            # 040 a 079  40  Alfanum  Razão Social/ Nome do responsável
            type0.write_str(rais_data.responsavel_legal_name, 40)

            # 080 a 119  40  Alfanum  Logradouro do responsável
            type0.write_str(rais_data.responsavel_street, 40)
            # 120 a 125  06  Número   Número
            type0.write_num(int(rais_data.responsavel_number), 6)
            # 126 a 146  21  Alfanum  Complemento
            type0.write_str(rais_data.responsavel_street2, 21)
            # 147 a 165  19  Alfanum  Bairro
            type0.write_str(rais_data.responsavel_district, 19)
            # 166 a 173  08  Número   CEP
            type0.write_str(
                re.sub('[^0-9]', '', str(rais_data.responsavel_zip)), 8
                )

            if rais_data.responsavel_l10n_br_city_id:
                city = rais_data.responsavel_l10n_br_city_id
                # 174 a 180  07  Número   Código do Município
                type0.write_num(city.ibge_code, 7)
                # 181 a 210  30  Alfanum  Nome do Município
                type0.write_str(city.name, 30)
                # 211 a 212  02  Alfa Sigla da UF
                type0.write_str(city.state_id.code, 2)
            else:
                type0.write_str('', 39)

            # 213 a 214  02  Número   Telefone/Fax para contato (Código DDD)
            type0.write_num(rais_data.responsavel_phone_ddd, 2)
            # 215 a 222  08  Número   Telefone/Fax para contato (Número)
            type0.write_num(rais_data.responsavel_phone, 8)

            # 223 a 223  01  Número   Indicador de retificação da declaração
            #                         1 - retifica os estabelecimentos entregues anteriormente
            #                         2 - a declaração não é retificação (é primeira entrega)
            type0.write_num(rais_data.indicador_retificacao, 1)
            # 224 a 231  08  Número   Data da retificação dos estabelecimentos (ddmmaaaa)
            today = datetime.datetime.today().strftime('%d%m%Y')
            type0.write_num(today, 8)

            # 232 a 239  08  Número   Data de geração do arquivo (ddmmaaaa)
            type0.write_str(today, 8)
            # 240 a 284  45  Alfanum  E-mail do responsável
            type0.write_str(rais_data.responsavel_email, 45)
            # 285 a 336  52  Alfanum  Nome do Responsável
            type0.write_str(rais_data.responsavel_name, 52)
            # 337 a 356  20  Alfanum Espaços
            type0.write_str('', 20)
            # 357 a 360  04  Número   Constante = 0551
            type0.write_num(551, 4)
            # 361 a 371  11  Número   CPF do responsável
            if rais_data.responsavel_cpf:
                type0.write_str(
                    re.sub('[^0-9]', '', rais_data.responsavel_cpf), 11
                    )
            else:
                type0.write_str('', 11)

            # 372 a 383  12  Número   CREA a ser retificado: fazer campo
            type0.write_num(rais_data.crea_retificacao, 12)

            # 384 a 391  08  Numero   Data de nascimento do responsável (ddmmaaaa)
            if rais_data.responsavel_birthday:
                birthday = datetime.datetime.strptime(
                    rais_data.responsavel_birthday, '%Y-%m-%d'
                    )
                type0.write_str(birthday.strftime('%d%m%Y'), 8)
            else:
                type0.write_num(0, 8)

            # 392 a 551 160  Alfanum  Espaços
            type0.write_str('', 160)

            lines.append(type0)

            '''
            TYPE-1 - Company
            '''
            type1_count = 0

            type1 = line()
            type1_count += 1

            # 001 a 006  06  Número   Sequencial do registro no arquivo
            seq += 1
            type1.write_num(seq, 6)
            # 007 a 020  14  Número   Inscrição CNPJ/CEI do estabelecimento
            type1.write_num(re.sub('[^0-9]', '', company.cnpj), 14)
            # 021 a 022  02  Alfanum  Prefixo do estabelecimento
            type1.write_str('00', 2)
            # 023 a 023  01  Número   Tipo do registro = 1
            type1.write_num(1, 1)
            # 024 a 075  52  Alfanum  Razão Social
            type1.write_str(company.legal_name, 52)

            if company.partner_id.address:
                company_address = company.partner_id.address[0]

                # 076 a 115  40  Alfanum  Logradouro
                type1.write_str(company_address.street, 40)
                # 116 a 121  06  Número   Número
                type1.write_str(company_address.number, 6)
                # 122 a 142  21  Alfanum  Complemento
                type1.write_str(company_address.street2, 21)
                # 143 a 161  19  Alfanum  Bairro
                type1.write_str(company_address.district, 19)
                # 162 a 169  08  Número   CEP
                type1.write_str(
                    re.sub('[^0-9]', '', str(company_address.zip)), 8
                    )

                if company_address.l10n_br_city_id:
                    # 170 a 176  07  Número   Código do município
                    type1.write_num(
                        company_address.l10n_br_city_id.ibge_code, 7
                        )
                    # 177 a 206  30  Alfanum  Nome do município
                    type1.write_str(company_address.l10n_br_city_id.name, 30)
                    # 207 a 208  02  Alfa Sigla da UF
                    type1.write_str(
                        company_address.l10n_br_city_id.state_id.code, 2
                        )
                else:
                    type1.write_str('', 39)

                if company_address.phone:
                    phone = re.sub('[^0-9]', '', str(company_address.phone))
                    # 209 a 210  02  Número   Telefone (Código DDD)
                    type1.write_str(phone, 2)
                    # 211 a 218  08  Número   Telefone (Número)
                    type1.write_str(phone[2:], 8)
                else:
                    type1.write_str('', 10)

                # 219 a 263  45  Alfunum  E-mail do estabelecimento
                type1.write_str(company_address.email, 45)

            else:
                type1.write_str('', 188)

            # 264 a 270  07  Número   Atividade Econômica (CNAE)
            type1.write_num(
                re.sub('[^0-9]', '', str(company.cnae_main_id.code)), 7
                )

            # 271 a 274  04  Número   Natureza Jurídica
            type1.write_str(
                re.sub('[^0-9]', '', str(company.natureza_juridica_id.code)),
                4
                )

            # 275 a 276  02  Número   Número de Proprietários
            type1.write_str(rais_data.numero_proprietarios, 2)

            # 277 a 278  02  Número   Data-base
            type1.write_num(rais_data.data_base, 2)

            # 279 a 279  01  Número   Tipo de Inscrição do estabelecimento
            type1.write_num(1, 1)

            # 280 a 280  01  Número   Tipo de RAIS
            #     0 - estabelecimento com empregados
            #     1 - estabelecimento sem empregados
            if len(employees):
                type1.write_num(0, 1)
            else:
                type1.write_num(1, 1)

            # 281 a 282  02  Número   Zeros
            type1.write_num(0, 2)

            # 283 a 294  12  Número   Matrícula CEI vinculada a uma inscrição CNPJ (1)
            #     Informe a matrícula CEI que possui inscrição simultânea no CNPJ.
            #     Exemplo: empresa de construção civil com empregados em obras específicas.
            # Não suportado por enquanto
            type1.write_num(0, 12)

            # 295 a 298  04  Número   2011
            type1.write_num(2011, 4)
            # 299 a 299  01  Número   Porte da Empresa
            #     1 - Microempresa
            #     2 - Empresa de Pequeno Porte
            #     3 - Empresa/orgão não classificados nos itens anteriores
            type1.write_num(company.porte_id.id, 1)
            # 300 a 300  01  Número   Indicador de Optante pelo Simples
            #     1 - é optante pelo Simples
            #     2 - não é optante pelo Simples
            if company.simples in ['2', '3', '6']:
                optante = 1
            else:
                optante = 2
            type1.write_num(optante, 1)
            # 301 a 301  01  Número   Indicador de participação no PAT 
            #     1 - participa do PAT
            #     2 - não participa do PAT
            if company.participa_pat:
                participa_pat = 1
            else:
                participa_pat = 2
            type1.write_num(participa_pat, 1)

            # 302 a 307  06  Número   PAT-Trabalhadores que recebem até 5 Sal.Mínimos
            type1.write_num(rais_data.pat_trabalhadores_baixa_renda, 6)
            # 308 a 313  06  Número   PAT-Trabalhadores que recebem acima de 5 Sal.Mínimos
            type1.write_num(rais_data.pat_trabalhadores_alta_renda, 6)

            # 314 a 316  03  Número   Porcentagem de serviço próprio (%)
            type1.write_num(rais_data.porcentagem_servico_proprio, 3)
            # 317 a 319  03  Número   Porcentagem de administração de cozinhas (%)
            type1.write_num(rais_data.porcentagem_admin_cozinhas, 3)
            # 320 a 322  03  Número   Porcentagem de refeição-convênio (%)
            type1.write_num(rais_data.porcentagem_refeicao_convenio, 3)
            # 323 a 325  03  Número   Porcentagem de refeições transportadas (%)
            type1.write_num(rais_data.porcentagem_refeicoes_transportadas, 3)
            # 326 a 328  03  Número   Porcentagem de cesta alimento (%)
            type1.write_num(rais_data.porcentagem_cesta_alimento, 3)
            # 329 a 331  03  Número   Porcentagem de alimentação-convênio (%)
            type1.write_num(rais_data.porcentagem_alimentacao_convenio, 3)

            # 332 a 332  01  Número   Indicador de Encerramento das atividades
            type1.write_num(rais_data.indicador_encerramento, 1)
            # 333 a 340  08  Número   Data de Encerramento das atividades (ddmmaaaa)
            if rais_data.data_de_encerramento:
                data_de_encerramento = datetime.datetime.strptime(
                    rais_data.data_de_encerramento, '%Y-%m-%d'
                    )
                type1.write_num(data_de_encerramento.strftime('%d%m%Y'), 8)
            else:
                type1.write_num(0, 8)

            # 341 a 354  14  Número   CNPJ - contribuição associativa (patronal)
            type1.write_num(re.sub(
                '[^0-9]', '',
                str(rais_data.sindicato_contribuicao_associativa.cnpj_cpf)
                ), 14)
            # 355 a 363  09  Número   Valor - contribuição associativa (patronal) (com centavos)
            type1.write_num(re.sub(
                '[^0-9]', '', '%.02f' % rais_data.valor_contribuicao_associativa
                ), 9)

            # 364 a 377  14  Número   CNPJ - contribuição (tributo) sindical (patronal)
            type1.write_num(re.sub(
                '[^0-9]', '',
                str(rais_data.sindicato_contribuicao_sindical.cnpj_cpf)
                ), 14)
            # 378 a 386  09  Número   Valor - contribuição (tributo) sindical (patronal) (com centavos)
            type1.write_num(re.sub(
                '[^0-9]', '', '%.02f' % rais_data.valor_contribuicao_sindical
                ), 9)

            # 387 a 400  14  Número   CNPJ - contribuição assistencial (patronal)
            type1.write_num(re.sub(
                '[^0-9]', '',
                str(rais_data.sindicato_contribuicao_assistencial.cnpj_cpf)
                ), 14)
            # 401 a 409  09  Número   Valor - contribuição assistencial (patronal) (com centavos)
            type1.write_num(re.sub(
                '[^0-9]', '', '%.02f' % rais_data.valor_contribuicao_assistencial
                ), 9)

            # 410 a 423  14  Número   CNPJ - contribuição confederativa (patronal)
            type1.write_num(re.sub(
                '[^0-9]', '',
                str(rais_data.sindicato_contribuicao_confederativa.cnpj_cpf)
                ), 14)
            # 424 a 432  09  Número   Valor - contribuição confederativa (patronal) (com centavos)
            type1.write_num(re.sub(
                '[^0-9]', '', '%.02f' % rais_data.valor_contribuicao_confederativa
                ), 9)

            # 33 a 433  01  Número   Esteve em atividade no ano-base
            type1.write_num(rais_data.em_atividade_no_ano_base and 1 or 2, 1)

            # 434 a 434  01  Número   Indicador de centralização do pagamento da contribuição sindical
            type1.write_num(
                rais_data.indicador_centralizacao_contribuicao and 1 or 2, 1
                )
            # 435 a 448  14  Número   CNPJ - estabelecimento centralizador da contribuição sindical
            type1.write_num(
                re.sub('[^0-9]', '',
                       str(rais_data.cnpj_centralizador_contribuicao)),
                14
                )

            # 449 a 449  01  Número   Indicador - empresa filiada a sindicato
            type1.write_num(rais_data.filiada_a_sindicato and 1 or 2, 1)

            # 450 a 539  90  Alfanum  Espaços
            type1.write_str('', 90)

            # 540 a 551  12  Alfanum  Informação de uso exclusivo da empresa
            type1.write_str(rais_data.para_uso_da_empresa, 12)

            lines.append(type1)

            '''
            TYPE-2 - Employees
            '''
            type2_count = 0

            for employee in employees:

                for contract in employee.contract_ids:

                    # check if contract was active in the base year
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
                        end_year = date_end.strftime('%Y')

                        if end_year < rais_data.ano_da_declaracao:
                            continue

                    type2 = line()
                    type2_count += 1

                    # 001 a 006  06  Número   Sequencial do registro no arquivo
                    seq += 1
                    type2.write_num(seq, 6)
                    # 007 a 020  14  Número   Inscrição CNPJ/CEI do estabelecimento
                    type2.write_str(re.sub('[^0-9]', '', company.cnpj), 14)
                    # 021 a 022  02  Alfanum  Prefixo do estabelecimento
                    type2.write_str('00', 2)
                    # 023 a 023  01  Número   Tipo do registro = 2
                    type2.write_num(2, 1)
                    # 024 a 034  11  Número   Código PIS/PASEP
                    type2.write_str(re.sub('[^0-9]', '', str(employee.pis_pasep)), 11)
                    # 035 a 086  52  Alfanum  Nome do Empregado
                    type2.write_str(employee.name, 52)

                    # 087 a 094  08  Número   Data de Nascimento (ddmmaaaa)
                    if employee.birthday:
                        birthday = datetime.datetime.strptime(
                            employee.birthday, '%Y-%m-%d'
                            )
                        type2.write_str(birthday.strftime('%d%m%Y'), 8)
                    else:
                        type2.write_num(0, 8)

                    # 095 a 096  02  Número   Nacionalidade
                    type2.write_num(employee.nationality_id.code, 2)
                    # 097 a 100  04  Número   Ano de Chegada ao país (aaaa)
                    type2.write_num(employee.ano_de_chegada, 4)
                    # 101 a 102  02  Número   Grau de Instrução (01 a 11)
                    type2.write_num(employee.grau_de_instrucao_id.code, 2)
                    # 103 a 113  11  Número   CPF
                    type2.write_str(re.sub('[^0-9]', '', str(employee.cpf)), 11)
                    # 114 a 121  08  Número   CTPS - (número)
                    type2.write_num(employee.carteira_de_trabalho_numero, 8)
                    # 122 a 126  05  Alfanum  CTPS - (série)
                    type2.write_num(employee.carteira_de_trabalho_serie, 5)
                    # 127 a 134  08  Número   Data de Admissão/Data da Transferência (ddmmaaaa)
                    if contract.date_start:
                        date_start = datetime.datetime.strptime(
                            contract.date_start, '%Y-%m-%d'
                            )
                        type2.write_str(date_start.strftime('%d%m%Y'), 8)
                    else:
                        type2.write_num(0, 8)
                    # 135 a 136  02  Número   Tipo de Admissão
                    type2.write_num(contract.tipo_de_admissao_id.code, 2)
                    # 137 a 145  09  Número   Salário Contratual (Valor com centavos)
                    salario_contratual = re.sub(
                        '[^0-9]', '', '%.02f' % contract.wage
                        )
                    type2.write_num(salario_contratual, 9)
                    # 146 a 146  01  Número   Tipo de Salário Contratual
                    type2.write_num(contract.tipo_de_salario_contratual, 1)

                    # 147 a 148  02  Número   Horas Semanais
                    working_hours = []

                    if contract.working_hours:
                        for att in contract.working_hours.attendance_ids:
                            diff = att.hour_to - att.hour_from

                            # if dayofweek is 0, reapeat all work days
                            if att.dayofweek == '0':
                                working_hours.append(5 * diff)
                            else:
                                working_hours.append(diff)

                    type2.write_num(sum(working_hours), 2)

                    # 149 a 154  06  Número   CBO
                    type2.write_num(contract.ocupacao_id.code, 6)
                    # 155 a 156  02  Número   Vínculo empregatício
                    type2.write_num(contract.vinculo_id.code, 2)
                    # 157 a 158  02  Número   Código do desligamento
                    type2.write_num(contract.motivo_de_desligamento_id.code, 2)

                    # 159 a 162  04  Número   Data do desligamento (ddmm)
                    if contract.data_de_desligamento:
                        data_de_desligamento = datetime.datetime.strptime(
                            contract.data_de_desligamento, '%Y-%m-%d'
                            )
                        type2.write_str(data_de_desligamento.strftime('%d%m'), 4)
                    else:
                        type2.write_num(0, 4)

                    payslip_ids = payslip_obj.search(cr, uid, [
                            ('state', '=', 'done'),
                            ('contract_id', '=', contract.id),
                        ],
                        context=context
                        )
                    payslips = payslip_obj.browse(
                        cr, uid, payslip_ids, context=context
                        )
                    
                    month = 1
                    grouped_payslips = {}

                    for m in range(1, 13):
                        grouped_payslips[m] = {'value': 0}
                        grouped_payslips['HEXTRAS_%d' % m] = {
                            'quantity': 0,
                            }

                    categories = [
                        '13SALAD', '13SALFI', 'DISSIDIO', 'ALW', 'BHORAS',
                        'CASSOC1', 'CASSOC2', 'CASSIST', 'CSIND', 'CCONF',
                        'MRESCISAO', 'FIND', 'APREVIO',
                        ]

                    for category in categories:
                        grouped_payslips[category] = {'value': 0}

                        if category in ['BHORAS', 'DISSIDIO', 'ALW']:
                            grouped_payslips[category]['months'] = set()

                    for payslip in payslips:

                        date_from = datetime.datetime.strptime(
                            payslip.date_from, '%Y-%m-%d'
                            )
                        month = int(date_from.strftime('%m'))

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

                        # Extra work time payslip lines
                        p_line_ids = payslip_line_obj.search(cr, uid, [
                            ('slip_id', '=', payslip.id),
                            ('code', 'in', ['HEXTRAS']),
                            ], context=context)

                        if p_line_ids:
                            p_lines = payslip_line_obj.browse(
                                cr, uid, p_line_ids, context=context
                                )
                            for l in p_lines:
                                try:
                                    grouped_payslips['HEXTRAS_%d' % month]['quantity'] += l.quantity
                                except KeyError:
                                    grouped_payslips['HEXTRAS_%d' % month]['quantity'] = l.quantity

                        # Other payslip line data
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

                                if l.code in ['BHORAS', 'DISSIDIO', 'ALW']:
                                    grouped_payslips[l.code]['months'].add(
                                        month
                                        )

                    # 163 a 171  09  Número   Remuneração de Janeiro (com centavos)
                    type2.write_num(re.sub(
                        '[^0-9]', '', '%.02f' % grouped_payslips[1]['value']
                        ), 9)
                    # 172 a 180  09  Número   Remuneração de Fevereiro (com centavos)
                    type2.write_num(re.sub(
                        '[^0-9]', '', '%.02f' % grouped_payslips[2]['value']
                        ), 9)
                    # 181 a 189  09  Número   Remuneração de Março (com centavos)
                    type2.write_num(re.sub(
                        '[^0-9]', '', '%.02f' % grouped_payslips[3]['value']
                        ), 9)
                    # 190 a 198  09  Número   Remuneração de Abril (com centavos)
                    type2.write_num(re.sub(
                        '[^0-9]', '', '%.02f' % grouped_payslips[4]['value']
                        ), 9)
                    # 199 a 207  09  Número   Remuneração de Maio (com centavos)
                    type2.write_num(re.sub(
                        '[^0-9]', '', '%.02f' % grouped_payslips[5]['value']
                        ), 9)
                    # 208 a 216  09  Número   Remuneração de Junho (com centavos)
                    type2.write_num(re.sub(
                        '[^0-9]', '', '%.02f' % grouped_payslips[6]['value']
                        ), 9)
                    # 217 a 225  09  Número   Remuneração de Julho (com centavos)
                    type2.write_num(re.sub(
                        '[^0-9]', '', '%.02f' % grouped_payslips[7]['value']
                        ), 9)
                    # 226 a 234  09  Número   Remuneração de Agosto (com centavos)
                    type2.write_num(re.sub(
                        '[^0-9]', '', '%.02f' % grouped_payslips[8]['value']
                        ), 9)
                    # 235 a 243  09  Número   Remuneração de Setembro (com centavos)
                    type2.write_num(re.sub(
                        '[^0-9]', '', '%.02f' % grouped_payslips[9]['value']
                        ), 9)
                    # 244 a 252  09  Número   Remuneração de Outubro (com centavos)
                    type2.write_num(re.sub(
                        '[^0-9]', '', '%.02f' % grouped_payslips[10]['value']
                        ), 9)
                    # 253 a 261  09  Número   Remuneração de Novembro (com centavos)
                    type2.write_num(re.sub(
                        '[^0-9]', '', '%.02f' % grouped_payslips[11]['value']
                        ), 9)
                    # 262 a 270  09  Número   Remuneração de Dezembro (com centavos)
                    type2.write_num(re.sub(
                        '[^0-9]', '', '%.02f' % grouped_payslips[12]['value']
                        ), 9)

                    # 271 a 279  09  Número   Remuneração de 13º Salário Adiantamento (com centavos)
                    type2.write_num(re.sub(
                        '[^0-9]', '', '%.02f' % grouped_payslips['13SALAD']['value']
                        ), 9)
                    # 280 a 281  02  Número   Mês de pagamento do 13º Salário Adiantamento
                    try:
                        create_date = grouped_payslips['13SALAD']['create_date'].strftime('%m')
                    except:
                        create_date = 0

                    type2.write_num(create_date, 2)

                    # 282 a 290  09  Número   Remuneração do 13º Salário Final (com centavos)
                    type2.write_num(re.sub(
                        '[^0-9]', '',
                        '%.02f' % grouped_payslips['13SALFI']['value']
                        ), 9)
                    # 291 a 292  02  Número   Mês de pagamento do 13º Salário Final
                    try:
                        create_date = grouped_payslips['13SALFI']['create_date'].strftime('%m')
                    except:
                        create_date = 0

                    type2.write_num(create_date, 2)

                    # 293 a 293  01  Número   Raça/Cor
                    type2.write_num(employee.etnia_id.code, 1)
                    # 294 a 294  01  Número   Indicador de Deficiência
                    if not employee.deficiencia or employee.deficiencia == '0':
                        type2.write_num(2, 1)
                    else:
                        type2.write_num(1, 1)
                    # 295 a 295  01  Número   Tipo de Deficiência
                    type2.write_num(employee.deficiencia, 1)
                    # 296 a 296  01  Número   Indicador de Alvará
                    type2.write_num(employee.possui_alvara_judicial, 1)

                    # 297 a 305  09  Número   Aviso Prévio Indenizado (valor com centavos)
                    type2.write_num(re.sub(
                        '[^0-9]', '',
                        '%.02f' % grouped_payslips['APREVIO']['value']
                        ), 9)

                    # 306 a 306  01  Número   Sexo  (1 - masc,  2 - fem)
                    if employee.gender == 'female':
                        type2.write_num(2, 1)
                    else:
                        type2.write_num(1, 1)

                    # 307 a 308  02  Número   Motivo do Primeiro Afastamento
                    # 309 a 312  04  Número   Data Início do Primeiro Afastamento (ddmm)
                    # 313 a 316  04  Número   Data Final do Primeiro Afastamento (ddmm)
                    # 317 a 318  02  Número   Motivo do Segundo Afastamento
                    # 319 a 322  04  Número   Data Início do Segundo Afastamento (ddmm)
                    # 323 a 326  04  Número   Data Final do Segundo Afastamento (ddmm)
                    # 327 a 328  02  Número   Motivo do Terceiro Afastamento
                    # 329 a 332  04  Número   Data Início do Terceiro Afastamento (ddmm)
                    # 333 a 336  04  Número   Data Final do Terceiro Afastamento (ddmm)
                    rais_period_min = '%d-01-01' % rais_data.ano_da_declaracao
                    rais_period_max = '%d-12-31' % rais_data.ano_da_declaracao
                    holidays_ids = holidays_obj.search(
                        cr, uid, [
                            ('employee_id', '=', employee.id),
                            ('state', '=', 'validate'),
                            '|',
                            '&',
                            ('date_from', '>=', rais_period_min),
                            ('date_from', '<=', rais_period_max),
                            '&',
                            ('date_to', '>=', rais_period_min),
                            ('date_to', '<=', rais_period_max),
                        ], limit=3
                        )

                    if holidays_ids:
                        holidays = holidays_obj.browse(cr, uid, holidays_ids,
                                                       context=context)
                        days = 0
                        count = 0
    
                        for holiday in holidays:
                            reason = holiday.holiday_status_id.code

                            if not reason:
                                continue
    
                            date_from = datetime.datetime.strptime(
                                holiday.date_from, '%Y-%m-%d %H:%M:%S'
                                )
                            date_to = datetime.datetime.strptime(
                                holiday.date_to, '%Y-%m-%d %H:%M:%S'
                                )
    
                            if holiday.number_of_days:
                                days += abs(holiday.number_of_days)
                            else:
                                delta = date_from - date_to
                                days += delta.days
    
                            type2.write_num(reason, 2)
                            type2.write_num(date_from.strftime('%d%m'), 4)
                            type2.write_num(date_to.strftime('%d%m'), 4)
                            count += 1

                        while count < 3:
                            type2.write_num(0, 10)
                            count += 1
    
                        # 337 a 339  03  Número   Quantidade Dias Afastamento
                        type2.write_num(days, 3)
                    else:
                        type2.write_num(0, 33)

                    # 340 a 347  08  Número   Valor - férias indenizadas (com centavos)
                    type2.write_num(re.sub(
                        '[^0-9]', '',
                        '%.02f' % grouped_payslips['FIND']['value']
                        ), 8)

                    # 348 a 355  08  Número   Valor - banco de horas (com centavos)
                    type2.write_num(re.sub(
                        '[^0-9]', '',
                        '%.02f' % grouped_payslips['BHORAS']['value']
                        ), 8)
                    # 356 a 357  02  Número   Quantidade de meses - banco de horas
                    type2.write_num(
                        len(grouped_payslips['BHORAS']['months']),
                        2
                        )

                    # 358 a 365  08  Número   Valor - dissídio coletivo (com centavos)
                    type2.write_num(re.sub(
                        '[^0-9]', '',
                        '%.02f' % grouped_payslips['DISSIDIO']['value']
                        ), 8)
                    # 366 a 367  02  Número   Quantidade de meses - dissídio coletivo
                    type2.write_num(
                        len(grouped_payslips['DISSIDIO']['months']),
                        2
                        )

                    # 368 a 375  08  Número   Valor - gratificações (com centavos)
                    type2.write_num(re.sub(
                        '[^0-9]', '',
                        '%.02f' % grouped_payslips['ALW']['value']
                        ), 8)
                    # 376 a 377  02  Número   Quantidade de meses - gratificações
                    type2.write_num(
                        len(grouped_payslips['ALW']['months']),
                        2
                        )

                    # 378 a 385  08  Número   Valor - multa por rescisão sem justa causa (com centavos)
                    type2.write_num(re.sub(
                        '[^0-9]', '',
                        '%.02f' % grouped_payslips['MRESCISAO']['value']
                        ), 8)

                    # 386 a 399  14  Número   CNPJ - contribuição associativa (1ª ocorrência)
                    type2.write_num(re.sub(
                        '[^0-9]', '', contract.sindicato_cassoc1.cnpj_cpf
                        ), 14)
                    # 400 a 407  08  Número   Valor - contribuição associativa (1ª ocorrência) (com centavos)
                    type2.write_num(re.sub(
                        '[^0-9]', '',
                        '%.02f' % grouped_payslips['CASSOC1']['value']
                        ), 8)

                    # 408 a 421  14  Número   CNPJ - contribuição associativa (2ª ocorrência)
                    type2.write_num(re.sub(
                        '[^0-9]', '', contract.sindicato_cassoc2.cnpj_cpf
                        ), 14)
                    # 422 a 429  08  Número   Valor - contribuição associativa (2ª ocorrência) (com centavos)
                    type2.write_num(re.sub(
                        '[^0-9]', '',
                        '%.02f' % grouped_payslips['CASSOC2']['value']
                        ), 8)

                    # 430 a 443  14  Número   CNPJ - contribuição (tributo) sindical
                    type2.write_num(re.sub(
                        '[^0-9]', '', contract.sindicato_csind.cnpj_cpf
                        ), 14)
                    # 444 a 451  08  Número   Valor - contribuição (tributo) sindical (com centavos)
                    type2.write_num(re.sub(
                        '[^0-9]', '',
                        '%.02f' % grouped_payslips['CSIND']['value']
                        ), 8)

                    # 452 a 465  14  Número   CNPJ - contribuição assistencial
                    type2.write_num(re.sub(
                        '[^0-9]', '', contract.sindicato_cassist.cnpj_cpf
                        ), 14)
                    # 466 a 473  08  Número   Valor - contribuição assistencial (com centavos)
                    type2.write_num(re.sub(
                        '[^0-9]', '',
                        '%.02f' % grouped_payslips['CASSIST']['value']
                        ), 8)

                    # 474 a 487  14  Número   CNPJ - contribuição confederativa
                    type2.write_num(re.sub(
                        '[^0-9]', '', contract.sindicato_cconf.cnpj_cpf
                        ), 14)
                    # 488 a 495  08  Número   Valor - contribuição confederativa (com centavos)
                    type2.write_num(re.sub(
                        '[^0-9]', '',
                        '%.02f' % grouped_payslips['CCONF']['value']
                        ), 8)

                    # 496 a 502  07  Número   Município - local de trabalho
                    type2.write_num(contract.local_de_trabalho_cidade.ibge_code, 7)

                    # 503 a 505  03  Número Horas Extras Trabalhadas - Janeiro
                    type2.write_num(
                        grouped_payslips['HEXTRAS_1']['quantity'], 3
                        )
                    # 506 a 508  03  Número Horas Extras Trabalhadas - Fevereiro
                    type2.write_num(
                        grouped_payslips['HEXTRAS_2']['quantity'], 3
                        )
                    # 509 a 511  03  Número Horas Extras Trabalhadas - Março
                    type2.write_num(
                        grouped_payslips['HEXTRAS_3']['quantity'], 3
                        )
                    # 512 a 514  03  Número Horas Extras Trabalhadas - Abril
                    type2.write_num(
                        grouped_payslips['HEXTRAS_4']['quantity'], 3
                        )
                    # 515 a 517  03  Número Horas Extras Trabalhadas - Maio
                    type2.write_num(
                        grouped_payslips['HEXTRAS_5']['quantity'], 3
                        )
                    # 518 a 520  03  Número Horas Extras Trabalhadas - Junho
                    type2.write_num(
                        grouped_payslips['HEXTRAS_6']['quantity'], 3
                        )
                    # 521 a 523  03  Número Horas Extras Trabalhadas - Julho
                    type2.write_num(
                        grouped_payslips['HEXTRAS_7']['quantity'], 3
                        )
                    # 524 a 526  03  Número Horas Extras Trabalhadas - Agosto
                    type2.write_num(
                        grouped_payslips['HEXTRAS_8']['quantity'], 3
                        )
                    # 527 a 529  03  Número Horas Extras Trabalhadas - Setembro
                    type2.write_num(
                        grouped_payslips['HEXTRAS_9']['quantity'], 3
                        )
                    # 530 a 532  03  Número Horas Extras Trabalhadas - Outubro
                    type2.write_num(
                        grouped_payslips['HEXTRAS_10']['quantity'], 3
                        )
                    # 533 a 535  03  Número Horas Extras Trabalhadas - Novembro
                    type2.write_num(
                        grouped_payslips['HEXTRAS_11']['quantity'], 3
                        )
                    # 536 a 538  03  Número Horas Extras Trabalhadas - Dezembro
                    type2.write_num(
                        grouped_payslips['HEXTRAS_12']['quantity'], 3
                        )

                    # 539 a 539  01  Número   Indicador - empregado filiado a sindicato
                    #    1 - Sim
                    #    2 - Não
                    filiado = contract.filiado_a_sindicato and 1 or 2
                    type2.write_num(filiado, 1)

                    # 540 a 551  12  Alfanum  Informação de uso exclusivo da empresa.
                    type2.write_str('', 12)

                    lines.append(type2)

            '''
            TYPE-9 - Footer
            '''
            type9 = line()

            # 001 a 006  06  Número   Sequencial do registro no arquivo
            seq += 1
            type9.write_num(seq, 6)
            # 007 a 020  14  Número   Inscrição CNPJ/CEI do último estabelecimento do arquivo
            type9.write_str(re.sub('[^0-9]', '', company.cnpj), 14)
            # 021 a 022  02  Alfanum  Prefixo do último estabelecimento do arquivo
            type9.write_str('00', 2)
            # 023 a 023  01  Número   Tipo do registro = 9
            type9.write_num(9, 1)
            # 024 a 029  06  Número   Total de registros tipo 1 no arquivo
            type9.write_num(type1_count, 6)
            # 030 a 035  06  Número   Total de registros tipo 2 no arquivo
            type9.write_num(type2_count, 6)
            # 036 a 551 516  Alfanum Espaços
            type9.write_str('', 516)
            lines.append(type9)

            file_content = '\n'.join([l.content.upper() for l in lines])
            message = u'Arquivo gerado com sucesso'
            state = 'done'

            file_name = 'rais_{}.txt'.format(rais_data.ano_da_declaracao)

            encoded_data = file_content.encode("utf-8").encode("base64")
            self.write(cr, uid, ids, {
                'file': encoded_data,
                'file_name': file_name,
                'state': state,
                'message': message,
                },
                context=context)

            return True

        self.write(cr, uid, ids, {
            'state': state,
            'message': message,
            })

        return False

rais()
