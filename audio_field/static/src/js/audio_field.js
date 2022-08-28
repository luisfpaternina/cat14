/*
# Copyright 2017-2020,2022 Oleksandr Komarov (https://modool.pro)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
*/

odoo.define('web.audio_field', function (require) {
"use strict";

// TODO >>> const field_registry = require('web.field_registry_owl');
var QWeb = require('web.core').qweb;
var fields = require('web.basic_fields');
var field_registry = require('web.field_registry');

var AudioPlayer = require('audio_field/static/src/components/audio_player/audio_player.js');
const { ComponentWrapper, WidgetAdapterMixin } = require('web.OwlCompatibility');

var AudioField = fields.FieldChar.extend(WidgetAdapterMixin, {

    get_audio_player_data() {
        var props = {
            source: this.value,
        };
        if ('controls' in this.nodeOptions) {
            props['controls'] = this.nodeOptions.controls;
        };
        if ('width' in this.nodeOptions) {
            props['width'] = parseInt(this.nodeOptions.width);
        };
        if ('height' in this.nodeOptions) {
            props['height'] = parseInt(this.nodeOptions.height);
        };
        if ('preload' in this.nodeOptions) {
            props['preload'] = this.nodeOptions.preload;
        };
        if ('add_styles' in this.nodeOptions) {
            props['style'] = this.nodeOptions.add_styles;
        };
        if ('class' in this.nodeOptions) {
            props['class'] = this.nodeOptions.class;
        };
        return props;
    },
    update() {
        if (this.component) {
           this.component.update(this.get_audio_player_data());
        };
    },
    // This func is fix error when click on player
    _onInput: function () {
        if (this.component) {
            return;
        } else {
            return this._super.apply(this, arguments);
        }
    },
    // This func is fix error when click on player
    _getValue: function () {
        if (this.component) {
            return;
        } else {
            return this._super.apply(this, arguments);
        };
    },
    _renderReadonly: function () {
        this._super.apply(this, arguments);
        if (this.value) {
            this.component = new ComponentWrapper(this, AudioPlayer, this.get_audio_player_data());
            this.$el.empty();
            this.component.mount(this.el);
        }
    },
    _render: function () {
        if (this.getParent().mode === "edit" &&
            !this.nodeOptions.show_on_edit_mode) {
            return this._renderEdit();
        } else {
            return this._renderReadonly();
        }
    },
});

field_registry.add('audio_field', AudioField);

return AudioField;

});
