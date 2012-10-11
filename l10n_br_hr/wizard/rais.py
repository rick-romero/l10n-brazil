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
                data = int(re.sub('[^0-9]', '', data))

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
        'company_id': fields.many2one('res.company', u'Empresa',
                                      required=True),
        }
    _defaults = {
        'state': 'init',
        }

    def generate_file(self, cr, uid, ids, context=None):

        lines = []
        type0 = line()
        type1 = line()
        type2 = line()
        type9 = line()

        partner_obj = self.pool.get('res.partner')
        address_obj = self.pool.get('res.partner.address')

        r = self.browse(cr, uid, ids[0])
        company = r.company_id
        company_partner = partner_obj.browse(cr, uid,
                                             company.partner_id.id,
                                             context=context)
        responsible = partner_obj.browse(cr, uid,
                                         company.responsavel_legal_id.id,
                                         context=context)

        seq = 1
        
        print responsible.address

        if not company.cnpj:
            message = u'A empresa deve possuir CNPJ cadastrado'
            state = 'init'
            raise osv.except_osv(_('Error'), message)

        elif not responsible.cnpj_cpf:
            message = u'O responsável legal pela empresa não possui CPF ou CNPJ cadastrado'
            state = 'init'
            raise osv.except_osv(_('Error'), message)

        else:
            print company.cnpj
            print responsible.cnpj_cpf

            # 001 a 006  06  Número   Sequencial do registro no arquivo
            type0.write_num(seq, 6)
            # 007 a 020  14  Número   Inscrição CNPJ/CEI do 1º estabelecimento do arquivo
            type0.write_str(re.sub('[^0-9]', '', company.cnpj))
            # TODO: 021 a 022  02  Alfanum  Prefixo do 1º estabelecimento do arquivo
            type0.write_str('00')
            # 023 a 023  01  Número   Tipo do registro = 0
            type0.write_num(0, 1)
            # 024 a 024  01  Número   Constante = 1
            type0.write_num(1, 1)
            # 025 a 038  14  Número   CNPJ/CEI/CPF do responsável
            type0.write_str(re.sub('[^0-9]', '', responsible.cnpj_cpf))
            # 039 a 039  01  Número   Tipo de Inscrição do responsável
            #                         1 - CNPJ
            #                         3 - CEI
            #                         4 - CPF
            if responsible.tipo_pessoa == 'J':
                type0.write_str('1')
            else:
                type0.write_num(4, 1)

            # 040 a 079  40  Alfanum  Razão Social/ Nome do responsável
            type0.write_str(company.legal_name, 40)

            if responsible.address:
                responsible_address = responsible.address[0]
                # 080 a 119  40  Alfanum  Logradouro do responsável
                type0.write_str(responsible_address.street, 40)
                # 120 a 125  06  Número   Número
                type0.write_num(int(responsible_address.number), 6)
                # 126 a 146  21  Alfanum  Complemento
                type0.write_str(responsible_address.street2, 21)
                # 147 a 165  19  Alfanum  Bairro
                type0.write_str(responsible_address.district, 19)
                # 166 a 173  08  Número   CEP
                type0.write_str(re.sub('[^0-9]', '', str(responsible_address.zip)))
                # 174 a 180  07  Número   Código do Município
                print responsible_address.l10n_br_city_id.ibge_code
                type0.write_num(responsible_address.l10n_br_city_id.ibge_code, 7)
                # 181 a 210  30  Alfanum  Nome do Município
                type0.write_str(responsible_address.l10n_br_city_id.name, 30)
                # 211 a 212  02  Alfa Sigla da UF
                type0.write_str(responsible_address.l10n_br_city_id.state_id.code, 2)
                
                if responsible_address.phone:
                    phone = re.sub('[^0-9]', '', str(responsible_address.phone))
                    # 213 a 214  02  Número   Telefone/Fax para contato (Código DDD)
                    type0.write_str(phone, 2)
                    # 215 a 222  08  Número   Telefone/Fax para contato (Número)
                    type0.write_str(phone[2:], 8)
                else:
                    type0.write_str('', 10)

            else:
                # 080 a 222 143  Alfanum  Espaços
                type0.write_str('', 143)

            # 223 a 223  01  Número   Indicador de retificação da declaração
            #                         1 - retifica os estabelecimentos entregues anteriormente
            #                         2 - a declaração não é retificação (é primeira entrega)
            # 224 a 231  08  Número   Data da retificação dos estabelecimentos (ddmmaaaa)
            # 232 a 239  08  Número   Data de geração do arquivo (ddmmaaaa)
            # 240 a 284  45  Alfanum  E-mail do responsável
            # 285 a 336  52  Alfanum  Nome do Responsável
            type0.write_str(responsible.name, 52)
            # 337 a 356  20  Alfanum Espaços
            type0.write_str('', 20)
            # 357 a 360  04  Número   Constante = 0551
            type0.write_num(551, 4)
            # 361 a 371  11  Número   CPF do responsável
            type0.write_str('', 11)
            # 372 a 383  12  Número   CREA a ser retificado
            # 384 a 391  08  Numero   Data de nascimento do responsável (ddmmaaaa)


            # 392 a 551 160  Alfanum  Espaços
            type0.write_str('', 160)


            lines.append(type0)
            lines.append(type1)
            lines.append(type2)
            lines.append(type9)

            print lines
            file_content = '\n'.join([l.content for l in lines])
            print file_content

            message = u'Arquivo gerado com sucesso'
            state = 'done'

        '''
        self.write(cr, uid, ids, {
            'state': state,
            'message': message,
            })
        '''

rais()
