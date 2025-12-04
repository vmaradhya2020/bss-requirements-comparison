# AT&T BSS Implementation - Legacy System

## Customer: AT&T
**Implementation Version:** 2.8
**Production Date:** 2023-12-01
**Implemented Features:** 12

---

## Core Billing

1. **Real-time Rating System**
   Legacy real-time rating engine for prepaid and postpaid. Handles 50K TPS. Integration with IN platform for service control.

2. **Convergent Invoicing**
   Multi-service billing supporting wireless, DirecTV, and U-verse. Consolidated statement generation with product-specific sections.

3. **Tiered Pricing Platform**
   Usage-based pricing with data buckets, overage charges, and family plan sharing. Legacy rating tables with manual configuration.

4. **Billing Cycle Management**
   Monthly billing automation with 20 different cycle dates. Supports proration and plan changes with next-cycle activation.

## Payments

5. **Payment Gateway**
   Payment processing via Authorize.net and internal ACH. Support for autopay, one-time payments, and payment extensions.

6. **Payment Application**
   Manual and automated payment posting. Basic payment allocation with FIFO rules. Refund processing with finance approval workflow.

7. **Payment Card Storage**
   Tokenized payment storage meeting PCI requirements. Card-on-file management with expiration notifications.

## Account Management

8. **MyAT&T Customer Portal**
   Legacy web portal for bill viewing and payment. Limited mobile app functionality. Batch updates overnight.

9. **Business Account Hierarchy**
    Multi-level corporate accounts with parent billing. Volume discounts and enterprise pricing agreements.

10. **Collections Management**
    Basic dunning with email/SMS notifications. Manual collection agent assignment and promise-to-pay tracking.

## Financial

11. **Revenue Recognition**
    Monthly revenue recognition with manual journal entries. Basic GL posting for receivables and revenue.

12. **Sales Tax Calculation**
    Integrated Vertex tax engine. Federal, state, local tax calculation. Exempt account management with certificate validation.
