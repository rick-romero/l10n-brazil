

def test_create_sale_order(oerp):
    """ create an Sale Order.
        Modules required:
            l10n_br, l10n_br_sale

    """
    sale_order_obj = oerp.pool.get('sale.order')
    product_obj = oerp.pool.get('product.product')

    sale_order_lines = []

    cfop_obj = oerp.pool.get('l10n_br_account.cfop')
    cfop_id = cfop_obj.search(oerp.cr, 1, [])[0]
    fiscal_doc_obj = oerp.pool.get('l10n_br_account.fiscal.document')
    fiscal_doc_id = fiscal_doc_obj.search(oerp.cr, 1, [('nfe', '=', 'TRUE')])[0]

    fopc_obj = oerp.pool.get('l10n_br_account.fiscal.operation.category')
    fopc_id = fopc_obj.create(oerp.cr, 1, {
        'code': 'isento',
        'name': 'isento',
        'type': 'output',
        'use_sale': 'TRUE',
        'use_invoice': 'TRUE',
        'fiscal_type': 'product'
        })

    assert fopc_obj.browse(oerp.cr, 1, [fopc_id])[0].id == fopc_id

    # create service template
    prod_obj = oerp.pool.get('product.product')
    prod_tpl_obj = oerp.pool.get('product.template')

    prod_tpl_id = prod_tpl_obj.create(oerp.cr, 1, {
        'supply_method': 'buy',
        'standard_price': 1.00,
        'list_price': 100.00,
        'mes_type': 'fixed',
        'name': 'service test',
        'uom_po_id': 1,
        'type': 'service',
        'procure_method': 'make_to_stock',
        'cost_method': 'standard',
        'categ_id': 1
        })

    assert prod_tpl_obj.browse(oerp.cr, 1, [prod_tpl_id])[0].id == prod_tpl_id

    # create service obj
    prod_id = prod_obj.create(oerp.cr, 1, {
        'product_tmpl_id': prod_tpl_id,
        'valuation': 'manual_periodic'
        })

    assert prod_obj.browse(oerp.cr, 1, [prod_id])[0].id == prod_id

    prod1 = prod_obj.browse(oerp.cr, 1, [prod_id])[0]

    sol = {'name': prod1.name,
            'product_uom_qty': 1,
            'product_id': prod1.id,
            'product_uom': 1,
            'price_unit': prod1.price_get('list_price')[prod1.id]
            }

    #sol_new = sale_order_line_obj.product_id_change(oerp.cr, 1, None, 1, 0, 1, 1,name=prod1.name, partner_id=1,fiscal_position=fp1)['value']

    sale_order_lines.append((0, 0, sol))

    order_id = sale_order_obj.create(oerp.cr, 1, {
        'user_id': 1,
        'partner_id': 1,
        'partner_order_id': 1,
        'partner_invoice_id': 1,
        'partner_shipping_id': 1,
        'pricelist_id': 1,
        'order_line': sale_order_lines,
        'fiscal_operation_category_id': fopc_id
        #'fiscal_position': 1
        })

    assert sale_order_obj.browse(oerp.cr, 1, [order_id])[0].id == order_id
