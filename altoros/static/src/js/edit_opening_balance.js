odoo.define('altoros.edit_opening_balance', function (require) {
    "use strict";

    let ListController = require('web.ListController');

    ListController.include({

    /**
     * This function creates button and calls _actionEditOpeningBalance function.
     */

        renderButtons: function ($node) {
            this._super.apply(this, arguments);
            if (this.hasButtons){
                this.$buttons.find('.edit_opening_balance').on('click', this._actionEditOpeningBalance.bind(this));
            }

        },


    /**
     * This function calls edit.opening.balance wizard.
     */

        _actionEditOpeningBalance: function (event) {
            event.stopPropagation();
            let self = this;
            return this.do_action({
                    name: 'Edit opening balance',
                    type: 'ir.actions.act_window',
                    res_model : 'edit.opening.balance',
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
