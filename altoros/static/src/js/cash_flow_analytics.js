odoo.define('altoros.cash_flow_analytics', function (require) {
    "use strict";

    let ListController = require('web.ListController');

    ListController.include({

    /**
     * This function creates button and calls _actionCashFlowGenerate function.
     */

        renderButtons: function ($node) {
            this._super.apply(this, arguments);
            if (this.hasButtons){
                this.$buttons.find('.cash_flow_analytics').on('click', this._actionCashFlowGenerate.bind(this));
            }

        },


    /**
     * This function calls generate.cash.flow.analytics wizard.
     */

        _actionCashFlowGenerate: function (event) {
            event.stopPropagation();
            let self = this;
            return this.do_action({
                    name: 'Generate cash flow analitics',
                    type: 'ir.actions.act_window',
                    res_model : 'generate.cash.flow.analytics',
                    target: 'new',
                    views: [[false, 'form']],
                 },
               {
                   on_close:()=>{
                       self.trigger_up('reload')}
            })
        },
    });
});
