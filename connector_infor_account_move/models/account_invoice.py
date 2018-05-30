# Copyright (C) 2018 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from jinja2 import Template
import pytz

from odoo import api, fields, models

body_template = """﻿<?xml version="1.0" encoding="utf-8"?> <ProcessSourceSystemJournalEntry xsi:schemaLocation="http://schema.infor.com/InforOAGIS/2 http://schema.infor.com/2.9.0/InforOAGIS/BODs/Developer/ProcessSourceSystemJournalEntry.xsd" releaseID="9.2" versionID="2.9.0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns="http://schema.infor.com/InforOAGIS/2">
  <ApplicationArea>
    <Sender>
      <LogicalID schemeVersionID="6.02.01.0188">lid://infor.sunsystems.1</LogicalID>
      <ComponentID>SunSystems 6</ComponentID>
      <ConfirmationCode>Always</ConfirmationCode>
      <AuthorizationID />
    </Sender>
    <CreationDateTime>{{CREATE_DATE}}</CreationDateTime>
    <BODID>Infor-nid:Infor:${BUSINESS_UNIT}::{{INVOICE_ID}}:0?SourceSystemJournalEntry&amp;verb=Process</BODID>
  </ApplicationArea>
  <DataArea>
    <Process>
      <TenantID>${TENANT_ID}</TenantID>
      <AccountingEntityID>{{ACCOUNTING_ENTITY_ID}}</AccountingEntityID>
      <ActionCriteria>
        <ActionExpression actionCode="Add" />
      </ActionCriteria>
    </Process>
    <SourceSystemJournalEntry>
      <JournalEntryHeader>
        <JournalID accountingEntity="${BUSINESS_UNIT}" variationID="">{{INVOICE_ID}}</JournalID>
        <DisplayID>{{INVOICE_ID}}</DisplayID>
        <BaseJournalEntryHeader>
          <LedgerID>A</LedgerID>
          <LedgerType>Actual</LedgerType>
          <AccountingJournalReference>
            <ID>{{JOURNAL_CODE}}</ID>
          </AccountingJournalReference>
          <LedgerSetupReference>
            <DocumentID>
              <ID>A</ID>
            </DocumentID>
            <BookInstanceID>A</BookInstanceID>
          </LedgerSetupReference>
          <JournalStatus>
            <Code>Final</Code>
          </JournalStatus>
        </BaseJournalEntryHeader>
      </JournalEntryHeader>
      <JournalEntryLine sequence="${JOURNAL_ENTRY_SEQUENCE}">
      {% for line in JOURNAL_LINES %}
        <Amount currencyID="{{ line.company_id.currency_id.name }}">{{SEC_AMOUNT}}</Amount>
        <FunctionalAmount currencyID="{{COMPANY_CURRENCY}}">{{COMPANY_AMOUNT}}</FunctionalAmount>
        <ReportingCurrencyAmount currencyID="{{CURRENCY}}">0</ReportingCurrencyAmount>
        <GLAccount>
          <GLNominalAccount>{{ line.account_id.code }}</GLNominalAccount>
          <AccountingChartReference>
            <ID>${BUSINESS_UNIT}</ID>
          </AccountingChartReference>
        </GLAccount>
        <DimensionCodes>
          <DimensionCode sequence="1" listID="${CUSTOM_ATTRIBUTE}">${CUSTOM_VALUE}</DimensionCode>
        </DimensionCodes>
        {%- if line.credit > 0 -%}
            <DebitCreditFlag>C</DebitCreditFlag>
        {% else %}
            <DebitCreditFlag>D</DebitCreditFlag>
        {%- endif %}
        <SourceAccountingDate>
          <PeriodID>${FISCAL_PERIOD}</PeriodID>
          <Year>${FISCAL_YEAR}</Year>
          <PostDateTime>{{ line.create_date }}</PostDateTime>
        </SourceAccountingDate>
        <TransactionReferenceText>{{INVOICE_NUMBER}}</TransactionReferenceText>
        <Description languageID="${LANGUAGE}">${DESCRIPTION}</Description>
        <MemoAmount>
          <AmountNumeric />
        </MemoAmount>
        <ExchangeRateDateTime>${TRANSACTION_DATE}</ExchangeRateDateTime>
        <UserArea>
          <Property sequence="1">
            <NameValue name="${CUSTOM_ATTRIBUTE}" type="String" unitCode="EA">${CUSTOM_VALUE}</NameValue>
          </Property>
        </UserArea>
      {% endfor %}
      </JournalEntryLine>
    </SourceSystemJournalEntry>
  </DataArea>
</ProcessSourceSystemJournalEntry>
"""


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'


    @api.multi
    def invoice_validate(self):
        template = Template(body_template)
        today = fields.Datetime.now(pytz.timezone('GMT'))
        for invoice in self:
            # Only applicable for Vendor bills
            if invoice.type == 'in_invoice':
                move = invoice.move_id
                move_lines = move.line_ids.filtered(
                    lambda x: x.credit or x.debit)
                b = template.render(
                    CREATE_DATE=today,
                    INVOICE_ID=invoice.id,
                    INVOICE_NUMBER=invoice.number,
                    ACCOUNTING_ENTITY_ID=move.id,
                    JOURNAL_CODE=move.journal_id.code,
                    SEC_CURRENCY=move.currency_id.name,
                    COMPANY_CURRENCY=move.company_id.currency_id.name,
                    JOURNAL_LINES=move_lines,
                )
        res = super(AccountInvoice, self).invoice_validate()
        return res
