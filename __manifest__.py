# -*- coding: utf-8 -*-
{
    'name': 'Usl Field Service',
    'version': '2.0.0',
    'summary': 'Usl Field Service',
    'sequence': -100,
    'description': """Usl Field Service""",
    'category': 'Usl Field Service',
    'author': 'Unisoft Software Ltd',
    'maintainer': 'Unisoft Software Ltd',
    'website': 'https://uslbd.com/',
    'license': 'AGPL-3',
    'depends': ['mail', 'stock', 'product', 'gts_branch_management', 'gts_financial_pdf_report'],
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'data/data.xml',
        'views/menu.xml',

        'views/field_service_view.xml',
        'views/field_service_data_view.xml',
        'views/service_type_view.xml',
        'views/warranty_void_reason_view.xml',
        'views/service_order_transfer_view.xml',
        'views/assign_engineer_details.xml',
        'views/diagnosis_repair.xml',
        'views/assign_engineer.xml',
        'views/template.xml',
        ''
        'views/engineer_observation.xml',
        'views/symptoms_type_view.xml',
        'views/field_service_department_view.xml',
        'views/field_service_priority_level_view.xml',
        'views/communication_media_view.xml',
        'views/warranty_status_view.xml',
        'views/advance_item_requisition_warranty_inherit_view.xml',
        'views/advance_item_requisition_non_warranty_inherit_view.xml',
        'views/service_order_receive_view.xml',
        'views/css_loader.xml',
        'views/service_order_receive.xml',
        'views/item_requisition_warranty_view_inherit.xml',
        'views/item_requisition_non_warranty_view_inherit.xml',
        'views/reason_type_view.xml',
        'views/operation.xml',
        'views/operation_receive.xml',
        'views/transfer_order_receive.xml',
        'views/transfer_order_receive_operation.xml'

    ],
    'assets': {
        'web.assets_backend': [
            '/usl_service_erp/static/src/css/style.css',
        ]},
    'demo': [],
    'qweb': [],
    'images': ['static/description/banner.gif'],
    'installable': True,
    'application': True,
    'auto_install': False,
}
