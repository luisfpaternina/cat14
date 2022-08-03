odoo.define('base_bim_2.attendances', function (require) {
    "use strict";
    var MyAttendances = require('hr_attendance.my_attendances');
    var KioskConfirm = require('hr_attendance.kiosk_confirm');
    var domain_attendance = [];
    domain_attendance.push(['state_id.include_in_attendance','=',true]);

    MyAttendances.include({
        willStart: function () {
            var self = this;
            var def = this._rpc({
                model: 'bim.project',
                method: 'search_read',
                args: [domain_attendance, ['name', 'nombre']],
            }).then(function (projects) {
                self.projects = projects;
            });
            return Promise.all([def, this._super.apply(this, arguments)]);
        },
        update_attendance: function () {
            var self = this;
            var project_id = $('#bim_project').children("option:selected").val();
            if (this.projects.length > 0 && !project_id && this.employee.attendance_state != 'checked_in') {
                alert('Seleccione una obra antes de continuar');
                return;
            }
            this._rpc({
                model: 'hr.employee',
                method: 'attendance_manual',
                args: [[self.employee.id], 'hr_attendance.hr_attendance_action_my_attendances'],
                context: { default_project_id: parseInt(project_id) },
            }).then(function (result) {
                if (result.action) {
                    self.do_action(result.action);
                } else if (result.warning) {
                    self.do_warn(result.warning);
                }
            });
        },
    });

    KioskConfirm.include({
        events: _.extend(KioskConfirm.prototype.events, {}, {
            "click .o_hr_attendance_sign_in_out_icon": _.debounce(function () {
                var self = this;
                var project_id = $('#bim_project').children("option:selected").val();
                if (this.projects.length > 0 && !project_id && this.employee_state != 'checked_in') {
                    alert('Seleccione una obra antes de continuar');
                    return;
                }
                this._rpc({
                    model: 'hr.employee',
                    method: 'attendance_manual',
                    args: [[this.employee_id], this.next_action],
                    context: { default_project_id: parseInt(project_id) },
                }).then(function (result) {
                    if (result.action) {
                        self.do_action(result.action);
                    } else if (result.warning) {
                        self.do_warn(result.warning);
                    }
                });
            }, 200, true),
            'click .o_hr_attendance_pin_pad_button_ok': _.debounce(function() {
                var self = this;
                var project_id = this.$('#bim_project').children("option:selected").val();
                if (this.projects.length > 0 && !project_id && this.employee_state != 'checked_in') {
                    alert('Seleccione una obra antes de continuar');
                    return;
                }
                this.$('.o_hr_attendance_pin_pad_button_ok').attr("disabled", "disabled");
                this._rpc({
                        model: 'hr.employee',
                        method: 'attendance_manual',
                        args: [[this.employee_id], this.next_action, this.$('.o_hr_attendance_PINbox').val()],
                        context: { default_project_id: parseInt(project_id) },
                    })
                    .then(function(result) {
                        if (result.action) {
                            self.do_action(result.action);
                        } else if (result.warning) {
                            self.do_warn(result.warning);
                            self.$('.o_hr_attendance_PINbox').val('');
                            setTimeout( function() { self.$('.o_hr_attendance_pin_pad_button_ok').removeAttr("disabled"); }, 500);
                        }
                    });
            }, 200, true),
        }),
        willStart: function () {
            var self = this;
            var def = this._rpc({
                model: 'bim.project',
                method: 'search_read',
                args: [domain_attendance, ['name', 'nombre']],
            }).then(function (projects) {
                self.projects = projects;
            });
            return Promise.all([def, this._super.apply(this, arguments)]);
        },
    });
});