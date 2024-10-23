/* Copyright (c) 2015-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>) */
/* See LICENSE file for full copyright and licensing details. */
/* License URL : <https://store.webkul.com/license.html/> */
odoo.define('odoo_email_cc_bcc/static/src/js/message.js', function (require) {
    'use strict';

    const {
        registerClassPatchModel,
        registerFieldPatchModel,
    } = require('@mail/model/model_core');
    const { attr } = require('@mail/model/model_field');

    registerFieldPatchModel('mail.message', 'odoo_email_cc_bcc/static/src/js/message.js', {
        cc_partners: attr({
            default: false,
        }),
        bcc_partners: attr({
            default: false,
        }),
        email_cc: attr({
            default: false,
        }),
        email_bcc: attr({
            default: false,
        }),
    });
    registerClassPatchModel('mail.message', 'odoo_email_cc_bcc/static/src/js/message.js', {
        //----------------------------------------------------------------------
        // Public
        //----------------------------------------------------------------------
    
        /**
         * @override
         */
        convertData(data) {
            const data2 = this._super(data);
            if ('cc_partners' in data && data.cc_partners) {
                if (!data2.cc_partners) {
                    data2.cc_partners = data.cc_partners;
                }                
            }
            if ('bcc_partners' in data && data.bcc_partners) {
                if (!data2.bcc_partners) {
                    data2.bcc_partners = data.bcc_partners;
                }
            }
            if ('email_cc' in data && data.email_cc) {
                if (!data2.email_cc) {
                    data2.email_cc = data.email_cc
                }
            }
            if ('email_bcc' in data && data.email_bcc) {
                if (!data2.email_bcc) {
                    data2.email_bcc = data.email_bcc
                }
            }
            console.log(data)
            return data2;
        },
    });
});

/* @odoo-module */

import { Message } from "@mail/core/common/message";

import { patch } from "@web/core/utils/patch";

patch(Message, {
    _insert(data) {
        const message = super._insert(...arguments);
        if ('cc_partners' in data && data.cc_partners) {
            if (!message.cc_partners) {
                message.cc_partners = data.cc_partners;
            }                
        }
        if ('bcc_partners' in data && data.bcc_partners) {
            if (!message.bcc_partners) {
                message.bcc_partners = data.bcc_partners;
            }
        }
        if ('email_cc' in data && data.email_cc) {
            if (!message.email_cc) {
                message.email_cc = data.email_cc
            }
        }
        if ('email_bcc' in data && data.email_bcc) {
            if (!message.email_bcc) {
                message.email_bcc = data.email_bcc
            }
        }
        console.log(data)
        return message;
    },
});
