odoo.define('web_notify.Notification', function (require) {
    "use strict";

    var Notification = require('web.Notification');

    Notification.include({
        template: "Notification",
        icon_mapping: {
            'success': 'fa-thumbs-up',
            'danger': 'fa-exclamation-triangle',
            'warning': 'fa-exclamation',
            'info': 'fa-info',
            'default': 'fa-lightbulb-o',
        },
        init: function () {
            this._super.apply(this, arguments);
            // Delete default classes
            this.className = this.className.replace(' o_error', '');
            // Add custom icon and custom class
            this.icon = (this.type in this.icon_mapping) ?
                this.icon_mapping[this.type] :
                this.icon_mapping['default'];
            this.className += ' o_' + this.type;
            this.rids = (arguments[1].rids) ? arguments[1].rids : [];
            this.rmodel = arguments[1].rmodel;
            this.events = _.extend(this.events || {}, {
                'click .pop2detail': function() {
                    var self = this;
                    const newAudio = document.createElement("audio");
                    newAudio.id = 'audiotag1';
                    newAudio.src = 'web_notify/static/src/audio/notification.mp3';
                    newAudio.preload = 'auto';
                    newAudio.play();
                    console.log(newAudio)
                    //this._rpc({
                      //      route: '/notify/playsound',
                        //    params: {
                          //      res_model: self.rmodel,
                            //    res_ids: self.rids
                            //},
                        //}).then(function(r) {
                          //  return r;
                        //});


                },
    
                'click .pop2close': function() {
                    this.close();
                },
            });
        },
    });

});
