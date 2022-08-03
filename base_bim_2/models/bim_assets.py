from odoo import api, fields, models, _


class BimAsset(models.Model):
    _name = 'bim.assets'
    _description = 'Assets and Discounts'

    name = fields.Char('Code', default='New')
    desc = fields.Char('Gloss', required=True, translate=True)
    default_value = fields.Float('Default value')

    type = fields.Selection([('M', 'Total Materials'),
                             ('H', 'Total Labor'),
                             ('Q', 'Total Equipment'),
                             ('S', 'Total Sub-Contracts'),
                             ('T', 'Total Direct Costs'),
                             ('N', 'Total Net'),
                             ('O', 'Other')], default='N')

    obs = fields.Text('Observation')
    show_on_report = fields.Boolean('Show in report', default=True,
                                    help="Indicates if you want to show credit / discount in budget report")
    not_billable = fields.Boolean('Not Billable', default=False)

    @api.model_create_multi
    def create(self, vals_list):
        sec_obj = self.env['ir.sequence']
        for vals in vals_list:
            if vals.get('name', 'New') == 'New':
                vals['name'] = sec_obj.next_by_code('bim.assets') or 'New'
        return super().create(vals_list)

    def name_get(self):
        res = super().name_get()
        result = []
        for element in res:
            haberesydesr_id = element[0]
            glosa = self.browse(haberesydesr_id).desc
            name = element[1] and '[%s] %s' % (element[1], glosa) or '%s' % element[1]
            result.append((haberesydesr_id, name))
        return result

    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        records = self.search((args or []) + [('desc', operator, name)])
        if records:
            return records.name_get()
        return super().name_search(name, args, operator, limit)


class BimHaberesydescTemplateLine(models.Model):
    _name = 'bim.assets.template.line'
    _description = 'Assets and Discounts template line'
    _rec_name = 'asset_id'
    _order = 'sequence'


    @api.model
    def default_get(self, default_fields):
        values = super(BimHaberesydescTemplateLine, self).default_get(default_fields)
        values['sequence'] = len(self.template_id.line_ids) + 1
        return values

    sequence = fields.Integer('Sequence')
    template_id = fields.Many2one('bim.assets.template', 'Template', ondelete="restrict")
    asset_id = fields.Many2one('bim.assets', 'Credit or Discount', required=True)
    type = fields.Selection(related='asset_id.type', readonly=True)
    value = fields.Float('Value')
    affect_ids = fields.Many2many(
        string='Affects',
        comodel_name='bim.assets.template.line',
        relation='template_line_assets_afect_rel',
        column1='parent_id',
        column2='child_id',
    )
    main_asset = fields.Boolean(default=False)

    _sql_constraints = [
        ('unique_asset_template_line', 'unique(template_id, asset_id)', 'A Credit or Discount cannot be repeated in the same template')
    ]

    @api.onchange('asset_id')
    def _onchange_assets(self):
        for record in self:
            record.value = record.asset_id and record.asset_id.default_value or 0.0
            record.sequence = len(record.template_id.line_ids)


class BimHaberesydescTemplate(models.Model):
    _name = 'bim.assets.template'
    _description = 'Assets and Discounts Template'

    @api.model
    def _default_lines(self):
        return [(0, 0, {
            'sequence': i,
            'asset_id': self.env.ref('base_bim_2.had0000%d' % i)
        }) for i in range(1, 5)]

    name = fields.Char('Name', required=True)
    desc = fields.Text('Description')
    line_ids = fields.One2many('bim.assets.template.line', 'template_id', string='Lines', required=True, default=_default_lines)
