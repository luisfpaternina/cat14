odoo.define('base_bim_2.FormRenderer', function (require) {
    "use strict";

    var FormRenderer = require('web.FormRenderer');

    FormRenderer.include({
        _renderTabHeader: function (page, page_id) {
            var $li = this._super.apply(this, arguments);
            if (this.state.model === 'bim.budget') {
                if (page.attrs.name === 'bim_budget_setting') {
                    $li.find('a').html('<i class="fa fa-fw fa-cog"/>')
                } else if (page.attrs.name === 'bim_budget_tools') {
                    $li.find('a').html('<i class="fa fa-fw fa-wrench"/>')
                }
            }
            return $li;
        },
        _renderStatButton: function (node) {
            var $button = this._super.apply(this, arguments);
            if (this.state.model === 'bim.budget') {
                if (node.attrs.name === 'action_view_chapter_certifications') {
                    $button.find('i').addClass('text-success');
                } else if (node.attrs.name === 'action_view_certifications') {
                    $button.find('i').addClass('text-warning');
                }
            }
            return $button;
        },
    });
});
