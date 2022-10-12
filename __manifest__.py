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
    'depends': ['mail', 'product', 'gts_branch_management', 'gts_financial_pdf_report'],
    'data': [
        'security/ir.model.access.csv',
        'data/data.xml',
        'views/menu.xml',
        'views/field_service_view.xml',
        'views/field_service_data_view.xml',
        'views/service_type_view.xml',
        'views/warranty_void_reason_view.xml',
        'views/warranty_view.xml'

    ],
    'demo': [],
    'qweb': [],
    'images': ['static/description/banner.gif'],
    'installable': True,
    'application': True,
    'auto_install': False,
}
