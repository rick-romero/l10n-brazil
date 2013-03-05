# -*- coding: utf-8 -*-

##############################################################################
#                                                                            #
#  Copyright (C) 2013 Proge Informática Ltda (<http://www.proge.com.br>).    #
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
import datetime
import cnab240
from cnab240.bancos import bb
import decimal
import re


class payment_line(osv.osv):
    _name = 'l10n_br_account_cnab240.payment.line'
    _description = 'Payment order line'
    _columns = {
        'payment': fields.many2one(
            'l10n_br_account_cnab240.payment',
            u'Referência da Ordem de Pagamento',
            required=True,
            ondelete='cascade',
            select=True,
            ),
        'document_number': fields.integer(
            u'Número do Documento', required=True
            ),
        'expiration_date': fields.date(u'Vencimento do Título'),
        'value': fields.float(
            u'Valor do Título', digits=(0, 2), required=True
            ),
        'type': fields.selection([
                ('01', u'CH Cheque'),
                ('02', u'DM Duplicata Mercantil'),
                ('03', u'DMI Duplicata Mercantil p/ Indicação'),
                ('04', u'DS Duplicata de Serviço'),
                ('05', u'DSI Duplicata de Serviço p/ Indicação'),
                ('06', u'DR Duplicata Rural'),
                ('07', u'LC Letra de Câmbio'),
                ('08', u'NCC Nota de Crédito Comercial'),
                ('09', u'NCE Nota de Crédito a Exportação'),
                ('10', u'NCI Nota de Crédito Industrial'),
                ('11', u'NCR Nota de Crédito Rural'),
                ('12', u'NP Nota Promissória'),
                ('13', u'NPR Nota Promissória Rural'),
                ('14', u'TM Triplicata Mercantil'),
                ('15', u'TS Triplicata de Serviço'),
                ('16', u'NS Nota de Seguro'),
                ('17', u'RC Recibo'),
                ('18', u'FAT Fatura'),
                ('19', u'ND Nota de Débito'),
            ],
            u'Espécie do Título',
            required=True,
            ),
        'acceptance': fields.selection([
                ('A', 'Aceite'),
                ('N', 'Não Aceite'),
            ],
            u'Aceite',
            required=True,
            ),
        'emission_date': fields.date(u'Data de Emissão', required=True),
        'daily_interest': fields.float(
            u'Juros de Mora por Dia',
            help=u'Valor ou porcentagem sobre o valor do título a ser ' +\
                'cobrada de juros de mora.',
            ),
        'discount_value': fields.float(u'Juros de Mora por Dia'),
        'description': fields.char(u'Identificação do Título', size=128),
        'protest': fields.selection([
                ('1', u'Protestar Dias Corridos'),
                ('2', u'Protestar Dias Úteis'),
                ('3', u'Não Protestar'),
                ('4', u'Protestar Fim Falimentar - Dias Úteis'),
                ('5', u'Protestar Fim Falimentar - Dias Corridos'),
                ('8', u'Negativação sem Protesto'),
                ('9', u'Cancelamento Protesto Automático'),
            ],
            u'Protesto',
            ),
        'protest_time': fields.integer(u'Número de Dias para Protesto'),
        'devolution': fields.selection([
                ('1', u'Baixar/Devolver'),
                ('2', u'Não Baixar/Não Devolver'),
                ('3', u'Cancelar Prazo para Baixa/Devolução'),
            ],
            u'Baixa/Devolução',
            ),
        'devolution_time': fields.integer(
            u'Número de Dias para Baixa/Devolução'
            ),
        'wallet': fields.selection([
                ('1', u'Cobrança Simples'),
                ('2', u'Cobrança Vinculada'),
                ('3', u'Cobrança Caucionada'),
                ('4', u'Cobrança Descontada'),
                ('5', u'Cobrança Vendor'),
            ],
            u'Carteira',
            ),
        'action': fields.selection([
                ('0', u'Inclusão de Pagamento'),
                ('9', u'Exclusão de Pagamento'),
            ],
            u'Tipo de Movimento',
            required=True,
            ),
        }
    _defaults = {
        'emission_date': lambda self, cr, uid, c: \
            datetime.datetime.today().strftime('%Y-%m-%d'),
        'protest': '3',
        'action': '0',
        }


payment_line()


class payment(osv.osv):
    _name = 'l10n_br_account_cnab240.payment'
    _description = 'Generate payment order'
    _columns = {
        'payer_company': fields.many2one('res.company', u'Empresa'),
        'payer_bank': fields.many2one('res.partner.bank', u'Banco'),
        'recipient_partner': fields.many2one('res.partner', u'Parceiro'),
        'recipient_bank': fields.many2one('res.partner.bank', u'Banco'),
        'payment_line': fields.one2many(
            'l10n_br_account_cnab240.payment.line',
            'payment',
            u'Pagamentos',
            ),
        'type': fields.selection([
                ('01', u'Crédito em Conta Corrente'),
                ('02', u'Pagamento Contra Recibo'),
                ('03', u'DOC/TED'),
                ('04', u'Cartão Salário'),
                ('05', u'Crédito em Conta Poupança'),
                ('10', u'Ordem de Pagamento'),
                ('41', u'TED Outra Titularidade'),
                ('43', u'TED Mesma Titularidade'),
            ],
            u'Operação',
            required=True,
            ),
        'service_type': fields.selection([
                ('20', u'Pagamento a Fornecedores'),
                ('30', u'Pagamento de Salários'),
                ('98', u'Pagamentos Diversos'),
            ],
            u'Tipo de Serviço',
            ),
        'agreement_number': fields.integer(
            u'Nº do Convênio de Pagamento',
            size=9,
            required=True,
            ),
        'file': fields.binary(u'Arquivo', readonly=True),
        'file_name': fields.char(u'Nome do Arquivo', 128, readonly=True),
        }
    _defaults = {
        'payer_company': lambda self, cr, uid, c: self.pool.get(
            'res.company'
            )._company_default_get(cr, uid, 'account.invoice', context=c),
        }

    def onchange_payer_company(self, cr, uid, ids, company_id):
        bank_obj = self.pool.get('res.partner.bank')
        bank_ids = bank_obj.search(cr, uid, [('company_id', '=', company_id)])
        bank_id = len(bank_ids) and bank_ids[0] or None

        result = {'value': {}}
        if bank_id is not None:
            result['value']['payer_bank'] = bank_id
        return result

    def onchange_recipient_partner(self, cr, uid, ids, partner_id):
        bank_obj = self.pool.get('res.partner.bank')
        bank_ids = bank_obj.search(cr, uid, [('partner_id', '=', partner_id)])
        bank_id = len(bank_ids) and bank_ids[0] or None

        result = {'value': {}}
        if bank_id is not None:
            result['value']['recipient_bank'] = bank_id
        return result

    def generate_file(self, cr, uid, ids, context=None):
        partner_obj = self.pool.get('res.partner')
        partner_address_obj = self.pool.get('res.partner.address')
        order = self.browse(cr, uid, ids[0])

        if order.payer_bank.bank_bic != '001':
            raise osv.except_osv(
                u'Banco não suportado.',
                u'Atualmente apenas o Banco do Brasil é suportado.'
                )

        company_address = None
        address = None

        company_default_address = partner_obj.address_get(
            cr, uid, [order.payer_company.partner_id.id], ['default']
            )
        default_address = partner_obj.address_get(
            cr, uid, [order.recipient_partner.id], ['default']
            )

        if company_default_address['default']:
            company_address = partner_address_obj.browse(
                cr, uid, company_default_address['default']
                )

        if default_address['default']:
            address = partner_address_obj.browse(
                cr, uid, default_address['default']
                )

        today = datetime.datetime.today()
        company_partner = order.payer_company.partner_id
        partner_type = company_partner.tipo_pessoa == 'F' and 1 or 2

        file_data = {
            "controle_banco": int(order.payer_bank.bank_bic),
            #"controle_registro": 1,
            "cedente_inscricao_tipo": partner_type,
            "cedente_inscricao_numero": int(
                re.sub('[^0-9]', '', str(company_partner.cnpj_cpf))
                ),
            "cedente_convenio": order.agreement_number,
            "cedente_agencia": int(order.payer_bank.bra_number),
            "cedente_agencia_dv": order.payer_bank.bra_number_dig,
            "cedente_conta": int(order.payer_bank.acc_number),
            "cedente_conta_dv": order.payer_bank.acc_number_dig,
            "cedente_nome": order.payer_bank.owner_name,
            "nome_do_banco": order.payer_bank.bank_name,
            # FIXME: Fixo para remessa
            "arquivo_codigo":   1,
            "arquivo_data_de_geracao": int(today.strftime('%d%m%Y')),
            "arquivo_hora_de_geracao": int(today.strftime('%H%M%S')),
            "arquivo_sequencia": 0,
            "arquivo_layout": 84,
            "arquivo_densidade": 0,

            #"servico_operacao": 'C',
            "servico_servico": int(order.service_type),
            "servico_lancamento": int(order.type),
            #"servico_layout": ,
            'cedente_convenio_bb4': 'TS',
            }

        if company_address:
            cep, cep_complemento = company_address.zip.split('-')
            cep = int(re.sub('[^0-9]', '', cep))
            file_data.update({
                'endereco_logradouro': company_address.street,
                'endereco_numero': int(company_address.number),
                'endereco_complemento': company_address.street2,
                'endereco_bairro': company_address.district,
                'endereco_cep': cep,
                'endereco_cep_complemento': cep_complemento,
                'endereco_cidade': company_address.l10n_br_city_id.name,
                'endereco_uf': company_address.state_id.code,
                })

        arquivo = cnab240.tipos.Arquivo(
            bb, **file_data
            )
        lote = 1

        for line in order.payment_line:
            
            sequencial_registro_lote = 1
            
            p_type = order.recipient_partner.tipo_pessoa == 'F' and 1 or 2
            
            data = {
                'favorecido_banco': int(order.recipient_bank.bank_bic),
                'favorecido_agencia': int(order.recipient_bank.bra_number),
                'favorecido_agencia_dv': order.recipient_bank.bra_number_dig,
                'favorecido_conta': int(order.recipient_bank.acc_number),
                'favorecido_conta_dv': order.recipient_bank.acc_number_dig,
                'favorecido_inscricao_tipo': p_type,
                'favorecido_inscricao_numero': int(
                    re.sub('[^0-9]', '', str(order.recipient_partner.cnpj_cpf))
                    ),
                'favorecido_nome': order.recipient_partner.name,
                'favorecido_aviso': 0,
                'carteira_numero': int(line.wallet),
                'numero_documento': line.document_number,
                'vencimento_titulo': line.expiration_date,
                'valor_titulo': decimal.Decimal(line.value),
                'especie_titulo': line.type,
                'aceite_titulo': line.acceptance,
                'data_emissao_titulo': line.emission_date,
                'juros_mora_taxa_dia': decimal.Decimal(line.daily_interest),
                'valor_abatimento': line.discount_value,
                'identificacao_titulo': line.description,
                'codigo_protesto': line.protest,
                'prazo_protesto': line.protest_time,
                'codigo_baixa': line.devolution,
                'prazo_baixa': line.devolution_time,
                'controle_lote': lote,
                'lote_servico': lote,
                'sequencial_registro_lote': sequencial_registro_lote,
                'tipo_movimento': int(line.action),
                }

            if order.type == '03':
                if line.value <= 4999.99:
                    codigo_camara_centralizadora = 700
                else:
                    codigo_camara_centralizadora = 18
            elif order.type in ('41', '43'):
                codigo_camara_centralizadora = 18
            else:
                codigo_camara_centralizadora = 0

            codigo_instrucao_movimento = line.action == '0' and 0 or 99

            data.update({
                # Segmento A
                'codigo_instrucao_movimento': codigo_instrucao_movimento,

                'codigo_camara_centralizadora': codigo_camara_centralizadora,
                'documento_atribuido_empresa': line.document_number,

                'data_pagamento': 0,
                'tipo_moeda': 'BRL',
                'valor_pagamento': 0,
                'outras_informacoes': '0' * 39,
                'complemento_tipo_servico': '',
                'finalidade_ted': '',
                'complemente_finalidade_pagamento': '',

                # Segmento C
                # TODO: Registros não tratado atualmente pelo Banco do Brasil
                'valor_ir': 0,
                'valor_iss': 0,
                'valor_iof': 0,
                'valor_outras_deducoes': 0,
                'valor_outros_acrescimos': 0,
                'valor_inss': 0,
                })

            if address:
                cep, cep_complemento = address.zip.split('-')
                cep = int(re.sub('[^0-9]', '', cep))
                data.update({
                    'favorecido_endereco': address.street,
                    'favorecido_endereco_bairro': address.district,
                    'favorecido_endereco_cep': cep,
                    'favorecido_endereco_cep_complemento': cep_complemento,
                    'favorecido_endereco_cidade': address.l10n_br_city_id.name,
                    'favorecido_endereco_uf': address.state_id.code,
                    })
                
            arquivo.incluir_pagamento(order.service_type, **data)
            sequencial_registro_lote += 1

        encoded_data = arquivo._remover_acentos().encode("base64")
        self.write(cr, uid, ids, {
            'file': encoded_data,
            'file_name': 'cnab240.txt',
            },
            context=context)


payment()
