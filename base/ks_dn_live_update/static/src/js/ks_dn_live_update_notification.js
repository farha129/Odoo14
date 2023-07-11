odoo.define('ks_dn_live_update.ks_dn_live_update_notification', function(require) {
    "use strict";

    var KsDashboardNinja = require('ks_dashboard_ninja.ks_dashboard');



    KsDashboardNinja.include({
        start: function() {
            var self = this;
            return this._super()
                .then(function() {
                    var dashboards_live = self.ks_dashboard_data['ks_auto_update_type'];
                    if (dashboards_live == 'ks_live_update') {
                        self.call('bus_service', 'onNotification', self, function(notifications) {
                            _.each(notifications, (function(notification) {
                                if (notification[1].hasOwnProperty('type') && notification['1'].type === "ks_dashboard_ninja.notification" && self.ks_mode === 'active') {
                                    var item_to_update = Object.keys(self.ks_dashboard_data['ks_item_data']).filter((x) => self.ks_dashboard_data['ks_item_data'][x].ks_model_name === notification[1].model);

                                    var defs = [];
                                    for (var i = 0; i < item_to_update.length; i++) {
                                        defs.push(self.ksFetchUpdateItem(item_to_update[i]));
                                    }
                                    Promise.all(defs).then(function () {
                                        if (self.ks_dashboard_data['ks_show_live_pop_up'] == true) {
                                            if (item_to_update.length > 0) {
                                                var msg = "" + (item_to_update).length + " Dashboard item(s) has been updated."
                                                self.call('notification', 'notify', {
                                                    message: msg,
                                                    type: 'info',
                                                });
                                            }
                                        }
                                    })
                                }
                            }).bind(this));
                        });
                    }
                });
            }
        })

    return KsDashboardNinja

})