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
import datetime


class hr_payslip(osv.osv):
    _inherit = 'hr.payslip'
    _columns = {
        'base_calculo_previdencia': fields.float(
            u'Base de Cálculo da Previdência Social',
            size=16,
            digits=(13, 2),
            ),
        }

    def pre_compute_sheet(self, cr, uid, ids, context=None):
        payslip_line_obj = self.pool.get('hr.payslip.line')

        for payslip in self.browse(cr, uid, ids, context):

            gross = 0

            p_line_ids = payslip_line_obj.search(cr, uid, [
                    ('slip_id', '=', payslip.id),
                    ('code', '=', 'GROSS'),
                ], context=context)

            if p_line_ids:
                p_lines = payslip_line_obj.browse(
                    cr, uid, p_line_ids, context=context
                    )

                for l in p_lines:
                    gross += l.total

            self.write(cr, uid, payslip.id, {
                'base_calculo_previdencia': gross
                }, context)

        return self.compute_sheet(cr, uid, ids, context)


hr_payslip()
