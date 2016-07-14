import re
from openerp import models, fields, api, _
from openerp.addons.l10n_br_base.tools import fiscal
from openerp.exceptions import Warning


class PhoneCall(models.Model):
    """ Phone call """
    _inherit = "crm.phonecall"
    
    foto01 = fields.Binary(related='opportunity_id.foto01', string='Foto 01', readonly=True)
    foto02 = fields.Binary(related='opportunity_id.foto02', string='Foto 02', readonly=True)
    foto03 = fields.Binary(related='opportunity_id.foto03', string='Foto 03', readonly=True)
    
    comprador = fields.Char(related='opportunity_id.comprador', string='Comprador')
    novos_produtos = fields.Char(related='opportunity_id.novos_produtos', string='Autoriza Novos Produtos')
    comprador_melhor_horario = fields.Char(related='opportunity_id.comprador_melhor_horario', string='Comprador Melhor Horario')
    
    ja_compra = fields.Boolean(related='opportunity_id.ja_compra', string='Ja compra o produto')
    ja_compra_preco = fields.Float(related='opportunity_id.ja_compra_preco', string='Preco de compra')
    
    fq_price = fields.Integer(related='opportunity_id.fq_price', string='Preco FourSquare', readonly=True)
    fq_distance = fields.Char(related='opportunity_id.fq_distance', string='Distancia')
    fq_category = fields.Char(related='opportunity_id.fq_category', string='Categoria FourSquare')