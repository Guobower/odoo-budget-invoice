
# RULE 1
def rule_001():
    discount_percentage = 0.00
    if invoice_id.invoice_date and invoice_id.contract_id:

        year_invoice = invoice_id.year_invoice
        year_invoice = 'Year ' + str(int(year_invoice[-1]) - 1)
        sql = """
        SELECT SUM(certified_invoice_amount)
        FROM budget_invoice_invoice
        WHERE state NOT IN ('draft', 'on hold', 'rejected', 'amount hold')
          AND contract_id = %(contract_id)s
          AND year_invoice = '%(year_invoice)s'
        GROUP BY contract_id, year_invoice
        """ % {
            'contract_id': contract_id.id,
            'year_invoice': year_invoice,
        }

        cr.execute(sql)
        res = cr.dictfetchone()
        total_certified_amount_previous_month = 0.0 if res is None else res['sum']
        for discount in contract_id.discount_ids.search([('contract_id', '=', contract_id.id)],
                                                        order='min_threshold desc'):
            min_threshold = discount.min_threshold
            max_threshold = discount.max_threshold
            if min_threshold <= total_certified_amount_previous_month and max_threshold == -1:
                discount_percentage = discount.discount_percentage
                break

            elif min_threshold <= total_certified_amount_previous_month <= max_threshold:
                discount_percentage = discount.discount_percentage
                break
