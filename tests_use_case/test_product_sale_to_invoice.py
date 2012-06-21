from workflow.wkf_service import workflow_service


def test_product_sale_to_invoice_nfe(oerp):
    """ create an invoice from a product sale order with NFE fiscal
    document.
        taxes in this invoice are:
            COFINS 0,74% Incluso
            PIS 0,25% Incluso
            CSLL 0,21% Incluso
            INSS 1,80% Incluso
            ICMS 1,25% Incluso
            IPI 5,00% Adicionado
    Confs required:
         Brazilian chart of accounts generated;
         Fiscal document serie for NFE fiscal document;
         CNAE da empresa.

    """

    #create empty fiscal classification for the product
    prod_fc_obj = oerp.pool.get('account.product.fiscal.classification')
    prod_fc_id = prod_fc_obj.create(oerp.cr, 1, {
        'name': 'isento',
        'description': 'isento'
        })

    assert prod_fc_obj.browse(oerp.cr, 1, [prod_fc_id])[0].id == prod_fc_id
    # create product template - utiliza plano de contas brasileiro
    prod_obj = oerp.pool.get('product.product')
    prod_tpl_obj = oerp.pool.get('product.template')

    prod_tpl_id = prod_tpl_obj.create(oerp.cr, 1, {
        'supply_method': 'buy',
        'standard_price': 1.00,
        'list_price': 100.00,
        'mes_type': 'fixed',
        'name': 'pytest product',
        'property_account_income': 1193,
        'property_account_expense': 669,
        'property_fiscal_classification': prod_fc_id,
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
        'default_code': 'pytest_123'
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
        'domain': 'cofins'
        })

    # create PIS tax code with tax_include
    tax_code_pis_id = tax_code_obj.create(oerp.cr, 1, {
        'name': 'PIS_test',
        'company_id': 1,
        'sign': 1,
        'tax_discount': True,
        'tax_include': True,
        'notprintable': True,
        'domain': 'pis'
        })

    assert tax_code_obj.browse(oerp.cr, 1, [tax_code_cofins_id])[0].id == tax_code_cofins_id

    # create CSLL tax code with tax_include
    tax_code_csll_id = tax_code_obj.create(oerp.cr, 1, {
        'name': 'CSLL_test',
        'company_id': 1,
        'sign': 1,
        'tax_discount': True,
        'tax_include': True,
        'notprintable': True,
        'domain': 'csll'
        })

    assert tax_code_obj.browse(oerp.cr, 1, [tax_code_csll_id])[0].id == tax_code_csll_id

    # create INSS tax code with tax_include
    tax_code_inss_id = tax_code_obj.create(oerp.cr, 1, {
        'name': 'INSS_test',
        'company_id': 1,
        'sign': 1,
        'tax_discount': True,
        'tax_include': True,
        'notprintable': True,
        'domain': 'inss'
        })

    assert tax_code_obj.browse(oerp.cr, 1, [tax_code_inss_id])[0].id == tax_code_inss_id

    # create ICMS tax code with tax_include
    tax_code_icms_id = tax_code_obj.create(oerp.cr, 1, {
        'name': 'ICMS_test',
        'company_id': 1,
        'sign': 1,
        'tax_discount': True,
        'tax_include': True,
        'notprintable': False,
        'domain': 'icms'
        })

    assert tax_code_obj.browse(oerp.cr, 1, [tax_code_icms_id])[0].id == tax_code_icms_id

    # create IPI tax code with tax_include
    tax_code_ipi_id = tax_code_obj.create(oerp.cr, 1, {
        'name': 'IPI_test',
        'company_id': 1,
        'sign': 1,
        'tax_discount': True,
        'tax_include': False,
        'notprintable': False,
        'domain': 'ipi'
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
        'domain': 'csll',
        })

    assert tax_obj.browse(oerp.cr, 1, [tax_csll_id])[0].id == tax_csll_id
    sale_order_taxes.append(tax_csll_id)

    # create COFINS 0,74% tax with type tax_include
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
        'domain': 'cofins',
        })

    assert tax_obj.browse(oerp.cr, 1, [tax_cofins_id])[0].id == tax_cofins_id
    sale_order_taxes.append(tax_cofins_id)

    # create PIS 0,25% tax with type tax_include
    tax_pis_id = tax_obj.create(oerp.cr, 1, {
        'sequence': '1',
        'type_tax_use': 'all',
        'applicable_type': 'true',
        'company_id': 1,
        'name': 'PIS 0,25% Recolhe_test',
        'amount': 0.0025,
        'type': 'percent',
        'tax_code_id': tax_code_pis_id,
        'base_reduction': 0.0000,
        'amount_mva': 0.0000,
        'price_include': False,
        'tax_discount': True,
        'tax_add': False,
        'tax_include': True,
        'tax_retain': False,
        'domain': 'pis',
        })

    assert tax_obj.browse(oerp.cr, 1, [tax_pis_id])[0].id == tax_pis_id
    sale_order_taxes.append(tax_pis_id)

    # create INSS 1,80% tax with type tax_include
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
        'domain': 'inss',
        })

    assert tax_obj.browse(oerp.cr, 1, [tax_inss_id])[0].id == tax_inss_id
    sale_order_taxes.append(tax_inss_id)

    # create ICMS 1,25% tax with type tax_include
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
        'domain': 'icms',
        })

    assert tax_obj.browse(oerp.cr, 1, [tax_icms_id])[0].id == tax_icms_id
    sale_order_taxes.append(tax_icms_id)

    # create IPI 5% tax with type tax_include
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
        'domain': 'ipi',
        })

    assert tax_obj.browse(oerp.cr, 1, [tax_ipi_id])[0].id == tax_ipi_id
    sale_order_taxes.append(tax_ipi_id)

    #create CSTs
    cst_obj = oerp.pool.get('l10n_br_account.cst')
    cst_icms_id = cst_obj.create(oerp.cr, 1, {
        'name': 'isento',
        'code': 40,
        'tax_code_id': tax_code_icms_id
        })
    assert cst_obj.browse(oerp.cr, 1, [cst_icms_id])[0].id == cst_icms_id
    
    cst_cofins_id = cst_obj.create(oerp.cr, 1, {
        'name': 'isento',
        'code': 07,
        'tax_code_id': tax_code_cofins_id
        })
    assert cst_obj.browse(oerp.cr, 1, [cst_cofins_id])[0].id == cst_cofins_id
    
    cst_ipi_id = cst_obj.create(oerp.cr, 1, {
        'name': 'isento',
        'code': 02,
        'tax_code_id': tax_code_ipi_id
        })
    assert cst_obj.browse(oerp.cr, 1, [cst_ipi_id])[0].id == cst_ipi_id
    
    cst_pis_id = cst_obj.create(oerp.cr, 1, {
        'name': 'isento',
        'code': 07,
        'tax_code_id': tax_code_pis_id
        })
    assert cst_obj.browse(oerp.cr, 1, [cst_pis_id])[0].id == cst_pis_id

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

    # create product fiscal operation category
    cfop_obj = oerp.pool.get('l10n_br_account.cfop')
    cfop_id = cfop_obj.search(oerp.cr, 1, [])[0]
    fiscal_doc_obj = oerp.pool.get('l10n_br_account.fiscal.document')
    fiscal_doc_id = fiscal_doc_obj.search(oerp.cr, 1, [('nfe', '=', True)])[0]

    fopc_obj = oerp.pool.get('l10n_br_account.fiscal.operation.category')
    fopc_id = fopc_obj.create(oerp.cr, 1, {
        'code': 'pytest_produtos',
        'name': 'pytest_produtos',
        'type': 'output',
        'use_sale': True,
        'use_invoice': True,
        'fiscal_type': 'product'
        })

    assert fopc_obj.browse(oerp.cr, 1, [fopc_id])[0].id == fopc_id

    oerp.cr.execute('insert into l10n_br_account_fiscal_operation_category_rel (fiscal_operation_category_id,journal_id) values (%s, %s)' % (fopc_id, acc_journal_id))

    # create product fiscal operation
    fop_obj = oerp.pool.get('l10n_br_account.fiscal.operation')

    fop_id = fop_obj.create(oerp.cr, 1, {
        'code': 'pytest_produto01',
        'name': 'pytest_produto01',
        'type': 'output',
        'fiscal_operation_category_id': fopc_id,
        'cfop_id': cfop_id,
        'fiscal_document_id': fiscal_doc_id,
        'use_sale': True,
        'use_invoice': True,
        'fiscal_type': 'product'
        })

    assert fop_obj.browse(oerp.cr, 1, [fop_id])[0].id == fop_id

    fop_line_obj = oerp.pool.get('l10n_br_account.fiscal.operation.line')

    fop_lines = []

    fopl1 = {'company_id': 1,
            'fiscal_classification_id': prod_fc_id,
            'tax_code_id': tax_code_icms_id,
            'cst_id': cst_icms_id,
            'fiscal_operation_id': fop_id
            }

    fopl2 = {'company_id': 1,
            'fiscal_classification_id': prod_fc_id,
            'tax_code_id': tax_code_cofins_id,
            'cst_id': cst_cofins_id,
            'fiscal_operation_id': fop_id
            }

    fopl3 = {'company_id': 1,
            'fiscal_classification_id': prod_fc_id,
            'tax_code_id': tax_code_ipi_id,
            'cst_id': cst_ipi_id,
            'fiscal_operation_id': fop_id
            }

    fopl4 = {'company_id': 1,
            'fiscal_classification_id': prod_fc_id,
            'tax_code_id': tax_code_pis_id,
            'cst_id': cst_pis_id,
            'fiscal_operation_id': fop_id
            }

    fop_lines.append((0, 0, fopl1))
    fop_lines.append((0, 0, fopl2))
    fop_lines.append((0, 0, fopl3))
    fop_lines.append((0, 0, fopl4))

    fop_obj.write(oerp.cr, 1, fop_id, {
        'fiscal_operation_line': fop_lines
        })

    # update company data
    partner_obj = oerp.pool.get('res.partner')
    partner_address_obj = oerp.pool.get('res.partner.address')
    country_obj = oerp.pool.get('res.country')
    state_obj = oerp.pool.get('res.country.state')

    country_id = country_obj.search(oerp.cr, 1, [('code', '=', 'BR')])[0]
    state_id = state_obj.search(oerp.cr, 1, [('code', '=', 'RS'),('country_id', '=', country_id)])[0]

    partner_obj.write(oerp.cr, 1, 1, {
        'name': 'emp teste',
        'tipo_pessoa': 'J',
        'legal_name': 'emp teste',
        'cnpj_cpf': '10.965.392/0001-87',
        'inscr_est': '1111',
        'partner_fiscal_type_id': 1
        })

    partner_address_obj.write(oerp.cr, 1, 1, {
        'phone': '5130850096',
        'street': 'av abc',
        'active': True,
        'partner_id': 1,
        'city': 'poa',
        'name': 'Vinicius',
        'country_id': country_id,
        'type': 'default',
        'email': 'proge@proge.com.br',
        'state_id': state_id,
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
        'country_id': country_id,
        'type': 'default',
        'email': 'proge@proge.com.br',
        'state_id': state_id,
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
            'price_unit': prod.price_get('list_price')[prod.id],
            'fiscal_operation_category_id': fopc_id,
            'fiscal_operation_id': fop_id
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
        'fiscal_operation_id': fop_id,
        'fiscal_classification_id': prod_fc_id
        #'fiscal_position': 1
        })

    assert sale_order_obj.browse(oerp.cr, 1, [order_id])[0].id == order_id

    sol_id = sale_order_line_obj.search(oerp.cr, 1, [('order_id', '=', order_id)])[0]
    
    assert sale_order_line_obj.browse(oerp.cr, 1, [sol_id])[0].fiscal_operation_id.id == fop_id

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
    assert invoice.amount_total == 105.0
    assert invoice.amount_untaxed == 100.0
    assert invoice.amount_tax == 5.00
    #assert invoice.cfop_id.id == cfop_id
    assert invoice.fiscal_operation_category_id.id == fopc_id
    assert invoice.fiscal_operation_id.id == fop_id

    #confirm invoice
    wf_service.trg_validate(1, 'account.invoice', inv_id, 'invoice_validate', oerp.cr)

    # reload invoice to get new fields created by the action on the workflow
    invoice = inv_obj.browse(oerp.cr, 1, [inv_id])[0]

    move_line_obj = oerp.pool.get('account.move.line')
    move_lines = move_line_obj.search(oerp.cr, 1, [('move_id', '=', invoice.move_id.id)])
    assert len(move_lines) == 8

    move1 = move_line_obj.search(oerp.cr, 1, [('move_id', '=', invoice.move_id.id), ('debit', '=', 105)])[0]
    assert move_line_obj.browse(oerp.cr, 1, move1).debit == 105

    move2 = move_line_obj.search(oerp.cr, 1, [('move_id', '=', invoice.move_id.id), ('credit', '=', 0.21)])[0]
    assert move_line_obj.browse(oerp.cr, 1, move2).credit == 0.21

    move3 = move_line_obj.search(oerp.cr, 1, [('move_id', '=', invoice.move_id.id), ('credit', '=', 0.74)])[0]
    assert move_line_obj.browse(oerp.cr, 1, move3).credit == 0.74

    move4 = move_line_obj.search(oerp.cr, 1, [('move_id', '=', invoice.move_id.id), ('credit', '=', 0.25)])[0]
    assert move_line_obj.browse(oerp.cr, 1, move4).credit == 0.25

    move5 = move_line_obj.search(oerp.cr, 1, [('move_id', '=', invoice.move_id.id), ('credit', '=', 1.80)])[0]
    assert move_line_obj.browse(oerp.cr, 1, move5).credit == 1.80

    move6 = move_line_obj.search(oerp.cr, 1, [('move_id', '=', invoice.move_id.id), ('credit', '=', 1.25)])[0]
    assert move_line_obj.browse(oerp.cr, 1, move6).credit == 1.25

    move7 = move_line_obj.search(oerp.cr, 1, [('move_id', '=', invoice.move_id.id), ('credit', '=', 5.00)])[0]
    assert move_line_obj.browse(oerp.cr, 1, move7).credit == 5

    move8 = move_line_obj.search(oerp.cr, 1, [('move_id', '=', invoice.move_id.id), ('credit', '=', 95.75)])[0]
    assert move_line_obj.browse(oerp.cr, 1, move8).credit == 95.75

    rec_ids = invoice._get_receivable_lines(inv_id, False, None)
    assert len(rec_ids) == 1

    rec_line = oerp.pool.get('account.move.line').browse(oerp.cr, 1, rec_ids[invoice.id])[0]
    assert rec_line.debit == 105
