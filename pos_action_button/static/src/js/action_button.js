odoo.define('pos_action_button.ActionButton', function (require) {
"use strict";

//require pos screens
var pos_screens = require('point_of_sale.screens')

// Crear boton y heredar de ActionButtonWidget
var DashboardButton = pos_screens.ActionButtonWidget.extend({
    template: 'DashBoardButton',
    button_click: async function(){
        await selectClient()
        alert("Button clicked")
    },
});

//definir acción del boton
pos_screens.define_action_button({
    'name': 'Dashboard lf',
    'widget': DashboardButton,
    'condition': function(){return this.pos;},
});

});
