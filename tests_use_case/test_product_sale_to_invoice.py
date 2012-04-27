from workflow.wkf_service import workflow_service


def test_product_sale_to_invoice_nfe(oerp):
    """ create an invoice from a product sale order with NFE fiscal
    document.
        taxes in this invoice are:
            COFINS 0,74% Incluso
            CSLL 0,21% Incluso
            INSS 1,80% Incluso
            ICMS 1,25% Incluso
            IPI 5,00% Adicionado

    """
    #create empty fiscal classification for the product
    prod_fc_obj = oerp.pool.get('account.product.fiscal.classification')
    prod_fc_id = prod_fc_obj.create(oerp.cr, 1, {
        'name': 'isento',
        'description': 'isento'
        })

    assert prod_fc_obj.browse(oerp.cr, 1, [prod_fc_id])[0].id == prod_fc_id

    # create product fiscal operation category
    cfop_obj = oerp.pool.get('l10n_br_account.cfop')
    cfop_id = cfop_obj.search(oerp.cr, 1, [])[0]
    fiscal_doc_obj = oerp.pool.get('l10n_br_account.fiscal.document')
    fiscal_doc_id = fiscal_doc_obj.search(oerp.cr, 1, [('nfe', '=', True)])[0]

    fopc_obj = oerp.pool.get('l10n_br_account.fiscal.operation.category')
    fopc_id = fopc_obj.create(oerp.cr, 1, {
        'code': 'produtos',
        'name': 'produtos',
        'type': 'output',
        'use_sale': True,
        'use_invoice': True,
        'fiscal_type': 'product'
        })

    assert fopc_obj.browse(oerp.cr, 1, [fopc_id])[0].id == fopc_id

    # create product fiscal operation
    fop_obj = oerp.pool.get('l10n_br_account.fiscal.operation')
    fop_id = fop_obj.create(oerp.cr, 1, {
        'code': 'produto01',
        'name': 'produto01',
        'type': 'output',
        'fiscal_operation_category_id': fopc_id,
        'cfop_id': cfop_id,
        'fiscal_document_id': fiscal_doc_id,
        'use_sale': True,
        'use_invoice': True,
        'fiscal_type': 'product'
        })

    assert fop_obj.browse(oerp.cr, 1, [fop_id])[0].id == fop_id

    # create product template
    prod_obj = oerp.pool.get('product.product')
    prod_tpl_obj = oerp.pool.get('product.template')

    prod_tpl_id = prod_tpl_obj.create(oerp.cr, 1, {
        'supply_method': 'buy',
        'standard_price': 1.00,
        'list_price': 100.00,
        'mes_type': 'fixed',
        'name': 'product test',
        'uom_po_id': 1,
        'type': 'product',
        'procure_method': 'make_to_stock',
        'cost_method': 'standard',
        'categ_id': 1
        })

    assert prod_tpl_obj.browse(oerp.cr, 1, [prod_tpl_id])[0].id == prod_tpl_id

    # create product obj
    prod_id = prod_obj.create(oerp.cr, 1, {
        'product_tmpl_id': prod_tpl_id,
        'valuation': 'manual_periodic',
        'default_code': '123'
        })

    assert prod_obj.browse(oerp.cr, 1, [prod_id])[0].id == prod_id

    # create COFINS tax code with tax_include
    tax_code_obj = oerp.pool.get('account.tax.code')
    tax_code_cofins_id = tax_code_obj.create(oerp.cr, 1, {
        'name': 'COFINS_test',
        'company_id': 1,
        'sign': 1,
        'tax_discount': True,
        'tax_include': True,
        'notprintable': True,
        'domain': 'cofins_test'
        })

    assert tax_code_obj.browse(oerp.cr, 1, [tax_code_cofins_id])[0].id == tax_code_cofins_id

    # create CSLL tax code with tax_include
    tax_code_obj = oerp.pool.get('account.tax.code')
    tax_code_csll_id = tax_code_obj.create(oerp.cr, 1, {
        'name': 'CSLL_test',
        'company_id': 1,
        'sign': 1,
        'tax_discount': True,
        'tax_include': True,
        'notprintable': True,
        'domain': 'csll_test'
        })

    assert tax_code_obj.browse(oerp.cr, 1, [tax_code_csll_id])[0].id == tax_code_csll_id

    # create INSS tax code with tax_include
    tax_code_obj = oerp.pool.get('account.tax.code')
    tax_code_inss_id = tax_code_obj.create(oerp.cr, 1, {
        'name': 'INSS_test',
        'company_id': 1,
        'sign': 1,
        'tax_discount': True,
        'tax_include': True,
        'notprintable': True,
        'domain': 'inss_test'
        })

    assert tax_code_obj.browse(oerp.cr, 1, [tax_code_inss_id])[0].id == tax_code_inss_id

    # create ICMS tax code with tax_include
    tax_code_obj = oerp.pool.get('account.tax.code')
    tax_code_icms_id = tax_code_obj.create(oerp.cr, 1, {
        'name': 'ICMS_test',
        'company_id': 1,
        'sign': 1,
        'tax_discount': True,
        'tax_include': True,
        'notprintable': False,
        'domain': 'icms_test'
        })

    assert tax_code_obj.browse(oerp.cr, 1, [tax_code_icms_id])[0].id == tax_code_icms_id

    # create IPI tax code with tax_include
    tax_code_obj = oerp.pool.get('account.tax.code')
    tax_code_ipi_id = tax_code_obj.create(oerp.cr, 1, {
        'name': 'IPI_test',
        'company_id': 1,
        'sign': 1,
        'tax_discount': True,
        'tax_include': False,
        'notprintable': False,
        'domain': 'ipi_test'
        })

    assert tax_code_obj.browse(oerp.cr, 1, [tax_code_icms_id])[0].id == tax_code_icms_id

    # create CSLL 0,21% tax with type tax_include
    sale_order_taxes = []

    tax_obj = oerp.pool.get('account.tax')
    tax_csll_id = tax_obj.create(oerp.cr, 1, {
        'sequence': '1',
        'type_tax_use': 'all',
        'applicable_type': 'true',
        'company_id': 1,
        'name': 'CSLL 0,21% Recolhe_test',
        'amount': 0.0021,
        'type': 'percent',
        'tax_code_id': tax_code_csll_id,
        'base_reduction': 0.0000,
        'amount_mva': 0.0000,
        'price_include': False,
        'tax_discount': True,
        'tax_add': False,
        'tax_include': True,
        'tax_retain': False,
        'domain': 'csll_test',
        })

    assert tax_obj.browse(oerp.cr, 1, [tax_csll_id])[0].id == tax_csll_id
    sale_order_taxes.append(tax_csll_id)

    # create COFINS 0,74% tax with type tax_include
    tax_obj = oerp.pool.get('account.tax')
    tax_cofins_id = tax_obj.create(oerp.cr, 1, {
        'sequence': '1',
        'type_tax_use': 'all',
        'applicable_type': 'true',
        'company_id': 1,
        'name': 'COFINS 0,74% Recolhe_test',
        'amount': 0.0074,
        'type': 'percent',
        'tax_code_id': tax_code_cofins_id,
        'base_reduction': 0.0000,
        'amount_mva': 0.0000,
        'price_include': False,
        'tax_discount': True,
        'tax_add': False,
        'tax_include': True,
        'tax_retain': False,
        'domain': 'cofins_test',
        })

    assert tax_obj.browse(oerp.cr, 1, [tax_cofins_id])[0].id == tax_cofins_id
    sale_order_taxes.append(tax_cofins_id)

    # create INSS 1,80% tax with type tax_include
    tax_obj = oerp.pool.get('account.tax')
    tax_inss_id = tax_obj.create(oerp.cr, 1, {
        'sequence': '1',
        'type_tax_use': 'all',
        'applicable_type': 'true',
        'company_id': 1,
        'name': 'INSS 1,80% Recolhe_test',
        'amount': 0.0180,
        'type': 'percent',
        'tax_code_id': tax_code_inss_id,
        'base_reduction': 0.0000,
        'amount_mva': 0.0000,
        'price_include': False,
        'tax_discount': True,
        'tax_add': False,
        'tax_include': True,
        'tax_retain': False,
        'domain': 'inss_test',
        })

    assert tax_obj.browse(oerp.cr, 1, [tax_inss_id])[0].id == tax_inss_id
    sale_order_taxes.append(tax_inss_id)

    # create ICMS 1,25% tax with type tax_include
    tax_obj = oerp.pool.get('account.tax')
    tax_icms_id = tax_obj.create(oerp.cr, 1, {
        'sequence': '1',
        'type_tax_use': 'all',
        'applicable_type': 'true',
        'company_id': 1,
        'name': 'ICMS 1,25% Recolhe_test',
        'amount': 0.0125,
        'type': 'percent',
        'tax_code_id': tax_code_icms_id,
        'base_reduction': 0.0000,
        'amount_mva': 0.0000,
        'price_include': False,
        'tax_discount': True,
        'tax_add': False,
        'tax_include': True,
        'tax_retain': False,
        'domain': 'icms_test',
        })

    assert tax_obj.browse(oerp.cr, 1, [tax_icms_id])[0].id == tax_icms_id
    sale_order_taxes.append(tax_icms_id)

    # create IPI 5% tax with type tax_include
    tax_obj = oerp.pool.get('account.tax')
    tax_ipi_id = tax_obj.create(oerp.cr, 1, {
        'sequence': '1',
        'type_tax_use': 'all',
        'applicable_type': 'true',
        'company_id': 1,
        'name': 'IPI 5% Recolhe_test',
        'amount': 0.0500,
        'type': 'percent',
        'tax_code_id': tax_code_ipi_id,
        'base_reduction': 0.0000,
        'amount_mva': 0.0000,
        'price_include': False,
        'tax_discount': True,
        'tax_add': True,
        'tax_include': False,
        'tax_retain': False,
        'domain': 'ipi_test',
        })

    assert tax_obj.browse(oerp.cr, 1, [tax_ipi_id])[0].id == tax_ipi_id
    sale_order_taxes.append(tax_ipi_id)

    # update company data
    partner_obj = oerp.pool.get('res.partner')
    partner_address_obj = oerp.pool.get('res.partner.address')

    partner_obj.write(oerp.cr, 1, 1, {
        'name': 'emp teste',
        'tipo_pessoa': 'J',
        'legal_name': 'emp teste',
        'cnpj_cpf': '10.965.392/0001-87',
        'partner_fiscal_type_id': 1
        })

    partner_address_obj.write(oerp.cr, 1, 1, {
        'phone': '5130850096',
        'street': 'av abc',
        'active': True,
        'partner_id': 1,
        'city': 'poa',
        'name': 'Vinicius',
        'country_id': 29,
        'type': 'default',
        'email': 'proge@proge.com.br',
        'state_id': 1,
        'l10n_br_city_id': 4530,
        'number': 34,
        'district': 'abcd',
        'zip': 92500000
        })

    # create client partner
    partner_client_id = partner_obj.create(oerp.cr, 1, {
        'name': 'cliente teste',
        'tipo_pessoa': 'J',
        'legal_name': 'cliente teste',
        'cnpj_cpf': '45.225.081/0001-66',
        'partner_fiscal_type_id': 1
        })

    assert partner_obj.browse(oerp.cr, 1, [partner_client_id])[0].id == partner_client_id

    # create client partner address
    partner_client_address_id = partner_address_obj.create(oerp.cr, 1, {
        'phone': '5130850096',
        'street': 'av abc',
        'active': True,
        'partner_id': partner_client_id,
        'city': 'poa',
        'name': 'Carlos',
        'country_id': 29,
        'type': 'default',
        'email': 'proge@proge.com.br',
        'state_id': 1,
        'l10n_br_city_id': 4530,
        'number': 34,
        'district': 'abcd',
        'zip': 92500000
        })

    assert partner_address_obj.browse(oerp.cr, 1, [partner_client_address_id])[0].id == partner_client_address_id

    # create sale order with above data
    sale_order_obj = oerp.pool.get('sale.order')
    sale_order_line_obj = oerp.pool.get('sale.order.line')

    sale_order_lines = []

    prod = prod_obj.browse(oerp.cr, 1, [prod_id])[0]

    sol = {'name': prod.name,
            'product_uom_qty': 1,
            'product_id': prod.id,
            'product_uom': 1,
            'price_unit': prod.price_get('list_price')[prod.id]
            }

    sale_order_lines.append((0, 0, sol))

    order_id = sale_order_obj.create(oerp.cr, 1, {
        'user_id': 1,
        'partner_id': 1,
        'partner_order_id': partner_client_address_id,
        'partner_invoice_id': partner_client_address_id,
        'partner_shipping_id': partner_client_address_id,
        'pricelist_id': 1,
        'order_line': sale_order_lines,
        'fiscal_operation_category_id': fopc_id,
        'fiscal_operation_id': fop_id
        #'fiscal_position': 1
        })

    assert sale_order_obj.browse(oerp.cr, 1, [order_id])[0].id == order_id

    sol_id = sale_order_line_obj.search(oerp.cr, 1, [('order_id', '=', order_id)])[0]

    for tax_id in sale_order_taxes:
        oerp.cr.execute('insert into sale_order_tax (order_line_id,tax_id) values (%d,%d)' % (sol_id, int(tax_id)))

    assert len(sale_order_obj.browse(oerp.cr, 1, [order_id])[0].order_line[0].tax_id) == 5

    sale_order_name = sale_order_obj.browse(oerp.cr, 1, [order_id])[0].name

    wf_service = workflow_service()
    wf_service.trg_validate(1, 'sale.order', order_id, 'order_confirm', oerp.cr)
    assert sale_order_obj.browse(oerp.cr, 1, [order_id])[0].state == 'manual'

    # create_invoice with above sale order
    wf_service.trg_validate(1, 'sale.order', order_id, 'manual_invoice', oerp.cr)
    assert sale_order_obj.browse(oerp.cr, 1, [order_id])[0].state == 'progress'

    inv_obj = oerp.pool.get('account.invoice')
    inv_id = inv_obj.search(oerp.cr, 1, [('origin', '=', sale_order_name)])[0]
    invoice = inv_obj.browse(oerp.cr, 1, [inv_id])[0]

    assert invoice.origin == sale_order_name
    inv_taxes = invoice.invoice_line[0].invoice_line_tax_id
    assert len(inv_taxes) == 5
    assert invoice.amount_total == 105.0
    assert invoice.amount_untaxed == 100.0
    assert invoice.amount_tax == 5.00
    assert invoice.cfop_id.id == cfop_id
    assert invoice.fiscal_operation_category_id.id == fopc_id
    assert invoice.fiscal_operation_id.id == fop_id

    #confirm invoice
    wf_service.trg_validate(1, 'account.invoice', inv_id, 'invoice_sefaz_export', oerp.cr)

    # reload invoice to get new fields created by the action on the workflow
    invoice = inv_obj.browse(oerp.cr, 1, [inv_id])[0]

    move_line_obj = oerp.pool.get('account.move.line')
    move_lines = move_line_obj.search(oerp.cr, 1, [('move_id', '=', invoice.move_id.id)])
    assert len(move_lines) == 7

    move1 = move_line_obj.search(oerp.cr, 1, [('move_id', '=', invoice.move_id.id), ('debit', '=', 105)])[0]
    assert move_line_obj.browse(oerp.cr, 1, move1).debit == 105

    move2 = move_line_obj.search(oerp.cr, 1, [('move_id', '=', invoice.move_id.id), ('credit', '=', 0.21)])[0]
    assert move_line_obj.browse(oerp.cr, 1, move2).credit == 0.21

    move3 = move_line_obj.search(oerp.cr, 1, [('move_id', '=', invoice.move_id.id), ('credit', '=', 0.74)])[0]
    assert move_line_obj.browse(oerp.cr, 1, move3).credit == 0.74

    move4 = move_line_obj.search(oerp.cr, 1, [('move_id', '=', invoice.move_id.id), ('credit', '=', 1.80)])[0]
    assert move_line_obj.browse(oerp.cr, 1, move4).credit == 1.80

    move5 = move_line_obj.search(oerp.cr, 1, [('move_id', '=', invoice.move_id.id), ('credit', '=', 1.25)])[0]
    assert move_line_obj.browse(oerp.cr, 1, move5).credit == 1.25

    move6 = move_line_obj.search(oerp.cr, 1, [('move_id', '=', invoice.move_id.id), ('credit', '=', 5.00)])[0]
    assert move_line_obj.browse(oerp.cr, 1, move6).credit == 5

    move7 = move_line_obj.search(oerp.cr, 1, [('move_id', '=', invoice.move_id.id), ('credit', '=', 96)])[0]
    assert move_line_obj.browse(oerp.cr, 1, move7).credit == 96

    rec_ids = invoice._get_receivable_lines(inv_id, False, None)
    assert len(rec_ids) == 1

    rec_line = oerp.pool.get('account.move.line').browse(oerp.cr, 1, rec_ids[invoice.id])[0]
    assert rec_line.debit == 105
