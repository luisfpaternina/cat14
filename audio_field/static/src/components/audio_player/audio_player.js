/* ========================================================================
 * Copyright © 2022 Oleksandr Komarov, Modool (https://modool.pro)
 * License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
 * ======================================================================== */
odoo.define('audio_field/static/src/components/audio_player/audio_player.js', function (require) {
'use strict';

const { Component } = owl;

class AudioPlayer extends Component {

    get audio_attributes() {
        var attrs = {};
        if (this.props.class) {
            attrs['class'] = this.props.class;
        };
        if (this.props.controls) {
            attrs['controls'] = this.props.controls;
        };
        if (this.props.width) {
            attrs['width'] = this.props.width;
        };
        if (this.props.height) {
            attrs['height'] = this.props.height;
        };
        if (this.props.preload) {
            attrs['preload'] = this.props.preload;
        };
        if (this.props.style) {
            attrs['style'] = this.props.style;
        };
        return attrs;
    }
}

Object.assign(AudioPlayer, {
    defaultProps: {
        controls: true,
    },
    props: {
        source: [String, Boolean],
        class: {
            type: String,
            optional: 1,
        },
        controls: {
            type: Boolean,
            optional: 1,
        },
        width: {
            type: Number,
            optional: 1,
        },
        height: {
            type: Number,
            optional: 1,
        },
        preload: {
            type: String,
            optional: 1,
            validate: prop => ['metadata', 'auto', 'none'].includes(prop),
        },
        style: {
            type: String,
            optional: 1,
        },
    },
    template: 'audio_field.AudioPlayer',
});

return AudioPlayer;

});
