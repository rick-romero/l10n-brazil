# -*- encoding: utf-8 -*-
###############################################################################
#                                                                             #
# Copyright (C) 2010-2012  Renato Lima (Akretion)                             #
#                                                                             #
#This program is free software: you can redistribute it and/or modify         #
#it under the terms of the GNU Affero General Public License as published by  #
#the Free Software Foundation, either version 3 of the License, or            #
#(at your option) any later version.                                          #
#                                                                             #
#This program is distributed in the hope that it will be useful,              #
#but WITHOUT ANY WARRANTY; without even the implied warranty of               #
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the                #
#GNU Affero General Public License for more details.                          #
#                                                                             #
#You should have received a copy of the GNU Affero General Public License     #
#along with this program.  If not, see <http://www.gnu.org/licenses/>.        #
###############################################################################

from openerp import api, models, fields


class ResPartner(models.Model):
    _inherit = 'res.partner'
    
    @api.multi
    def zip_search(self):
        obj_zip = self.env['l10n_br.zip']
        for res_partner in self:
            zip_ids = obj_zip.zip_search_multi(                
                country_id=res_partner.country_id.id,
                state_id=res_partner.state_id.id,
                l10n_br_city_id=res_partner.l10n_br_city_id.id,
                district=res_partner.district,
                street=res_partner.street,
                zip_code=res_partner.zip
            )

            obj_zip_result = self.env['l10n_br.zip.result']
            zip_data = obj_zip_result.map_to_zip_result(
                            zip_ids, self._name, res_partner.id)

            if len(zip_data) == 1: 
                result = obj_zip.set_result(zip_ids)
                res_partner.write(result)
                return True
            else:
                if len(zip_data) > 1:
                    return obj_zip.create_wizard(
                        self._name,
                        country_id=res_partner.country_id.id,
                        state_id=res_partner.state_id.id,
                        l10n_br_city_id=res_partner.l10n_br_city_id.id,
                        district=res_partner.district,
                        street=res_partner.street,
                        zip_code=res_partner.zip,
                        zip_ids=zip_ids
                    )
                else:
                    return True
