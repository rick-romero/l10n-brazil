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

class res_company(osv.osv):
    _inherit = 'res.company'
    _columns = {
        'natureza_juridica_id': fields.many2one(
            'l10n_br.natureza_juridica', u'Natureza Jurídica', required=True
            ),
        'porte_id': fields.many2one('l10n_br.porte', u'Porte', required=True),
        'optante_simples_nacional': fields.boolean(
            u'Optante pelo Simples Nacional'
            ),
        'participa_pat': fields.boolean(
            u'Participa do Programa de Alimentação do Trabalhador (PAT)'
            ),
        'responsavel_legal_id': fields.many2one(
            'res.partner', u'Responsável Legal', required=True,
            ),
        }
