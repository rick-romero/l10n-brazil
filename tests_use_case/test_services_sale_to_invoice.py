from workflow.wkf_service import workflow_service


def test_services_sale_to_invoice(oerp):
    """ create an invoice from a service sale order with one retained tax
        taxes in this invoice are:
            IR 1,5 Retido
            ISS 2% Recolhido
            COFINS 3% Recolhido
            PIS 0,65% Recolhido
            CSLL 2,88% Recolhido
            IR 3,3% Recolhido
        Confs required:
             Brazilian chart of accounts generated;
        Modules required:
            l10n_br, l10n_br_account, l10n_br_sale, l10n_br_product

    """
    #create empty fiscal classification for the service
    prod_fc_obj = oerp.pool.get('account.product.fiscal.classification')
    prod_fc_id = prod_fc_obj.create(oerp.cr, 1, {
        'name': 'isento',
        'description': 'isento'
        })

    assert prod_fc_obj.browse(oerp.cr, 1, [prod_fc_id])[0].id == prod_fc_id

    # create account journal
    acc_journal_obj = oerp.pool.get('account.journal')
    acc_journal_id = acc_journal_obj.create(oerp.cr, 1, {
        'code': 'bco',
        'name': 'bco',
        'view_id': 3,
        'sequence_id': 1,
        'company_id': 1,
        'revenue_expense': True,
        'type': 'cash'
        })

    assert acc_journal_obj.browse(oerp.cr, 1, [acc_journal_id])[0].id == acc_journal_id

    # create fiscal document serie
    fiscal_doc_obj = oerp.pool.get('l10n_br_account.fiscal.document')
    doc_serie_obj = oerp.pool.get('l10n_br_account.document.serie')
    ir_seq_obj = oerp.pool.get('ir.sequence')

    fiscal_doc_id = fiscal_doc_obj.search(oerp.cr, 1, [('nfe', '=', False)])[0]
    ir_seq_id = ir_seq_obj.search(oerp.cr, 1, [('code', '=', 'sale.order')])[0]
    
    doc_serie_id = doc_serie_obj.create(oerp.cr, 1, {
        'code': 'serie_nfe_pytest',
        'name': 'serie_nfe_pytest',
        'internal_sequence_id': ir_seq_id,
        'active': True,
        'fiscal_document_id': fiscal_doc_id,
        'company_id': 1,
        'fiscal_type': 'service'
        })

    # create service fiscal operation category
    fopc_obj = oerp.pool.get('l10n_br_account.fiscal.operation.category')
    fopc_id = fopc_obj.create(oerp.cr, 1, {
        'code': 'servicos',
        'name': 'servicos',
        'type': 'output',
        'use_sale': True,
        'use_invoice': True,
        'fiscal_type': 'service'
        })

    assert fopc_obj.browse(oerp.cr, 1, [fopc_id])[0].id == fopc_id

    oerp.cr.execute('insert into l10n_br_account_fiscal_operation_category_rel (fiscal_operation_category_id,journal_id) values (%s, %s)' % (fopc_id, acc_journal_id))

    # create service fiscal operation
    fop_obj = oerp.pool.get('l10n_br_account.fiscal.operation')
    fop_id = fop_obj.create(oerp.cr, 1, {
        'code': 'servico01',
        'name': 'servico01',
        'type': 'output',
        'fiscal_operation_category_id': fopc_id,
        'fiscal_document_id': fiscal_doc_id,
        'use_sale': True,
        'use_invoice': True,
        'fiscal_type': 'service'
        })

    assert fop_obj.browse(oerp.cr, 1, [fop_id])[0].id == fop_id

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
        'property_account_income': 1193,
        'property_account_expense': 669,
        'property_fiscal_classification': prod_fc_id,
        'procure_method': 'make_to_stock',
        'cost_method': 'standard',
        'categ_id': 1
        })

    assert prod_tpl_obj.browse(oerp.cr, 1, [prod_tpl_id])[0].id == prod_tpl_id

    # create service obj
    prod_id = prod_obj.create(oerp.cr, 1, {
        'product_tmpl_id': prod_tpl_id,
        'valuation': 'manual_periodic',
        'default_code': '123'
        })

    assert prod_obj.browse(oerp.cr, 1, [prod_id])[0].id == prod_id

    # create ISS tax code with tax_include
    tax_code_obj = oerp.pool.get('account.tax.code')
    tax_code_iss_id = tax_code_obj.create(oerp.cr, 1, {
        'name': 'ISS_test',
        'company_id': 1,
        'sign': 1,
        'tax_discount': True,
        'tax_include': True,
        'notprintable': True,
        'domain': 'iss_test'
        })

    assert tax_code_obj.browse(oerp.cr, 1, [tax_code_iss_id])[0].id == tax_code_iss_id

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

    # create PIS tax code with tax_include
    tax_code_obj = oerp.pool.get('account.tax.code')
    tax_code_pis_id = tax_code_obj.create(oerp.cr, 1, {
        'name': 'PIS_test',
        'company_id': 1,
        'sign': 1,
        'tax_discount': True,
        'tax_include': True,
        'notprintable': True,
        'domain': 'pis_test'
        })

    assert tax_code_obj.browse(oerp.cr, 1, [tax_code_pis_id])[0].id == tax_code_pis_id

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

    # create IR tax code with tax_include
    tax_code_obj = oerp.pool.get('account.tax.code')
    tax_code_ir_id = tax_code_obj.create(oerp.cr, 1, {
        'name': 'IR_test',
        'company_id': 1,
        'sign': 1,
        'tax_discount': True,
        'tax_include': True,
        'notprintable': True,
        'domain': 'ir_test'
        })

    assert tax_code_obj.browse(oerp.cr, 1, [tax_code_ir_id])[0].id == tax_code_ir_id

    # create IR Retido tax code with tax_include
    tax_code_obj = oerp.pool.get('account.tax.code')
    tax_code_ir_retido_id = tax_code_obj.create(oerp.cr, 1, {
        'name': 'IR Retido_test',
        'company_id': 1,
        'sign': 1,
        'tax_discount': True,
        'tax_include': False,
        'notprintable': False,
        'domain': 'ir_retido_test'
        })

    assert tax_code_obj.browse(oerp.cr, 1, [tax_code_ir_retido_id])[0].id == tax_code_ir_retido_id

    # create ISS 2% tax with type tax_include
    sale_order_taxes = []

    tax_obj = oerp.pool.get('account.tax')
    tax_iss_id = tax_obj.create(oerp.cr, 1, {
        'sequence': '1',
        'type_tax_use': 'all',
        'applicable_type': 'true',
        'company_id': 1,
        'name': 'ISS 2% Recolhe_test',
        'amount': 0.0200,
        'type': 'percent',
        'tax_code_id': tax_code_iss_id,
        'base_reduction': 0.0000,
        'amount_mva': 0.0000,
        'price_include': False,
        'tax_discount': True,
        'tax_add': False,
        'tax_include': True,
        'tax_retain': False,
        'domain': 'iss_test',
        })

    assert tax_obj.browse(oerp.cr, 1, [tax_iss_id])[0].id == tax_iss_id
    sale_order_taxes.append(tax_iss_id)

    # create COFINS 3% tax with type tax_include
    tax_obj = oerp.pool.get('account.tax')
    tax_cofins_id = tax_obj.create(oerp.cr, 1, {
        'sequence': '1',
        'type_tax_use': 'all',
        'applicable_type': 'true',
        'company_id': 1,
        'name': 'COFINS 3% Recolhe_test',
        'amount': 0.0300,
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

    # create PIS 0,65% tax with type tax_include
    tax_obj = oerp.pool.get('account.tax')
    tax_pis_id = tax_obj.create(oerp.cr, 1, {
        'sequence': '1',
        'type_tax_use': 'all',
        'applicable_type': 'true',
        'company_id': 1,
        'name': 'PIS 0,65% Recolhe_test',
        'amount': 0.0065,
        'type': 'percent',
        'tax_code_id': tax_code_pis_id,
        'base_reduction': 0.0000,
        'amount_mva': 0.0000,
        'price_include': False,
        'tax_discount': True,
        'tax_add': False,
        'tax_include': True,
        'tax_retain': False,
        'domain': 'pis_test',
        })

    assert tax_obj.browse(oerp.cr, 1, [tax_pis_id])[0].id == tax_pis_id
    sale_order_taxes.append(tax_pis_id)

    # create CSLL 2,88% tax with type tax_include
    tax_obj = oerp.pool.get('account.tax')
    tax_csll_id = tax_obj.create(oerp.cr, 1, {
        'sequence': '1',
        'type_tax_use': 'all',
        'applicable_type': 'true',
        'company_id': 1,
        'name': 'CSLL 2,88% Recolhe_test',
        'amount': 0.0288,
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

    # create IR 3,3% tax with type tax_include
    tax_obj = oerp.pool.get('account.tax')
    tax_ir_id = tax_obj.create(oerp.cr, 1, {
        'sequence': '1',
        'type_tax_use': 'all',
        'applicable_type': 'true',
        'company_id': 1,
        'name': 'IR 3,3% Recolhe_test',
        'amount': 0.0330,
        'type': 'percent',
        'tax_code_id': tax_code_ir_id,
        'base_reduction': 0.0000,
        'amount_mva': 0.0000,
        'price_include': False,
        'tax_discount': True,
        'tax_add': False,
        'tax_include': True,
        'tax_retain': False,
        'domain': 'ir_test',
        })

    assert tax_obj.browse(oerp.cr, 1, [tax_ir_id])[0].id == tax_ir_id
    sale_order_taxes.append(tax_ir_id)

    # create IR 1,5% Retido tax with type tax_include
    tax_obj = oerp.pool.get('account.tax')
    tax_ir_retido_id = tax_obj.create(oerp.cr, 1, {
        'sequence': '1',
        'type_tax_use': 'all',
        'applicable_type': 'true',
        'company_id': 1,
        'name': 'IR 1,5% Retido_test',
        'amount': 0.0150,
        'type': 'percent',
        'tax_code_id': tax_code_ir_retido_id,
        'base_reduction': 0.0000,
        'amount_mva': 0.0000,
        'price_include': False,
        'tax_discount': True,
        'tax_add': False,
        'tax_include': False,
        'tax_retain': True,
        'domain': 'ir_retido_test',
        })

    assert tax_obj.browse(oerp.cr, 1, [tax_ir_retido_id])[0].id == tax_ir_retido_id
    sale_order_taxes.append(tax_ir_retido_id)

    # create client partner
    partner_client_obj = oerp.pool.get('res.partner')
    partner_client_id = partner_client_obj.create(oerp.cr, 1, {
        'name': 'cliente teste',
        'tipo_pessoa': 'J',
        'legal_name': 'cliente teste',
        'cnpj_cpf': '45.225.081/0001-66',
        'partner_fiscal_type_id': 1
        })

    assert partner_client_obj.browse(oerp.cr, 1, [partner_client_id])[0].id == partner_client_id

    # create client partner address
    partner_client_address_obj = oerp.pool.get('res.partner.address')
    partner_client_address_id = partner_client_address_obj.create(oerp.cr, 1, {
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

    assert partner_client_address_obj.browse(oerp.cr, 1, [partner_client_address_id])[0].id == partner_client_address_id

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

    assert len(sale_order_obj.browse(oerp.cr, 1, [order_id])[0].order_line[0].tax_id) == 6

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
    assert len(inv_taxes) == 6
    assert invoice.amount_total == 98.5
    assert invoice.amount_untaxed == 100.0
    assert invoice.amount_tax == -1.5

    #confirm invoice
    wf_service.trg_validate(1, 'account.invoice', inv_id, 'invoice_validate', oerp.cr)

    # reload invoice to get new fields created by the action on the workflow
    invoice = inv_obj.browse(oerp.cr, 1, [inv_id])[0]

    move_line_obj = oerp.pool.get('account.move.line')
    move_lines = move_line_obj.search(oerp.cr, 1, [('move_id', '=', invoice.move_id.id)])
    assert len(move_lines) == 9

    move1 = move_line_obj.search(oerp.cr, 1, [('move_id', '=', invoice.move_id.id), ('debit', '=', 98.5)])[0]
    assert move_line_obj.browse(oerp.cr, 1, move1).debit == 98.5

    move2 = move_line_obj.search(oerp.cr, 1, [('move_id', '=', invoice.move_id.id), ('debit', '=', 1.50)])[0]
    assert move_line_obj.browse(oerp.cr, 1, move2).debit == 1.50

    move3 = move_line_obj.search(oerp.cr, 1, [('move_id', '=', invoice.move_id.id), ('credit', '=', 1.50)])[0]
    assert move_line_obj.browse(oerp.cr, 1, move3).credit == 1.50

    move4 = move_line_obj.search(oerp.cr, 1, [('move_id', '=', invoice.move_id.id), ('credit', '=', 3.00)])[0]
    assert move_line_obj.browse(oerp.cr, 1, move4).credit == 3.00

    move5 = move_line_obj.search(oerp.cr, 1, [('move_id', '=', invoice.move_id.id), ('credit', '=', 2.00)])[0]
    assert move_line_obj.browse(oerp.cr, 1, move5).credit == 2.00

    move6 = move_line_obj.search(oerp.cr, 1, [('move_id', '=', invoice.move_id.id), ('credit', '=', 0.65)])[0]
    assert move_line_obj.browse(oerp.cr, 1, move6).credit == 0.65

    move7 = move_line_obj.search(oerp.cr, 1, [('move_id', '=', invoice.move_id.id), ('credit', '=', 2.88)])[0]
    assert move_line_obj.browse(oerp.cr, 1, move7).credit == 2.88

    move8 = move_line_obj.search(oerp.cr, 1, [('move_id', '=', invoice.move_id.id), ('credit', '=', 3.30)])[0]
    assert move_line_obj.browse(oerp.cr, 1, move8).credit == 3.30

    move9 = move_line_obj.search(oerp.cr, 1, [('move_id', '=', invoice.move_id.id), ('credit', '=', 86.67)])[0]
    assert move_line_obj.browse(oerp.cr, 1, move9).credit == 86.67

    rec_ids = invoice._get_receivable_lines(inv_id, False, None)
    assert len(rec_ids) == 1

    rec_line = oerp.pool.get('account.move.line').browse(oerp.cr, 1, rec_ids[invoice.id])[0]
    assert rec_line.debit == 98.5
