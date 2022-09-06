odoo.define('mu_web_notification_base.channel', function (require) {
"use strict";

var WebClient = require('web.WebClient');
var base_bus = require('bus.Longpolling');
var session = require('web.session');
require('bus.BusService');

WebClient.include({
    init: function(parent, client_options){
    	this._super.apply(this, arguments);
        this.bus_channels = [];
        this.bus_events = [];
    },
    show_application: function() {
    	var channel = "notify";
        this.bus_declare_channel(channel, this.notify);
        var res = this._super();
        this.call(
                'bus_service', 'on', 'notification',
                this, this.bus_notification);
        this.call('bus_service', 'startPolling');
        return res;
    },
    destroy: function() {
        var self = this;
        $.each(this.bus_channels, function(index, channel) {
        	this.call('bus_service', 'deleteChannel', channel);
        	this.bus_channels.splice(index, 1);
        });
        this._super.apply(this, arguments);
    },
    bus_declare_channel: function(channel, method) {
        if($.inArray(channel, this.bus_channels) === -1) {
        	this.call('bus_service', 'addChannel', channel);
            this.bus_channels.push(channel);
        }
    },
    bus_notification: function(notifications) {
        var self = this;
        $.each(notifications, function(index, notification) {
            var channel = notification[0];
            var message = notification[1];
            if($.inArray(channel, self.bus_channels) !== -1) {
            	self.call(
                        'notification', 'notify', {
                            type: message.type,
                            title: message.title,
                            message: message.message,
                            sticky: message.sticky,
                            className: message.className,
                        }
                    );
            	return self.call('bus_service', '_beep');
            }
        });
    },
});
    
});
