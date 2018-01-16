Ext.require([
    'Ext.grid.*',
    'Ext.data.*',
    'Ext.panel.*',
    'Ext.layout.container.Border'
]);

Ext.onReady(function(){

    /** Define a Model to be used by our data source */
    Ext.define('TimeEntry',{
        extend: 'Ext.data.Model',
        fields: [
            'EntryDate',
            'ClientID',
            'JobID',
            'TaskID',
            'EmployeeID',
            'ClientName',
            'JobName',
            'TaskName',
            'EmployeeName',
            { 
                name: 'Hours',
                type: 'float'
            },{
                name: 'BillingRate',
                type: 'float'
            },{
                name: 'IsBillable',
                type: 'boolean'
            }
        ]
    });

    /** We'll create an ExtJS Store that will provide data to ditto */
    var store = Ext.create('Ext.data.Store', {
        model: 'TimeEntry',
        proxy: {
            type: 'ajax',
            url: '../data/time-data.json',
            reader: {
                type: 'json'
            }
        },
        autoLoad: false
    });

    /** We need to provide IDs and names for the designer to be able to display available data sources */
    var dataSources = [{
        id: "time",
        name: "Time",
        store: store
    }];

    var viewport = Ext.create('Ext.Viewport', {
        layout: {
            type: 'border'
        },
        items: [{
                region: 'north',
                split: true,
                cls: 'description',
                contentEl: 'description'
            },{
                region: 'south',
                xtype: 'tabpanel',
                id: 'reportViews',
                items: [{
                    title: 'Edit Report',
                    xtype: 'reportdesigner',
                    id: 'designer',
                    dataSources: dataSources,
                    listeners: {
                        save: function(sender, reportDef) {
                            Ext.getCmp('viewer').setReport(reportDef);
                        }
                    }
                },{
                    title: 'View Report Output',
                    xtype: 'reportviewer',
                    id: 'viewer',
                    dataSources: dataSources
                }],
                flex: 100
            }
        ]
    });

    // Load the report definition JSON file from the server
    Ext.Ajax.request({
        url: 'report.json',
        success: function(response) {
            var report = Ext.JSON.decode(response.responseText);
            Ext.getCmp('designer').setReport(report);
            Ext.getCmp('viewer').setReport(report);
        }
    });
    
    store.load();
});