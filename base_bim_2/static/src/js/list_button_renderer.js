odoo.define('base_bim_2.ListRenderer', function (require) {
    "use strict";
    var ListRenderer = require('web.ListRenderer');
    var HierarchyRenderer = require('hierarchy_view.renderer');

    ListRenderer.include({
        _renderBodyCell: function (record, node, colIndex, options) {
            var $td = this._super.apply(this, arguments);

            if (record.model === 'bim.concepts' && node.children.find(btn => btn.attrs.name === 'do_nature') && (record.data.type === 'chapter')) {
                $td.html('<div class="text-center text-success"><i class="fa fa-th-large"/></div>');
            }
            else if (record.model === 'bim.concepts' && node.children.find(btn => btn.attrs.name === 'do_nature') && record.data.type === 'departure') {
                $td.html('<div class="text-center text-warning"><i class="fa fa-th-list"/></div>');
            }
            else if (record.model === 'bim.concepts' && node.children.find(btn => btn.attrs.name === 'do_nature') && record.data.type === 'labor') {
                $td.html('<div class="text-center text-success"><i class="fa fa-male"/></div>');
            }
            else if (record.model === 'bim.concepts' && node.children.find(btn => btn.attrs.name === 'do_nature') && record.data.type === 'equip') {
                $td.html('<div class="text-center text-danger"><i class="fa fa-gears"/></div>');
            }
            else if (record.model === 'bim.concepts' && node.children.find(btn => btn.attrs.name === 'do_nature') && record.data.type === 'material') {
                $td.html('<div class="text-center text-warning"><i class="fa fa-maxcdn"/></div>');
            }
            else if (record.model === 'bim.concepts' && node.children.find(btn => btn.attrs.name === 'do_nature') && record.data.type === 'aux') {
                $td.html('<div class="text-center"><i class="fa fa-percent"/></div>');
            }
            return $td;
        },
        _renderHeaderCell: function (node) {
            var $th = this._super.apply(this, arguments);
            if (this.state.model === 'bim.budget.stage' && node.attrs.name === 'certification') {
                $th.css('color', 'green');
            } else if (this.state.model === 'bim.budget.stage' && node.attrs.name === 'executed') {
                $th.css('color', 'red');
            } else if (this.state.model === 'bim.budget.stage' && node.attrs.name === 'planning') {
                $th.css('color', 'blue');
            }
            return $th;
        },
    });//['equip','machine','material','aux'].indexOf(record.data.type) !== -1)
    HierarchyRenderer.include({
        _renderBodyCell: function (record, node, colIndex, options) {
            var $td = this._super.apply(this, arguments);

            if (record.model === 'bim.concepts' && node.children.find(btn => btn.attrs.name === 'do_nature') && (record.data.type === 'chapter')) {
                $td.html('<div class="text-center text-success"><i class="fa fa-th-large"/></div>');
            }
            else if (record.model === 'bim.concepts' && node.children.find(btn => btn.attrs.name === 'do_nature') && record.data.type === 'departure') {
                $td.html('<div class="text-center text-warning"><i class="fa fa-th-list"/></div>');
            }
            else if (record.model === 'bim.concepts' && node.children.find(btn => btn.attrs.name === 'do_nature') && record.data.type === 'labor') {
                $td.html('<div class="text-center text-success"><i class="fa fa-male"/></div>');
            }
            else if (record.model === 'bim.concepts' && node.children.find(btn => btn.attrs.name === 'do_nature') && record.data.type === 'equip') {
                $td.html('<div class="text-center text-danger"><i class="fa fa-gears"/></div>');
            }
            else if (record.model === 'bim.concepts' && node.children.find(btn => btn.attrs.name === 'do_nature') && record.data.type === 'material') {
                $td.html('<div class="text-center text-warning"><i class="fa fa-maxcdn"/></div>');
            }
            else if (record.model === 'bim.concepts' && node.children.find(btn => btn.attrs.name === 'do_nature') && record.data.type === 'aux') {
                $td.html('<div class="text-center"><i class="fa fa-percent"/></div>');
            }
            else if (record.model === 'bim.concepts' && (node.attrs.name === 'acs_date_start' || node.attrs.name === 'acs_date_end') && ['chapter', 'departure'].indexOf(record.data.type) < 0) {
                $td.html(null);
            }
            return $td;
        },
    });
});
