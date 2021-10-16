import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo11-addons-oca-connector-infor",
    description="Meta package for oca-connector-infor Odoo addons",
    version=version,
    install_requires=[
        'odoo11-addon-connector_infor',
        'odoo11-addon-connector_infor_account_move',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
        'Framework :: Odoo :: 11.0',
    ]
)
